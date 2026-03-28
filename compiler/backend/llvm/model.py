from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class LLVMType:
    spelling: str


LLVM_I1 = LLVMType("i1")
LLVM_I8 = LLVMType("i8")
LLVM_I16 = LLVMType("i16")
LLVM_I32 = LLVMType("i32")
LLVM_I64 = LLVMType("i64")
LLVM_PTR = LLVMType("ptr")
LLVM_VOID = LLVMType("void")


@dataclass(slots=True, frozen=True)
class LLVMValue:
    type: LLVMType
    text: str


@dataclass(slots=True, frozen=True)
class LLVMFunctionSignature:
    return_type: LLVMType
    parameter_types: tuple[LLVMType, ...] = ()


@dataclass(slots=True, frozen=True)
class LLVMParameter:
    name: str
    type: LLVMType


@dataclass(slots=True, frozen=True)
class LLVMDeclaration:
    name: str
    signature: LLVMFunctionSignature


@dataclass(slots=True, frozen=True)
class LLVMGlobalString:
    name: str
    value: str
    byte_length: int


@dataclass(slots=True, frozen=True)
class LLVMCallInstruction:
    callee: str
    return_type: LLVMType
    arguments: tuple[LLVMValue, ...] = ()
    result_name: str | None = None


LLVMInstruction = LLVMCallInstruction


@dataclass(slots=True, frozen=True)
class LLVMJumpTerminator:
    target: str


@dataclass(slots=True, frozen=True)
class LLVMBranchTerminator:
    condition: LLVMValue
    then_block: str
    else_block: str


@dataclass(slots=True, frozen=True)
class LLVMReturnTerminator:
    value: LLVMValue | None = None


LLVMTerminator = LLVMJumpTerminator | LLVMBranchTerminator | LLVMReturnTerminator


@dataclass(slots=True, frozen=True)
class LLVMBasicBlock:
    name: str
    instructions: tuple[LLVMInstruction, ...]
    terminator: LLVMTerminator


@dataclass(slots=True, frozen=True)
class LLVMFunction:
    name: str
    signature: LLVMFunctionSignature
    parameters: tuple[LLVMParameter, ...]
    blocks: tuple[LLVMBasicBlock, ...]
    linkage: str | None = None


@dataclass(slots=True, frozen=True)
class LLVMModule:
    name: str
    source_filename: str
    globals: tuple[LLVMGlobalString, ...] = ()
    declarations: tuple[LLVMDeclaration, ...] = ()
    functions: tuple[LLVMFunction, ...] = ()


__all__ = [
    "LLVMBasicBlock",
    "LLVMBranchTerminator",
    "LLVMCallInstruction",
    "LLVMDeclaration",
    "LLVMFunction",
    "LLVMFunctionSignature",
    "LLVMGlobalString",
    "LLVMInstruction",
    "LLVMJumpTerminator",
    "LLVMModule",
    "LLVMParameter",
    "LLVMReturnTerminator",
    "LLVMTerminator",
    "LLVMType",
    "LLVMValue",
    "LLVM_I1",
    "LLVM_I8",
    "LLVM_I16",
    "LLVM_I32",
    "LLVM_I64",
    "LLVM_PTR",
    "LLVM_VOID",
]
