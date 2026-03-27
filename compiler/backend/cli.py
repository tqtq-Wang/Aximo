from __future__ import annotations

import argparse
import sys

from .boundary import describe_boundary, iter_targets
from .llvm.cli import main as llvm_spike_main


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Describe the Aximo backend boundary and available backend targets. "
            "Formal backend integration consumes compiler.ir rather than parser or AST outputs."
        )
    )
    parser.add_argument(
        "--describe-boundary",
        action="store_true",
        help="Print the backend boundary contract and exit.",
    )
    parser.add_argument(
        "--list-targets",
        action="store_true",
        help="List backend targets and their current status.",
    )
    parser.add_argument(
        "--target",
        choices=[target.name for target in iter_targets()],
        help="Optional backend target to invoke.",
    )
    return parser


def _print_targets() -> None:
    for target in iter_targets():
        print(f"{target.name} [{target.status}]")
        print(f"  upstream: {target.upstream}")
        print(f"  entrypoint: {target.entrypoint}")
        print(f"  summary: {target.summary}")


def main(argv: list[str] | None = None) -> int:
    parser = build_argument_parser()
    args, forwarded = parser.parse_known_args(argv)

    if args.describe_boundary or args.target is None:
        print(describe_boundary())

    if args.list_targets or args.target is None:
        if args.describe_boundary or args.target is None:
            print()
        _print_targets()

    if args.target is None:
        return 0

    if args.target == "ir-backend":
        print(
            "ir-backend is reserved for the formal compiler.ir handoff and is not executable yet.",
            file=sys.stderr,
        )
        return 2

    return llvm_spike_main(forwarded)
