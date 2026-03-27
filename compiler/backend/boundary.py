from __future__ import annotations

from dataclasses import dataclass


FORMAL_UPSTREAM = "compiler.ir"


@dataclass(frozen=True)
class BackendTarget:
    name: str
    status: str
    entrypoint: str
    upstream: str
    emits: str
    summary: str


TARGETS: tuple[BackendTarget, ...] = (
    BackendTarget(
        name="ir-backend",
        status="formal-llvm-minimal",
        entrypoint=(
            "python -m compiler.backend --target ir-backend "
            "--input <file.ax> --emit-llvm --out <file.ll>"
        ),
        upstream=FORMAL_UPSTREAM,
        emits="formal compiler.ir JSON or textual LLVM IR",
        summary=(
            "Formal backend entrypoint. This route lowers source through the "
            "public parser -> compiler.ir chain and can emit textual LLVM IR "
            "through the formal backend lowering core."
        ),
    ),
    BackendTarget(
        name="llvm-spike",
        status="spike-compatibility",
        entrypoint="python -m compiler.backend.llvm",
        upstream="built-in demos only",
        emits="textual LLVM IR from demos only",
        summary=(
            "Feasibility-only textual LLVM IR emitter. Not a formal backend "
            "contract and not a substitute for compiler.ir."
        ),
    ),
)


def describe_boundary() -> str:
    return "\n".join(
        (
            "Aximo backend boundary",
            f"- formal upstream: {FORMAL_UPSTREAM}",
            "- backend must not consume parser or AST objects directly",
            "- semantic lowering owns the parser/AST -> IR transition",
            "- ir-backend is the formal top-level route from source through compiler.ir into textual LLVM IR",
            "- llvm-spike remains a spike-only compatibility path for built-in demos",
        )
    )


def iter_targets() -> tuple[BackendTarget, ...]:
    return TARGETS


def get_target(name: str) -> BackendTarget:
    for target in TARGETS:
        if target.name == name:
            return target
    raise KeyError(f"unknown backend target: {name}")
