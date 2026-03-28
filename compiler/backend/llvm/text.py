from __future__ import annotations

from .model import (
    LLVMBasicBlock,
    LLVMBranchTerminator,
    LLVMCallInstruction,
    LLVMDeclaration,
    LLVMFunction,
    LLVMGlobalString,
    LLVMJumpTerminator,
    LLVMModule,
    LLVMReturnTerminator,
    LLVMType,
    LLVMValue,
    LLVM_VOID,
)


def render_module(module: LLVMModule) -> str:
    lines = [
        "; Aximo formal compiler.ir -> textual LLVM IR lowering",
        f'source_filename = "{_escape_string(module.source_filename)}"',
    ]

    if module.declarations:
        lines.append("")
        for declaration in module.declarations:
            lines.append(render_declaration(declaration))

    if module.globals:
        lines.append("")
        for global_string in module.globals:
            lines.append(render_global_string(global_string))

    if module.functions:
        lines.append("")
        for index, function in enumerate(module.functions):
            if index:
                lines.append("")
            lines.extend(render_function(function))

    return "\n".join(lines) + "\n"


def render_declaration(declaration: LLVMDeclaration) -> str:
    parameters = ", ".join(
        render_type(parameter_type)
        for parameter_type in declaration.signature.parameter_types
    )
    return (
        f"declare {render_type(declaration.signature.return_type)} "
        f"@{declaration.name}({parameters})"
    )


def render_global_string(global_string: LLVMGlobalString) -> str:
    return (
        f"@{global_string.name} = private unnamed_addr constant "
        f"[{global_string.byte_length} x i8] c\"{_escape_bytes(global_string.value)}\""
    )


def render_function(function: LLVMFunction) -> list[str]:
    linkage = "" if function.linkage is None else f" {function.linkage}"
    parameters = ", ".join(
        f"{render_type(parameter.type)} %{parameter.name}"
        for parameter in function.parameters
    )
    lines = [
        f"define{linkage} {render_type(function.signature.return_type)} "
        f"@{function.name}({parameters}) {{"
    ]
    for block in function.blocks:
        lines.extend(render_block(block))
    lines.append("}")
    return lines


def render_block(block: LLVMBasicBlock) -> list[str]:
    lines = [f"{block.name}:"]
    for instruction in block.instructions:
        lines.append(f"  {render_instruction(instruction)}")
    lines.append(f"  {render_terminator(block.terminator)}")
    return lines


def render_instruction(instruction: LLVMCallInstruction) -> str:
    arguments = ", ".join(render_typed_value(argument) for argument in instruction.arguments)
    prefix = ""
    if instruction.result_name is not None:
        prefix = f"%{instruction.result_name} = "
    return (
        f"{prefix}call {render_type(instruction.return_type)} "
        f"@{instruction.callee}({arguments})"
    )


def render_terminator(
    terminator: LLVMJumpTerminator | LLVMBranchTerminator | LLVMReturnTerminator,
) -> str:
    if isinstance(terminator, LLVMJumpTerminator):
        return f"br label %{terminator.target}"
    if isinstance(terminator, LLVMBranchTerminator):
        return (
            f"br {render_typed_value(terminator.condition)}, "
            f"label %{terminator.then_block}, "
            f"label %{terminator.else_block}"
        )
    if terminator.value is None or terminator.value.type == LLVM_VOID:
        return "ret void"
    return f"ret {render_typed_value(terminator.value)}"


def render_typed_value(value: LLVMValue) -> str:
    return f"{render_type(value.type)} {value.text}"


def render_type(type_ref: LLVMType) -> str:
    return type_ref.spelling


def _escape_string(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def _escape_bytes(value: str) -> str:
    parts: list[str] = []
    for byte in value.encode("utf-8") + b"\x00":
        if 32 <= byte <= 126 and byte not in {34, 92}:
            parts.append(chr(byte))
            continue
        parts.append(f"\\{byte:02X}")
    return "".join(parts)


__all__ = [
    "render_block",
    "render_declaration",
    "render_function",
    "render_global_string",
    "render_instruction",
    "render_module",
    "render_terminator",
    "render_type",
    "render_typed_value",
]
