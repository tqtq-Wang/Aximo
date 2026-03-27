from __future__ import annotations

from dataclasses import dataclass


FORMAL_UPSTREAM = "compiler.ir"


@dataclass(frozen=True)
class BackendTarget:
    name: str
    status: str
    entrypoint: str
    upstream: str
    summary: str


TARGETS: tuple[BackendTarget, ...] = (
    BackendTarget(
        name="ir-backend",
        status="reserved",
        entrypoint="python -m compiler.backend",
        upstream=FORMAL_UPSTREAM,
        summary=(
            "Formal backend handoff placeholder. This route exists to consume "
            "compiler.ir once the IR contract is available."
        ),
    ),
    BackendTarget(
        name="llvm-spike",
        status="spike",
        entrypoint="python -m compiler.backend.llvm",
        upstream="built-in demos only",
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
            "- llvm-spike remains isolated until it is reconnected through IR",
        )
    )


def iter_targets() -> tuple[BackendTarget, ...]:
    return TARGETS
