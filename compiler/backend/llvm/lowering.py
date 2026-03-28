from __future__ import annotations

from dataclasses import dataclass, field
import re
from typing import Any

from compiler.ir import (
    BasicBlock as IRBasicBlock,
    Bind as IRBind,
    Branch as IRBranch,
    Declaration as IRDeclaration,
    DirectCall as IRDirectCall,
    EnumType as IREnumType,
    ErrorPropagationPlaceholder as IRErrorPropagationPlaceholder,
    Eval as IREval,
    FieldValue as IRFieldValue,
    Function as IRFunction,
    ImplSurface as IRImplSurface,
    Jump as IRJump,
    Literal as IRLiteral,
    LocalRef as IRLocalRef,
    Module as IRModule,
    Newtype as IRNewtype,
    ParameterRef as IRParameterRef,
    Return as IRReturn,
    StructType as IRStructType,
    SymbolRef as IRSymbolRef,
    TestSurface as IRTestSurface,
    TraitSurface as IRTraitSurface,
    TypeRef as IRTypeRef,
)

from .model import (
    LLVMBasicBlock,
    LLVMBranchTerminator,
    LLVMCallInstruction,
    LLVMDeclaration,
    LLVMFunction,
    LLVMFunctionSignature,
    LLVMGlobalString,
    LLVMJumpTerminator,
    LLVMModule,
    LLVMParameter,
    LLVMReturnTerminator,
    LLVMType,
    LLVMValue,
    LLVM_I1,
    LLVM_I8,
    LLVM_I16,
    LLVM_I32,
    LLVM_I64,
    LLVM_PTR,
    LLVM_VOID,
)

_IDENTIFIER_RE = re.compile(r"[^A-Za-z0-9_$.-]+")
_DECLARATION_LINKAGE = {
    "public": None,
    "internal": "internal",
    "private": "private",
}
_RUNTIME_STRING_CONCAT_SYMBOL = "ax_runtime_string_concat"
_INTEGER_TYPES = {
    "I8": LLVM_I8,
    "I16": LLVM_I16,
    "I32": LLVM_I32,
    "I64": LLVM_I64,
    "Int": LLVM_I64,
}


class BackendError(ValueError):
    def __init__(self, message: str, *, payload: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.payload = payload or {
            "kind": "BackendError",
            "code": "LLVM999",
            "message": message,
            "phase": "backend",
        }


@dataclass(slots=True, frozen=True)
class _KnownFunction:
    symbol_name: str
    signature: LLVMFunctionSignature


@dataclass(slots=True)
class _ModuleContext:
    module: IRModule
    defined_functions: dict[str, _KnownFunction]
    external_functions: dict[str, LLVMFunctionSignature] = field(default_factory=dict)
    global_strings: dict[str, LLVMGlobalString] = field(default_factory=dict)

    def register_external(
        self,
        *,
        symbol_name: str,
        signature: LLVMFunctionSignature,
        callee: IRSymbolRef,
    ) -> None:
        existing = self.external_functions.get(symbol_name)
        if existing is not None and existing != signature:
            raise _backend_error(
                "conflicting external declaration inferred from direct calls",
                code="LLVM010",
                function=callee.name,
                module=callee.module,
                symbol=symbol_name,
            )
        self.external_functions[symbol_name] = signature

    def register_global_string(self, value: str) -> LLVMGlobalString:
        existing = self.global_strings.get(value)
        if existing is not None:
            return existing

        global_string = LLVMGlobalString(
            name=f"str_{len(self.global_strings) + 1}",
            value=value,
            byte_length=len(value.encode("utf-8")) + 1,
        )
        self.global_strings[value] = global_string
        return global_string


@dataclass(slots=True)
class _FunctionContext:
    module: _ModuleContext
    function: IRFunction
    llvm_name: str
    signature: LLVMFunctionSignature
    block_names: dict[str, str]
    parameter_types: dict[str, LLVMType]
    parameter_values: dict[str, LLVMValue]
    binding_map: dict[str, IRBind]
    local_types: dict[str, LLVMType]
    local_cache: dict[str, LLVMValue] = field(default_factory=dict)
    temp_index: int = 0

    def next_temp(self, prefix: str = "tmp") -> str:
        self.temp_index += 1
        return f"{prefix}_{self.temp_index}"


def lower_module(module: IRModule) -> LLVMModule:
    defined_functions: dict[str, _KnownFunction] = {}
    for declaration in module.declarations:
        if not isinstance(declaration, IRFunction):
            continue
        if declaration.name in defined_functions:
            raise _backend_error(
                "duplicate function name in module",
                code="LLVM001",
                module=module.name,
                function=declaration.name,
            )
        signature = _lower_function_signature(
            declaration,
            context=f"function {declaration.name}",
        )
        defined_functions[declaration.name] = _KnownFunction(
            symbol_name=_mangle_global_name(module.name, declaration.name),
            signature=signature,
        )

    context = _ModuleContext(module=module, defined_functions=defined_functions)
    functions: list[LLVMFunction] = []

    for declaration in module.declarations:
        if isinstance(declaration, IRFunction):
            functions.append(lower_function(declaration, module_context=context))
            continue
        if _is_skippable_declaration(declaration):
            continue
        raise _unsupported_declaration_error(declaration)

    declarations = tuple(
        LLVMDeclaration(name=name, signature=signature)
        for name, signature in sorted(context.external_functions.items())
    )
    return LLVMModule(
        name=module.name,
        source_filename=module.source_file or module.name,
        globals=tuple(context.global_strings.values()),
        declarations=declarations,
        functions=tuple(functions),
    )


def lower_function(
    function: IRFunction,
    *,
    module_name: str | None = None,
    known_functions: dict[str, LLVMFunctionSignature] | None = None,
    module_context: _ModuleContext | None = None,
) -> LLVMFunction:
    if module_context is None:
        normalized_module_name = module_name or "<module>"
        signature = _lower_function_signature(
            function,
            context=f"function {function.name}",
        )
        defined_functions = {
            name: _KnownFunction(
                symbol_name=_mangle_global_name(normalized_module_name, name),
                signature=known_signature,
            )
            for name, known_signature in (known_functions or {}).items()
        }
        defined_functions.setdefault(
            function.name,
            _KnownFunction(
                symbol_name=_mangle_global_name(normalized_module_name, function.name),
                signature=signature,
            ),
        )
        module_context = _ModuleContext(
            module=IRModule(name=normalized_module_name, declarations=[function]),
            defined_functions=defined_functions,
        )

    known_function = module_context.defined_functions[function.name]
    block_names = _lower_block_names(function.blocks)
    parameter_values = {
        parameter.name: LLVMValue(
            type=_lower_non_void_type(
                parameter.type,
                context=f"parameter {function.name}.{parameter.name}",
            ),
            text=f"%{_mangle_local_name(parameter.name, prefix='arg')}",
        )
        for parameter in function.parameters
    }
    binding_map, local_types = _collect_bindings(function, module_context, parameter_values)

    context = _FunctionContext(
        module=module_context,
        function=function,
        llvm_name=known_function.symbol_name,
        signature=known_function.signature,
        block_names=block_names,
        parameter_types={name: value.type for name, value in parameter_values.items()},
        parameter_values=parameter_values,
        binding_map=binding_map,
        local_types=local_types,
    )

    parameters = tuple(
        LLVMParameter(
            name=_mangle_local_name(parameter.name, prefix="arg"),
            type=parameter_values[parameter.name].type,
        )
        for parameter in function.parameters
    )
    blocks = tuple(_lower_block(block, context) for block in function.blocks)
    return LLVMFunction(
        name=context.llvm_name,
        signature=context.signature,
        parameters=parameters,
        blocks=blocks,
        linkage=_DECLARATION_LINKAGE[function.visibility],
    )


def _lower_block(block: IRBasicBlock, context: _FunctionContext) -> LLVMBasicBlock:
    instructions: list[LLVMCallInstruction] = []
    for instruction in block.instructions:
        if isinstance(instruction, IRBind):
            _lower_bind_instruction(instruction, context, instructions)
            continue
        if isinstance(instruction, IREval):
            _lower_eval_instruction(instruction, context, instructions)
            continue
        if isinstance(instruction, IRErrorPropagationPlaceholder):
            raise _backend_error(
                "ErrorPropagationPlaceholder must be expanded before LLVM lowering",
                code="LLVM002",
                function=context.function.name,
                block=block.name,
            )
        raise _backend_error(
            "unsupported IR instruction for current LLVM lowering core",
            code="LLVM003",
            function=context.function.name,
            block=block.name,
            instruction=type(instruction).__name__,
        )

    terminator = _lower_terminator(block, context, instructions)
    return LLVMBasicBlock(
        name=context.block_names[block.name],
        instructions=tuple(instructions),
        terminator=terminator,
    )


def _lower_bind_instruction(
    instruction: IRBind,
    context: _FunctionContext,
    instructions: list[LLVMCallInstruction],
) -> None:
    binding_name = instruction.binding.name
    binding_type = context.local_types[binding_name]
    if isinstance(instruction.value, IRDirectCall):
        call_instruction = _build_call_instruction(
            instruction.value,
            context,
            instructions,
            result_name=_mangle_local_name(binding_name, prefix="local"),
            expected_result_type=binding_type,
        )
        instructions.append(call_instruction)
        return

    resolved = _resolve_value(
        instruction.value,
        context,
        instructions,
        expected_type=binding_type,
    )
    if resolved.type != binding_type:
        raise _backend_error(
            "bind value type does not match inferred local type",
            code="LLVM004",
            function=context.function.name,
            binding=binding_name,
            expected=binding_type.spelling,
            actual=resolved.type.spelling,
        )


def _lower_eval_instruction(
    instruction: IREval,
    context: _FunctionContext,
    instructions: list[LLVMCallInstruction],
) -> None:
    if isinstance(instruction.value, IRDirectCall):
        instructions.append(
            _build_call_instruction(
                instruction.value,
                context,
                instructions,
                result_name=None,
                expected_result_type=None,
            )
        )
        return
    _resolve_value(instruction.value, context, instructions, expected_type=None)


def _lower_terminator(
    block: IRBasicBlock,
    context: _FunctionContext,
    instructions: list[LLVMCallInstruction],
) -> LLVMBranchTerminator | LLVMJumpTerminator | LLVMReturnTerminator:
    terminator = block.terminator
    if isinstance(terminator, IRJump):
        return LLVMJumpTerminator(target=context.block_names[terminator.target_block])
    if isinstance(terminator, IRBranch):
        condition = _resolve_value(
            terminator.condition,
            context,
            instructions,
            expected_type=LLVM_I1,
        )
        if condition.type != LLVM_I1:
            raise _backend_error(
                "branch condition must lower to i1",
                code="LLVM005",
                function=context.function.name,
                block=block.name,
                actual=condition.type.spelling,
            )
        return LLVMBranchTerminator(
            condition=condition,
            then_block=context.block_names[terminator.then_block],
            else_block=context.block_names[terminator.else_block],
        )
    if isinstance(terminator, IRReturn):
        if terminator.value is None or _is_unit_literal(terminator.value):
            if context.signature.return_type != LLVM_VOID:
                raise _backend_error(
                    "non-void function cannot return without a value",
                    code="LLVM006",
                    function=context.function.name,
                    expected=context.signature.return_type.spelling,
                )
            return LLVMReturnTerminator()
        if context.signature.return_type == LLVM_VOID:
            raise _backend_error(
                "void function cannot return a value",
                code="LLVM007",
                function=context.function.name,
            )
        value = _resolve_value(
            terminator.value,
            context,
            instructions,
            expected_type=context.signature.return_type,
        )
        if value.type != context.signature.return_type:
            raise _backend_error(
                "return value type does not match function return type",
                code="LLVM008",
                function=context.function.name,
                expected=context.signature.return_type.spelling,
                actual=value.type.spelling,
            )
        return LLVMReturnTerminator(value=value)

    raise _backend_error(
        "unsupported IR terminator for current LLVM lowering core",
        code="LLVM009",
        function=context.function.name,
        block=block.name,
        terminator=type(terminator).__name__,
    )


def _build_call_instruction(
    call: IRDirectCall,
    context: _FunctionContext,
    instructions: list[LLVMCallInstruction],
    *,
    result_name: str | None,
    expected_result_type: LLVMType | None,
) -> LLVMCallInstruction:
    arguments = tuple(
        _resolve_value(argument, context, instructions, expected_type=None)
        for argument in call.arguments
    )
    symbol_name, signature = _resolve_call_target(
        call,
        context,
        arguments,
        expected_result_type=expected_result_type,
    )
    if result_name is not None and signature.return_type == LLVM_VOID:
        raise _backend_error(
            "cannot bind a void direct call result",
            code="LLVM012",
            function=context.function.name,
            callee=call.callee.name,
        )
    return LLVMCallInstruction(
        callee=symbol_name,
        return_type=signature.return_type,
        arguments=arguments,
        result_name=result_name,
    )


def _resolve_value(
    value: Any,
    context: _FunctionContext,
    instructions: list[LLVMCallInstruction],
    *,
    expected_type: LLVMType | None,
) -> LLVMValue:
    if isinstance(value, IRParameterRef):
        return _resolve_parameter_ref(value, context)
    if isinstance(value, IRLocalRef):
        return _resolve_local_ref(value, context)
    if isinstance(value, IRLiteral):
        return _lower_literal(value, context=context, expected_type=expected_type)
    if isinstance(value, IRDirectCall):
        call_instruction = _build_call_instruction(
            value,
            context,
            instructions,
            result_name=context.next_temp(),
            expected_result_type=expected_type,
        )
        instructions.append(call_instruction)
        if call_instruction.return_type == LLVM_VOID:
            raise _backend_error(
                "direct call used as a value must return a non-void type",
                code="LLVM013",
                function=context.function.name,
                callee=value.callee.name,
            )
        return LLVMValue(
            type=call_instruction.return_type,
            text=f"%{call_instruction.result_name}",
        )
    if isinstance(value, (IRFieldValue, IRSymbolRef)):
        raise _unsupported_value_error(value)
    raise _unsupported_value_error(value)


def _resolve_parameter_ref(value: IRParameterRef, context: _FunctionContext) -> LLVMValue:
    try:
        return context.parameter_values[value.name]
    except KeyError as error:
        raise _backend_error(
            "parameter reference does not name a function parameter",
            code="LLVM014",
            function=context.function.name,
            parameter=value.name,
        ) from error


def _resolve_local_ref(value: IRLocalRef, context: _FunctionContext) -> LLVMValue:
    try:
        return _resolve_local_binding(value.name, context, seen=set())
    except KeyError as error:
        raise _backend_error(
            "local reference does not name a bound local",
            code="LLVM015",
            function=context.function.name,
            local=value.name,
        ) from error


def _resolve_local_binding(
    name: str,
    context: _FunctionContext,
    *,
    seen: set[str],
) -> LLVMValue:
    cached = context.local_cache.get(name)
    if cached is not None:
        return cached
    if name in seen:
        raise _backend_error(
            "cyclic local alias is not supported by current LLVM lowering core",
            code="LLVM016",
            function=context.function.name,
            local=name,
        )
    seen.add(name)
    bind = context.binding_map[name]
    binding_type = context.local_types[name]

    if isinstance(bind.value, IRDirectCall):
        lowered = LLVMValue(
            type=binding_type,
            text=f"%{_mangle_local_name(name, prefix='local')}",
        )
    elif isinstance(bind.value, IRLocalRef):
        lowered = _resolve_local_binding(bind.value.name, context, seen=seen)
    elif isinstance(bind.value, IRParameterRef):
        lowered = _resolve_parameter_ref(bind.value, context)
    elif isinstance(bind.value, IRLiteral):
        lowered = _lower_literal(bind.value, context=context, expected_type=binding_type)
    else:
        raise _unsupported_value_error(bind.value)

    if lowered.type != binding_type:
        raise _backend_error(
            "local binding type does not match value type",
            code="LLVM017",
            function=context.function.name,
            local=name,
            expected=binding_type.spelling,
            actual=lowered.type.spelling,
        )
    context.local_cache[name] = lowered
    return lowered


def _collect_bindings(
    function: IRFunction,
    module_context: _ModuleContext,
    parameter_values: dict[str, LLVMValue],
) -> tuple[dict[str, IRBind], dict[str, LLVMType]]:
    binding_map: dict[str, IRBind] = {}
    parameter_types = {name: value.type for name, value in parameter_values.items()}

    for block in function.blocks:
        for instruction in block.instructions:
            if not isinstance(instruction, IRBind):
                continue
            binding = instruction.binding
            if binding.mutable:
                raise _backend_error(
                    "mutable local bindings are not supported by current LLVM lowering core",
                    code="LLVM018",
                    function=function.name,
                    binding=binding.name,
                )
            if binding.name in binding_map:
                raise _backend_error(
                    "local bindings must be unique per function",
                    code="LLVM019",
                    function=function.name,
                    binding=binding.name,
                )
            binding_map[binding.name] = instruction

    cache: dict[str, LLVMType] = {}
    for name, instruction in binding_map.items():
        cache[name] = _infer_binding_type(
            name,
            instruction,
            function=function,
            module_context=module_context,
            parameter_types=parameter_types,
            binding_map=binding_map,
            cache=cache,
            seen=set(),
        )
    return binding_map, cache


def _infer_binding_type(
    name: str,
    instruction: IRBind,
    *,
    function: IRFunction,
    module_context: _ModuleContext,
    parameter_types: dict[str, LLVMType],
    binding_map: dict[str, IRBind],
    cache: dict[str, LLVMType],
    seen: set[str],
) -> LLVMType:
    if name in seen:
        raise _backend_error(
            "cyclic local type inference is not supported",
            code="LLVM020",
            function=function.name,
            binding=name,
        )
    if name in cache:
        return cache[name]

    binding_type_ref = instruction.binding.type
    if binding_type_ref is not None:
        lowered = _lower_non_void_type(
            binding_type_ref,
            context=f"local binding {function.name}.{name}",
        )
        cache[name] = lowered
        return lowered

    seen.add(name)
    value_type = _infer_value_type(
        instruction.value,
        function=function,
        module_context=module_context,
        parameter_types=parameter_types,
        binding_map=binding_map,
        cache=cache,
        seen=seen,
    )
    cache[name] = value_type
    return value_type


def _infer_value_type(
    value: Any,
    *,
    function: IRFunction,
    module_context: _ModuleContext,
    parameter_types: dict[str, LLVMType],
    binding_map: dict[str, IRBind],
    cache: dict[str, LLVMType],
    seen: set[str],
) -> LLVMType:
    if isinstance(value, IRParameterRef):
        try:
            return parameter_types[value.name]
        except KeyError as error:
            raise _backend_error(
                "parameter reference does not name a function parameter",
                code="LLVM021",
                function=function.name,
                parameter=value.name,
            ) from error
    if isinstance(value, IRLocalRef):
        try:
            local_instruction = binding_map[value.name]
        except KeyError as error:
            raise _backend_error(
                "local reference does not name a bound local",
                code="LLVM022",
                function=function.name,
                local=value.name,
            ) from error
        return _infer_binding_type(
            value.name,
            local_instruction,
            function=function,
            module_context=module_context,
            parameter_types=parameter_types,
            binding_map=binding_map,
            cache=cache,
            seen=seen,
        )
    if isinstance(value, IRLiteral):
        lowered = _lower_literal_type(value.type)
        if lowered == LLVM_VOID:
            raise _backend_error(
                "unit literal cannot be bound to a local",
                code="LLVM023",
                function=function.name,
            )
        return lowered
    if isinstance(value, IRDirectCall):
        argument_types = tuple(
            _infer_value_type(
                argument,
                function=function,
                module_context=module_context,
                parameter_types=parameter_types,
                binding_map=binding_map,
                cache=cache,
                seen=set(seen),
            )
            for argument in value.arguments
        )
        return _infer_call_return_type(
            value,
            function=function,
            module_context=module_context,
            argument_types=argument_types,
        )
    raise _unsupported_value_error(value)


def _infer_call_return_type(
    call: IRDirectCall,
    *,
    function: IRFunction,
    module_context: _ModuleContext,
    argument_types: tuple[LLVMType, ...],
) -> LLVMType:
    known = _lookup_known_function(call.callee, module_context)
    if known is not None:
        if len(known.signature.parameter_types) != len(argument_types):
            raise _backend_error(
                "direct call argument count does not match callee signature",
                code="LLVM024",
                function=function.name,
                callee=call.callee.name,
            )
        return known.signature.return_type

    if call.result_type is None:
        raise _backend_error(
            "external direct call requires an explicit result_type when used as a value",
            code="LLVM025",
            function=function.name,
            callee=call.callee.name,
        )
    return _lower_type(call.result_type, context=f"direct call {call.callee.name} result")


def _resolve_call_target(
    call: IRDirectCall,
    context: _FunctionContext,
    arguments: tuple[LLVMValue, ...],
    *,
    expected_result_type: LLVMType | None,
) -> tuple[str, LLVMFunctionSignature]:
    builtin = _resolve_builtin_call(
        call,
        arguments=arguments,
        expected_result_type=expected_result_type,
        function_name=context.function.name,
    )
    if builtin is not None:
        symbol_name, signature = builtin
        context.module.register_external(
            symbol_name=symbol_name,
            signature=signature,
            callee=call.callee,
        )
        _validate_call_signature(
            call,
            signature=signature,
            arguments=arguments,
            expected_result_type=expected_result_type,
            function_name=context.function.name,
        )
        return symbol_name, signature

    known = _lookup_known_function(call.callee, context.module)
    if known is not None:
        _validate_call_signature(
            call,
            signature=known.signature,
            arguments=arguments,
            expected_result_type=expected_result_type,
            function_name=context.function.name,
        )
        return known.symbol_name, known.signature

    if call.result_type is not None:
        return_type = _lower_type(
            call.result_type,
            context=f"direct call {call.callee.name} result",
        )
    elif expected_result_type is not None:
        return_type = expected_result_type
    else:
        raise _backend_error(
            "external direct call requires an explicit result_type",
            code="LLVM041",
            function=context.function.name,
            callee=call.callee.name,
        )

    signature = LLVMFunctionSignature(
        return_type=return_type,
        parameter_types=tuple(argument.type for argument in arguments),
    )
    symbol_name = _mangle_symbol_ref(call.callee)
    context.module.register_external(
        symbol_name=symbol_name,
        signature=signature,
        callee=call.callee,
    )
    _validate_call_signature(
        call,
        signature=signature,
        arguments=arguments,
        expected_result_type=expected_result_type,
        function_name=context.function.name,
    )
    return symbol_name, signature


def _resolve_builtin_call(
    call: IRDirectCall,
    *,
    arguments: tuple[LLVMValue, ...],
    expected_result_type: LLVMType | None,
    function_name: str,
) -> tuple[str, LLVMFunctionSignature] | None:
    if call.callee.module is not None:
        return None

    if call.callee.name == "+":
        if len(arguments) != 2:
            raise _backend_error(
                "string concat runtime lowering requires exactly two arguments",
                code="LLVM043",
                function=function_name,
                callee=call.callee.name,
                actual=len(arguments),
            )
        if any(argument.type != LLVM_PTR for argument in arguments):
            raise _backend_error(
                "current '+' lowering only supports pointer-backed string values",
                code="LLVM044",
                function=function_name,
                callee=call.callee.name,
            )
        signature = LLVMFunctionSignature(
            return_type=LLVM_PTR,
            parameter_types=(LLVM_PTR, LLVM_PTR),
        )
        if call.result_type is not None:
            declared_return_type = _lower_type(
                call.result_type,
                context=f"direct call {call.callee.name} result",
            )
            if declared_return_type != LLVM_PTR:
                raise _backend_error(
                    "string concat runtime symbol must return ptr",
                    code="LLVM045",
                    function=function_name,
                    callee=call.callee.name,
                    actual=declared_return_type.spelling,
                )
        return _RUNTIME_STRING_CONCAT_SYMBOL, signature

    if _is_operator_symbol(call.callee.name):
        raise _backend_error(
            "unsupported builtin operator for current LLVM lowering core",
            code="LLVM046",
            function=function_name,
            callee=call.callee.name,
        )

    return None


def _validate_call_signature(
    call: IRDirectCall,
    *,
    signature: LLVMFunctionSignature,
    arguments: tuple[LLVMValue, ...],
    expected_result_type: LLVMType | None,
    function_name: str,
) -> None:
    if len(signature.parameter_types) != len(arguments):
        raise _backend_error(
            "direct call argument count does not match callee signature",
            code="LLVM026",
            function=function_name,
            callee=call.callee.name,
            expected=len(signature.parameter_types),
            actual=len(arguments),
        )
    for index, (expected_type, argument) in enumerate(zip(signature.parameter_types, arguments)):
        if expected_type != argument.type:
            raise _backend_error(
                "direct call argument type does not match callee signature",
                code="LLVM027",
                function=function_name,
                callee=call.callee.name,
                argument_index=index,
                expected=expected_type.spelling,
                actual=argument.type.spelling,
            )
    if expected_result_type is not None and signature.return_type != expected_result_type:
        raise _backend_error(
            "direct call result type does not match value context",
            code="LLVM028",
            function=function_name,
            callee=call.callee.name,
            expected=expected_result_type.spelling,
            actual=signature.return_type.spelling,
        )


def _lookup_known_function(
    callee: IRSymbolRef,
    module_context: _ModuleContext,
) -> _KnownFunction | None:
    if callee.module is None:
        return module_context.defined_functions.get(callee.name)
    if callee.module == module_context.module.name:
        return module_context.defined_functions.get(callee.name)
    return None


def _lower_function_signature(
    function: IRFunction,
    *,
    context: str,
) -> LLVMFunctionSignature:
    if function.type_parameters:
        raise _backend_error(
            "generic functions are not supported by current LLVM lowering core",
            code="LLVM029",
            function=function.name,
        )
    if function.async_:
        raise _backend_error(
            "async functions are not supported by current LLVM lowering core",
            code="LLVM030",
            function=function.name,
        )
    parameter_types = tuple(
        _lower_non_void_type(
            parameter.type,
            context=f"{context} parameter {parameter.name}",
        )
        for parameter in function.parameters
    )
    return LLVMFunctionSignature(
        return_type=(
            LLVM_VOID
            if function.return_type is None
            else _lower_type(function.return_type, context=f"{context} return type")
        ),
        parameter_types=parameter_types,
    )


def _lower_block_names(blocks: list[IRBasicBlock]) -> dict[str, str]:
    lowered: dict[str, str] = {}
    lowered_values: set[str] = set()
    for block in blocks:
        lowered_name = _mangle_local_name(block.name, prefix="bb")
        if lowered_name in lowered_values:
            raise _backend_error(
                "block names collide after LLVM sanitization",
                code="LLVM031",
                block=block.name,
            )
        lowered[block.name] = lowered_name
        lowered_values.add(lowered_name)
    return lowered


def _lower_type(type_ref: IRTypeRef, *, context: str) -> LLVMType:
    name = type_ref.name
    if name == "Unit":
        return LLVM_VOID
    if name == "Bool":
        return LLVM_I1
    if name in _INTEGER_TYPES:
        return _INTEGER_TYPES[name]
    if name == "String":
        return LLVM_PTR
    return LLVM_PTR


def _lower_non_void_type(type_ref: IRTypeRef, *, context: str) -> LLVMType:
    lowered = _lower_type(type_ref, context=context)
    if lowered == LLVM_VOID:
        raise _backend_error(
            "void/unit type is not valid in this LLVM value position",
            code="LLVM032",
            context=context,
        )
    return lowered


def _lower_literal(
    literal: IRLiteral,
    *,
    context: _FunctionContext,
    expected_type: LLVMType | None,
) -> LLVMValue:
    lowered_type = _lower_literal_type(literal.type)
    if lowered_type == LLVM_VOID:
        if expected_type == LLVM_VOID:
            return LLVMValue(type=LLVM_VOID, text="void")
        raise _backend_error(
            "unit literal is only supported as a void return marker",
            code="LLVM033",
        )
    if expected_type is not None and expected_type != lowered_type:
        raise _backend_error(
            "literal type does not match value context",
            code="LLVM034",
            expected=expected_type.spelling,
            actual=lowered_type.spelling,
        )
    if literal.type.name == "Bool":
        if not isinstance(literal.value, bool):
            raise _backend_error(
                "bool literal must carry a Python bool value",
                code="LLVM035",
            )
        return LLVMValue(type=LLVM_I1, text=("true" if literal.value else "false"))
    if literal.type.name in _INTEGER_TYPES:
        if isinstance(literal.value, bool) or not isinstance(literal.value, int):
            raise _backend_error(
                "integer literal must carry a Python int value",
                code="LLVM036",
            )
        return LLVMValue(type=lowered_type, text=str(literal.value))
    if literal.type.name == "String":
        if not isinstance(literal.value, str):
            raise _backend_error(
                "string literal must carry a Python str value",
                code="LLVM042",
            )
        global_string = context.module.register_global_string(literal.value)
        return LLVMValue(type=LLVM_PTR, text=f"@{global_string.name}")
    raise _backend_error(
        "literal kind is not supported by current LLVM lowering core",
        code="LLVM037",
        literal_type=literal.type.name,
    )


def _lower_literal_type(type_ref: IRTypeRef) -> LLVMType:
    if type_ref.name in {"Bool", "Unit", "String"} or type_ref.name in _INTEGER_TYPES:
        return _lower_type(type_ref, context=f"literal {type_ref.name}")
    raise _backend_error(
        "literal kind is not supported by current LLVM lowering core",
        code="LLVM038",
        literal_type=type_ref.name,
    )


def _is_unit_literal(value: Any) -> bool:
    return (
        isinstance(value, IRLiteral)
        and value.type.name == "Unit"
        and value.value is None
    )


def _is_skippable_declaration(declaration: IRDeclaration) -> bool:
    return isinstance(
        declaration,
        (IRStructType, IREnumType, IRNewtype, IRTraitSurface),
    )


def _unsupported_declaration_error(declaration: IRDeclaration) -> BackendError:
    if isinstance(declaration, IRImplSurface):
        kind = "ImplSurface"
    elif isinstance(declaration, IRTestSurface):
        kind = "TestSurface"
    else:
        kind = type(declaration).__name__
    return _backend_error(
        "unsupported IR declaration for current LLVM lowering core",
        code="LLVM039",
        declaration=kind,
    )


def _unsupported_value_error(value: Any) -> BackendError:
    return _backend_error(
        "unsupported IR value for current LLVM lowering core",
        code="LLVM040",
        value=type(value).__name__,
    )


def _mangle_symbol_ref(symbol: IRSymbolRef) -> str:
    return _mangle_global_name(symbol.module, symbol.name)


def _mangle_global_name(module_name: str | None, name: str) -> str:
    if module_name:
        return _sanitize_identifier(f"{module_name}__{name}")
    return _sanitize_identifier(name)


def _mangle_local_name(name: str, *, prefix: str) -> str:
    return _sanitize_identifier(f"{prefix}_{name}")


def _sanitize_identifier(value: str) -> str:
    sanitized = _IDENTIFIER_RE.sub("_", value).strip("_")
    if not sanitized:
        sanitized = "unnamed"
    if sanitized[0].isdigit():
        sanitized = f"v_{sanitized}"
    return sanitized


def _is_operator_symbol(value: str) -> bool:
    return bool(value) and all(not character.isalnum() and character != "_" for character in value)


def _backend_error(message: str, *, code: str, **details: Any) -> BackendError:
    payload = {
        "kind": "BackendError",
        "code": code,
        "message": message,
        "phase": "backend",
    }
    payload.update(details)
    return BackendError(message, payload=payload)


__all__ = [
    "BackendError",
    "lower_function",
    "lower_module",
]
