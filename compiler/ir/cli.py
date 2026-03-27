from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from .lowering import LoweringError, lower_file
from .types import module_to_json


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Lower Axiom .ax files into IR JSON.")
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
        payload = lower_file(target)
    except LoweringError as error:
        json.dump(error.payload, sys.stderr, indent=args.indent, ensure_ascii=False, sort_keys=True)
        sys.stderr.write("\n")
        return 1
    sys.stdout.write(module_to_json(payload, indent=args.indent))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
