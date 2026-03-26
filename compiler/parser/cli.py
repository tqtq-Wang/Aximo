from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from .parser import ParserError, parse_file


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Parse Axiom .ax files into AST JSON.")
    parser.add_argument("path", help="Path to a .ax source file")
    parser.add_argument("--indent", type=int, default=2, help="JSON indentation width")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_argument_parser()
    args = parser.parse_args(argv)
    target = Path(args.path)
    if not target.is_file():
        print(f"{target}: file not found", file=sys.stderr)
        return 1
    try:
        program = parse_file(target)
    except ParserError as error:
        json.dump(error.to_diagnostic_payload(), sys.stderr, indent=args.indent, ensure_ascii=False)
        sys.stderr.write("\n")
        return 1
    json.dump(program, sys.stdout, indent=args.indent, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
