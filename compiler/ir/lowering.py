from __future__ import annotations

import ast as python_ast
from dataclasses import dataclass, field
from pathlib import Path
import re
from typing import Any

from compiler.parser import ParseResult, ParserError, parse_file_result, parse_source_result

from .types import (
    BasicBlock,
    Bind,
    Branch,
    ConstructValue,
    DirectCall,
    EnumType,
    EnumVariant,
    ErrorPropagationPlaceholder,
    Eval,
    FieldValue,
    Function,
    ImplSurface,
    Import,
    Jump,
    Literal,
    LocalBinding,
    LocalRef,
    Module,
    NamedArgument,
    Newtype,
    Parameter,
    ParameterRef,
    Return,
    StructField,
    StructType,
    SymbolRef,
    TestSurface,
    TraitMember,
    TraitSurface,
    TypeParameter,
    TypeRef,
)

_NAME_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_PATH_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_:.]*$")
_CONSTRUCT_RE = re.compile(r"^(?P<name>[A-Za-z_][A-Za-z0-9_:]*)\s*\{(?P<body>.*)\}$", re.DOTALL)
_OPERATOR_RESULT_TYPES = {
    "==": "Bool",
    "!=": "Bool",
    "<": "Bool",
    "<=": "Bool",
    ">": "Bool",
    ">=": "Bool",
}


class LoweringError(ValueError):
    def __init__(self, message: str, *, payload: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.payload = payload or {
            "kind": "LoweringError",
            "code": "IR999",
            "message": message,
        }


def lower_file(path: str | Path) -> Module:
    return lower_parse_result(parse_file_result(path))


def lower_source(source: str, file_path: str = "<memory>") -> Module:
    return lower_parse_result(parse_source_result(source, file_path=file_path))


def lower_parse_result(result: ParseResult) -> Module:
    if result.error is not None:
        raise LoweringError("parser returned an error result", payload=_parser_error_payload(result.error))
    if result.program is None:
        raise LoweringError(
            "parser returned no program payload",
            payload={
                "kind": "LoweringError",
                "code": "IR001",
                "message": "parser returned no program payload",
                "phase": "lowering",
                "filePath": _normalize_path(result.file_path),
            },
        )

    program = result.program
    declarations: list[Any] = []
    for declaration in program.get("declarations", []):
        declarations.append(_lower_declaration(declaration))
    return Module(
        name=program["module"]["path"],
        imports=[_lower_import(use_decl) for use_decl in program.get("uses", [])],
        declarations=declarations,
        source_file=_normalize_path(result.file_path),
    )


def _lower_import(use_decl: dict[str, Any]) -> Import:
    return Import(
        module=use_decl["path"],
        names=[str(name) for name in use_decl.get("imports", [])],
        alias=None,
    )


def _lower_declaration(declaration: dict[str, Any]) -> Any:
    kind = declaration.get("kind")
    if kind == "FunctionDecl":
        return _FunctionLowerer(declaration).lower()
    if kind == "StructDecl":
        return StructType(
            name=declaration["name"],
            visibility=_lower_visibility(declaration["visibility"]),
            fields=[
                StructField(
                    name=field["name"],
                    type=_lower_type_ref(field["type"]),
                    visibility=_lower_visibility(field["visibility"]),
                )
                for field in declaration.get("fields", [])
            ],
        )
    if kind == "EnumDecl":
        return EnumType(
            name=declaration["name"],
            visibility=_lower_visibility(declaration["visibility"]),
            variants=[
                EnumVariant(name=variant["name"])
                for variant in declaration.get("variants", [])
            ],
        )
    if kind == "NewtypeDecl":
        return Newtype(
            name=declaration["name"],
            target=_lower_type_ref(declaration["target"]),
            visibility=_lower_visibility(declaration["visibility"]),
        )
    if kind == "TraitDecl":
        return TraitSurface(
            name=declaration["name"],
            visibility=_lower_visibility(declaration["visibility"]),
            type_parameters=_lower_type_parameters(declaration.get("typeParameters", [])),
            members=[
                TraitMember(
                    name=member["name"],
                    type_parameters=_lower_type_parameters(member.get("typeParameters", [])),
                    parameters=[
                        Parameter(
                            name=parameter["name"],
                            type=_lower_type_ref(parameter["type"]),
                        )
                        for parameter in member.get("parameters", [])
                    ],
                    return_type=_lower_type_ref(member["returnType"]),
                    effects=[str(effect) for effect in member.get("effects", [])],
                    async_=bool(member.get("async", False)),
                )
                for member in declaration.get("members", [])
            ],
        )
    if kind == "ImplDecl":
        return ImplSurface(
            trait=SymbolRef(name=declaration["trait"]),
            for_type=TypeRef(str(declaration["forType"])),
            methods=[
                _FunctionLowerer(member).lower()
                for member in declaration.get("members", [])
            ],
        )
    if kind == "TestDecl":
        return _FunctionLowerer(declaration["body"]).lower_test_surface(declaration["name"])
    raise _unsupported_node("declaration", kind, declaration)


@dataclass(slots=True)
class _BlockState:
    name: str
    instructions: list[Any] = field(default_factory=list)
    terminator: Any | None = None


class _FunctionLowerer:
    def __init__(self, declaration: dict[str, Any], *, notes: list[str] | None = None) -> None:
        self.declaration = declaration
        self.parameter_names = {
            parameter["name"] for parameter in declaration.get("parameters", [])
        }
        self.local_names: set[str] = set()
        self.block_order: list[str] = []
        self.blocks: dict[str, _BlockState] = {}
        self.block_counter = 0
        self.base_notes = list(notes or [])

    def lower(self) -> Function:
        entry_name = self._build_blocks(
            self.declaration["body"].get("statements", []),
            tail_position=True,
        )

        return Function(
            name=self.declaration["name"],
            visibility=_lower_visibility(self.declaration["visibility"]),
            type_parameters=_lower_type_parameters(self.declaration.get("typeParameters", [])),
            parameters=[
                Parameter(
                    name=parameter["name"],
                    type=_lower_type_ref(parameter["type"]),
                )
                for parameter in self.declaration.get("parameters", [])
            ],
            return_type=_lower_type_ref(self.declaration["returnType"]),
            effects=[str(effect) for effect in self.declaration.get("effects", [])],
            async_=bool(self.declaration.get("async", False)),
            entry_block=entry_name,
            blocks=[
                BasicBlock(
                    name=block_name,
                    instructions=self.blocks[block_name].instructions,
                    terminator=self.blocks[block_name].terminator or Return(),
                )
                for block_name in self.block_order
            ],
            notes=list(self.base_notes),
        )

    def lower_test_surface(self, name: str) -> TestSurface:
        entry_name = self._build_blocks(
            self.declaration.get("statements", []),
            tail_position=False,
        )
        return TestSurface(
            name=name,
            entry_block=entry_name,
            blocks=[
                BasicBlock(
                    name=block_name,
                    instructions=self.blocks[block_name].instructions,
                    terminator=self.blocks[block_name].terminator or Return(),
                )
                for block_name in self.block_order
            ],
            notes=list(self.base_notes),
        )

    def _build_blocks(self, statements: list[dict[str, Any]], *, tail_position: bool) -> str:
        entry_name = self._new_block("entry", explicit_name="entry")
        end_block = self._lower_statement_list(
            statements,
            entry_name,
            tail_position=tail_position,
        )
        if end_block is not None and self.blocks[end_block].terminator is None:
            self.blocks[end_block].terminator = Return()
        return entry_name

    def _lower_statement_list(
        self,
        statements: list[dict[str, Any]],
        block_name: str,
        *,
        tail_position: bool,
    ) -> str | None:
        current_block = block_name
        for index, statement in enumerate(statements):
            is_tail_statement = tail_position and index == len(statements) - 1
            current_block = self._lower_statement(
                statement,
                current_block,
                tail_position=is_tail_statement,
            )
            if current_block is None:
                return None
        return current_block

    def _lower_statement(
        self,
        statement: dict[str, Any],
        block_name: str,
        *,
        tail_position: bool,
    ) -> str | None:
        kind = statement.get("kind")
        if kind == "LetStmt":
            return self._lower_let_statement(statement, block_name)
        if kind == "ExprStmt":
            expression = statement["expression"]
            if tail_position:
                return self._lower_tail_expression(expression, block_name)
            self._append_instruction(block_name, self._lower_eval_instruction(expression))
            return block_name
        if kind == "ReturnStmt":
            return self._lower_return_statement(statement, block_name)
        if kind == "IfStmt":
            return self._lower_if_statement(statement, block_name, tail_position=tail_position)
        raise _unsupported_node("statement", kind, statement)

    def _lower_let_statement(self, statement: dict[str, Any], block_name: str) -> str:
        name = statement["name"]
        value_node = statement["value"]
        if _is_propagating_call(value_node):
            placeholder = self._lower_error_propagation(value_node, binding_name=name)
            self._append_instruction(block_name, placeholder)
        else:
            self._append_instruction(
                block_name,
                Bind(binding=LocalBinding(name=name), value=self._lower_value(value_node)),
            )
        self.local_names.add(name)
        return block_name

    def _lower_return_statement(self, statement: dict[str, Any], block_name: str) -> None:
        value_node = statement["value"]
        if _is_propagating_call(value_node):
            temp_name = self._new_temp("_return")
            self._append_instruction(
                block_name,
                self._lower_error_propagation(value_node, binding_name=temp_name),
            )
            self._set_terminator(block_name, Return(LocalRef(temp_name)))
            self.local_names.add(temp_name)
            return None
        self._set_terminator(block_name, Return(self._lower_value(value_node)))
        return None

    def _lower_tail_expression(self, expression: dict[str, Any], block_name: str) -> None:
        if expression.get("kind") == "MatchExpr":
            self._lower_tail_match(expression, block_name)
            return None
        if _is_propagating_call(expression):
            temp_name = self._new_temp("_return")
            self._append_instruction(
                block_name,
                self._lower_error_propagation(expression, binding_name=temp_name),
            )
            self.local_names.add(temp_name)
            self._set_terminator(block_name, Return(LocalRef(temp_name)))
            return None
        self._set_terminator(block_name, Return(self._lower_value(expression)))
        return None

    def _lower_if_statement(
        self,
        statement: dict[str, Any],
        block_name: str,
        *,
        tail_position: bool,
    ) -> str | None:
        then_block_name = self._new_block("if_then")
        else_block = statement.get("elseBlock")
        condition = self._lower_value(statement["condition"])

        if tail_position and else_block is None:
            raise _unsupported_node("tail if statement without else branch", statement.get("kind"), statement)

        if tail_position:
            else_block_name = self._new_block("if_else")
            self._set_terminator(
                block_name,
                Branch(condition=condition, then_block=then_block_name, else_block=else_block_name),
            )
            self._lower_statement_list(
                statement["thenBlock"].get("statements", []),
                then_block_name,
                tail_position=True,
            )
            self._lower_statement_list(
                else_block.get("statements", []),
                else_block_name,
                tail_position=True,
            )
            return None

        merge_block_name = self._new_block("if_end")
        if else_block is None:
            else_block_name = merge_block_name
        else:
            else_block_name = self._new_block("if_else")
        self._set_terminator(
            block_name,
            Branch(condition=condition, then_block=then_block_name, else_block=else_block_name),
        )

        then_exit = self._lower_statement_list(
            statement["thenBlock"].get("statements", []),
            then_block_name,
            tail_position=False,
        )
        if then_exit is not None and self.blocks[then_exit].terminator is None:
            self._set_terminator(then_exit, Jump(merge_block_name))

        if else_block is not None:
            else_exit = self._lower_statement_list(
                else_block.get("statements", []),
                else_block_name,
                tail_position=False,
            )
            if else_exit is not None and self.blocks[else_exit].terminator is None:
                self._set_terminator(else_exit, Jump(merge_block_name))

        return merge_block_name

    def _lower_tail_match(self, expression: dict[str, Any], block_name: str) -> None:
        subject = self._lower_value(expression["subject"])
        arms = list(expression.get("arms", []))
        if not arms:
            self._set_terminator(block_name, Return())
            return

        current_block_name = block_name
        for index, arm in enumerate(arms):
            arm_block_name = self._new_block("match_arm")
            is_last_arm = index == len(arms) - 1
            if is_last_arm:
                self._set_terminator(current_block_name, Jump(arm_block_name))
            else:
                next_block_name = self._new_block("match_next")
                condition = DirectCall(
                    callee=SymbolRef(name="=="),
                    arguments=[subject, SymbolRef(name=arm["pattern"])],
                    result_type=TypeRef("Bool"),
                )
                self._set_terminator(
                    current_block_name,
                    Branch(
                        condition=condition,
                        then_block=arm_block_name,
                        else_block=next_block_name,
                    ),
                )
                current_block_name = next_block_name
            self._lower_tail_expression(arm["body"], arm_block_name)

    def _lower_eval_instruction(self, expression: dict[str, Any]) -> Any:
        if _is_propagating_call(expression):
            return self._lower_error_propagation(expression)
        return Eval(value=self._lower_value(expression))

    def _lower_error_propagation(
        self,
        expression: dict[str, Any],
        *,
        binding_name: str | None = None,
    ) -> ErrorPropagationPlaceholder:
        source, error_adapter = self._lower_propagation_source(expression)
        return ErrorPropagationPlaceholder(
            source=source,
            binding=(None if binding_name is None else LocalBinding(name=binding_name)),
            error_adapter=error_adapter,
            strategy="result_branch",
        )

    def _lower_propagation_source(
        self,
        expression: dict[str, Any],
    ) -> tuple[Any, SymbolRef | None]:
        callee_name = str(expression["callee"])
        arguments = list(expression.get("arguments", []))
        if callee_name.endswith(".map_err"):
            if len(arguments) != 1:
                raise _unsupported_node("map_err propagation call", expression.get("kind"), expression)
            adapter = self._lower_value(arguments[0])
            if not isinstance(adapter, SymbolRef):
                raise LoweringError(
                    "map_err adapter must lower to SymbolRef",
                    payload={
                        "kind": "LoweringError",
                        "code": "IR003",
                        "message": "map_err adapter must lower to SymbolRef",
                        "phase": "lowering",
                        "callee": callee_name,
                    },
                )
            base_call = callee_name[: -len(".map_err")]
            return self._parse_text_value(base_call), adapter
        return self._lower_call_expression(expression), None

    def _lower_value(self, expression: dict[str, Any]) -> Any:
        kind = expression.get("kind")
        if kind == "IdentifierExpr":
            return self._parse_text_value(expression["name"])
        if kind == "StringLiteralExpr":
            return Literal(type=TypeRef("String"), value=expression["value"])
        if kind == "BoolLiteralExpr":
            return Literal(type=TypeRef("Bool"), value=bool(expression["value"]))
        if kind == "CallExpr":
            if expression.get("propagateError"):
                raise LoweringError(
                    "propagating call cannot lower directly as value",
                    payload={
                        "kind": "LoweringError",
                        "code": "IR004",
                        "message": "propagating call cannot lower directly as value",
                        "phase": "lowering",
                        "callee": expression.get("callee"),
                    },
                )
            return self._lower_call_expression(expression)
        raise _unsupported_node("expression", kind, expression)

    def _lower_call_expression(self, expression: dict[str, Any]) -> Any:
        callee_name = str(expression["callee"])
        arguments = [self._lower_value(argument) for argument in expression.get("arguments", [])]
        if _looks_constructor_name(callee_name) and "." not in callee_name and callee_name not in {"Ok", "Err"}:
            return ConstructValue(
                type=TypeRef(callee_name),
                constructor=SymbolRef(name=callee_name),
                arguments=arguments,
            )
        result_type = None
        if callee_name in _OPERATOR_RESULT_TYPES:
            result_type = TypeRef(_OPERATOR_RESULT_TYPES[callee_name])
        return DirectCall(
            callee=SymbolRef(name=callee_name),
            arguments=arguments,
            result_type=result_type,
            await_=bool(expression.get("await", False)),
        )

    def _parse_text_value(self, source_text: str) -> Any:
        text = source_text.strip()
        if text == "()":
            return Literal(type=TypeRef("Unit"), value=None)
        if text == "true":
            return Literal(type=TypeRef("Bool"), value=True)
        if text == "false":
            return Literal(type=TypeRef("Bool"), value=False)
        if text.startswith('"') and text.endswith('"'):
            return Literal(type=TypeRef("String"), value=python_ast.literal_eval(text))
        if text.isdigit():
            return Literal(type=TypeRef("Int"), value=int(text))

        construct_match = _CONSTRUCT_RE.match(text)
        if construct_match is not None:
            fields = []
            for item in _split_top_level(construct_match.group("body"), ","):
                if not item.strip():
                    continue
                field_name, field_value = _split_top_level_once(item, ":")
                fields.append(
                    NamedArgument(
                        name=field_name.strip(),
                        value=self._parse_text_value(field_value),
                    )
                )
            type_name = construct_match.group("name")
            return ConstructValue(
                type=TypeRef(type_name),
                constructor=SymbolRef(name=type_name),
                fields=fields,
            )

        outer_call = _split_outer_call(text)
        if outer_call is not None:
            callee_name, raw_arguments = outer_call
            arguments = [
                self._parse_text_value(argument)
                for argument in _split_top_level(raw_arguments, ",")
                if argument.strip()
            ]
            if _looks_constructor_name(callee_name) and "." not in callee_name and callee_name not in {"Ok", "Err"}:
                return ConstructValue(
                    type=TypeRef(callee_name),
                    constructor=SymbolRef(name=callee_name),
                    arguments=arguments,
                )
            return DirectCall(
                callee=SymbolRef(name=callee_name),
                arguments=arguments,
            )

        if "." in text:
            dotted_value = self._maybe_field_chain(text)
            if dotted_value is not None:
                return dotted_value

        if text in self.local_names:
            return LocalRef(name=text)
        if text in self.parameter_names:
            return ParameterRef(name=text)
        if _PATH_RE.fullmatch(text):
            return SymbolRef(name=text)

        raise LoweringError(
            "source expression is not representable by current IR core",
            payload={
                "kind": "LoweringError",
                "code": "IR005",
                "message": "source expression is not representable by current IR core",
                "phase": "lowering",
                "sourceText": text,
            },
        )

    def _maybe_field_chain(self, text: str) -> Any | None:
        parts = text.split(".")
        if not parts or any(not _NAME_RE.fullmatch(part) for part in parts):
            return None
        base_name = parts[0]
        if base_name in self.local_names:
            value: Any = LocalRef(name=base_name)
        elif base_name in self.parameter_names:
            value = ParameterRef(name=base_name)
        else:
            return None
        for field_name in parts[1:]:
            value = FieldValue(base=value, field=field_name)
        return value

    def _new_block(self, prefix: str, *, explicit_name: str | None = None) -> str:
        if explicit_name is not None:
            name = explicit_name
        else:
            self.block_counter += 1
            name = f"{prefix}_{self.block_counter}"
        if name in self.blocks:
            raise LoweringError(
                "duplicate block name during lowering",
                payload={
                    "kind": "LoweringError",
                    "code": "IR006",
                    "message": "duplicate block name during lowering",
                    "phase": "lowering",
                    "block": name,
                },
            )
        self.blocks[name] = _BlockState(name=name)
        self.block_order.append(name)
        return name

    def _new_temp(self, prefix: str) -> str:
        while True:
            self.block_counter += 1
            candidate = f"{prefix}_{self.block_counter}"
            if candidate not in self.local_names and candidate not in self.parameter_names:
                return candidate

    def _append_instruction(self, block_name: str, instruction: Any) -> None:
        block = self.blocks[block_name]
        if block.terminator is not None:
            raise LoweringError(
                "cannot append instruction after terminator",
                payload={
                    "kind": "LoweringError",
                    "code": "IR007",
                    "message": "cannot append instruction after terminator",
                    "phase": "lowering",
                    "block": block_name,
                },
            )
        block.instructions.append(instruction)

    def _set_terminator(self, block_name: str, terminator: Any) -> None:
        block = self.blocks[block_name]
        if block.terminator is not None:
            raise LoweringError(
                "block terminator already set",
                payload={
                    "kind": "LoweringError",
                    "code": "IR008",
                    "message": "block terminator already set",
                    "phase": "lowering",
                    "block": block_name,
                },
            )
        block.terminator = terminator


def _lower_visibility(visibility: str) -> str:
    if visibility == "pub":
        return "public"
    if visibility == "internal":
        return "internal"
    return "private"


def _lower_type_parameters(items: list[dict[str, Any]]) -> list[TypeParameter]:
    return [
        TypeParameter(
            name=item["name"],
            constraint=(None if item.get("constraint") is None else SymbolRef(name=str(item["constraint"]))),
        )
        for item in items
    ]


def _lower_type_ref(type_ref: dict[str, Any]) -> TypeRef:
    return TypeRef(_render_type_ref(type_ref))


def _render_type_ref(type_ref: dict[str, Any]) -> str:
    kind = type_ref.get("kind")
    if kind == "NamedType":
        return str(type_ref["name"])
    if kind == "UnitType":
        return "Unit"
    if kind == "ResultType":
        ok_type = _render_type_ref(type_ref["ok"])
        err_type = _render_type_ref(type_ref["err"])
        return f"Result<{ok_type}, {err_type}>"
    raise _unsupported_node("type", kind, type_ref)


def _is_propagating_call(expression: dict[str, Any]) -> bool:
    return expression.get("kind") == "CallExpr" and bool(expression.get("propagateError"))


def _split_top_level(text: str, delimiter: str) -> list[str]:
    parts: list[str] = []
    current: list[str] = []
    paren_depth = 0
    brace_depth = 0
    in_string = False
    escape = False

    for char in text:
        if in_string:
            current.append(char)
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == '"':
                in_string = False
            continue

        if char == '"':
            in_string = True
            current.append(char)
            continue
        if char == "(":
            paren_depth += 1
            current.append(char)
            continue
        if char == ")":
            paren_depth -= 1
            current.append(char)
            continue
        if char == "{":
            brace_depth += 1
            current.append(char)
            continue
        if char == "}":
            brace_depth -= 1
            current.append(char)
            continue
        if char == delimiter and paren_depth == 0 and brace_depth == 0:
            parts.append("".join(current).strip())
            current = []
            continue
        current.append(char)

    parts.append("".join(current).strip())
    return parts


def _split_top_level_once(text: str, delimiter: str) -> tuple[str, str]:
    paren_depth = 0
    brace_depth = 0
    in_string = False
    escape = False
    for index, char in enumerate(text):
        if in_string:
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
            continue
        if char == "(":
            paren_depth += 1
            continue
        if char == ")":
            paren_depth -= 1
            continue
        if char == "{":
            brace_depth += 1
            continue
        if char == "}":
            brace_depth -= 1
            continue
        if char == delimiter and paren_depth == 0 and brace_depth == 0:
            return text[:index], text[index + 1 :]
    raise LoweringError(
        "could not split source text at top level",
        payload={
            "kind": "LoweringError",
            "code": "IR009",
            "message": "could not split source text at top level",
            "phase": "lowering",
            "sourceText": text,
            "delimiter": delimiter,
        },
    )


def _split_outer_call(text: str) -> tuple[str, str] | None:
    if not text.endswith(")"):
        return None
    in_string = False
    escape = False
    depth = 0
    open_index: int | None = None
    for index, char in enumerate(text):
        if in_string:
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
            continue
        if char == "(":
            if depth == 0:
                open_index = index
            depth += 1
            continue
        if char == ")":
            depth -= 1
            if depth == 0:
                if index != len(text) - 1 or open_index is None:
                    return None
                callee = text[:open_index].strip()
                if not callee:
                    return None
                return callee, text[open_index + 1 : -1]
    return None


def _looks_constructor_name(name: str) -> bool:
    return bool(name) and name[0].isupper() and _PATH_RE.fullmatch(name) is not None


def _normalize_path(path: str) -> str:
    return path.replace("\\", "/")


def _unsupported_node(category: str, actual_kind: str | None, node: dict[str, Any]) -> LoweringError:
    message = f"unsupported {category} for current IR lowering: {actual_kind!r}"
    return LoweringError(
        message,
        payload={
            "kind": "LoweringError",
            "code": "IR002",
            "message": message,
            "phase": "lowering",
            "sourceKind": actual_kind,
            "nodeKeys": sorted(node.keys()),
        },
    )


def _parser_error_payload(error: ParserError) -> dict[str, Any]:
    return {
        "kind": "LoweringError",
        "code": error.code,
        "message": error.message,
        "help": error.help,
        "phase": "parser",
        "filePath": error.normalized_file_path,
        "span": {
            "file": error.normalized_file_path,
            "start": {
                "line": error.span.start.line,
                "column": error.span.start.column,
            },
            "end": {
                "line": error.span.end.line,
                "column": error.span.end.column,
            },
        },
    }
