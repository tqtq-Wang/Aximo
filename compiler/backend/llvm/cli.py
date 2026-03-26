from __future__ import annotations

import argparse
from pathlib import Path
import sys

from .demos import DEMOS, get_demo


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Emit textual LLVM IR from built-in Aximo feasibility demos. "
            "This spike does not define the formal frontend -> IR -> LLVM contract."
        )
    )
    parser.add_argument(
        "--demo",
        choices=sorted(DEMOS),
        help="Built-in feasibility demo to emit.",
    )
    parser.add_argument(
        "--emit-ir",
        action="store_true",
        help="Compatibility flag. This spike always emits textual LLVM IR.",
    )
    parser.add_argument(
        "--out",
        help="Destination .ll path.",
    )
    parser.add_argument(
        "--stdout",
        action="store_true",
        help="Also print the generated LLVM IR to stdout.",
    )
    parser.add_argument(
        "--list-demos",
        action="store_true",
        help="List built-in demos and exit.",
    )
    return parser


def _write_ir(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def main(argv: list[str] | None = None) -> int:
    parser = build_argument_parser()
    args = parser.parse_args(argv)

    if args.list_demos:
        for name in sorted(DEMOS):
            demo = DEMOS[name]
            print(f"{demo.name}: {demo.description}")
        return 0

    if not args.demo:
        parser.error("--demo is required unless --list-demos is used")
    if not args.out:
        parser.error("--out is required unless --list-demos is used")

    demo = get_demo(args.demo)
    output_path = Path(args.out)
    _write_ir(output_path, demo.ir)

    if args.stdout:
        sys.stdout.write(demo.ir)
        if not demo.ir.endswith("\n"):
            sys.stdout.write("\n")

    return 0
