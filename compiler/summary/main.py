from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

if __package__ in (None, ""):
    CURRENT_DIR = Path(__file__).resolve().parent
    if str(CURRENT_DIR) not in sys.path:
        sys.path.insert(0, str(CURRENT_DIR))
    from builder import summary_from_source_file
    from contract import module_summary_from_mapping, new_module_summary, write_summary
else:
    from .builder import summary_from_source_file
    from .contract import module_summary_from_mapping, new_module_summary, write_summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Write a schema-aligned Axiom compiler summary JSON file."
    )
    parser.add_argument(
        "--module",
        help="Module name for a new summary skeleton or as an override for --input.",
    )
    parser.add_argument(
        "--import",
        dest="imports",
        action="append",
        default=[],
        help="Repeatable import path for a new summary skeleton.",
    )
    parser.add_argument(
        "--input",
        help="Optional JSON file containing a partial or complete summary payload.",
    )
    parser.add_argument(
        "--source",
        help="Optional .ax source file parsed through the public compiler.parser API.",
    )
    parser.add_argument(
        "--out",
        required=True,
        help="Destination .summary.json path.",
    )
    parser.add_argument(
        "--indent",
        type=int,
        default=2,
        help="JSON indentation width. Defaults to 2.",
    )
    return parser.parse_args()


def _load_summary_payload(path: str) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError("--input must point to a JSON object")
    return payload


def main() -> int:
    args = parse_args()

    if args.source and args.input:
        raise ValueError("--source and --input are mutually exclusive")
    if args.source and args.module:
        raise ValueError("--module cannot be used with --source")

    if args.source:
        summary = summary_from_source_file(args.source)
    elif args.input:
        payload = _load_summary_payload(args.input)
        if args.module:
            payload["module"] = args.module
        if args.imports:
            payload["imports"] = [*(payload.get("imports") or []), *args.imports]
        summary = module_summary_from_mapping(payload)
    else:
        if not args.module:
            raise ValueError("--module is required when --input is not provided")
        summary = new_module_summary(args.module, imports=args.imports)

    write_summary(summary, args.out, indent=args.indent)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
