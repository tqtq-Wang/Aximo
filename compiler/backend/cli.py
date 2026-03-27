from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from compiler.ir import module_to_json
from compiler.ir.lowering import LoweringError, lower_file

from .boundary import describe_boundary, get_target, iter_targets
from .llvm import BackendError, lower_module, render_module
from .llvm.cli import main as llvm_spike_main


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Describe the Aximo backend boundary and invoke backend targets. "
            "The formal top-level backend route consumes compiler.ir rather than "
            "parser or AST outputs."
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


def build_ir_backend_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m compiler.backend --target ir-backend",
        description=(
            "Formal ir-backend route. This path lowers source through "
            "compiler.ir.lowering and can emit compiler.ir JSON or textual LLVM IR."
        ),
    )
    parser.add_argument(
        "--input",
        help="Source .ax file for the formal ir-backend route.",
    )
    emit_group = parser.add_mutually_exclusive_group(required=True)
    emit_group.add_argument(
        "--emit-ir",
        action="store_true",
        help="Emit formal compiler.ir JSON for ir-backend.",
    )
    emit_group.add_argument(
        "--emit-llvm",
        action="store_true",
        help="Emit textual LLVM IR through the formal compiler.ir -> backend lowering path.",
    )
    parser.add_argument(
        "--out",
        help="Destination path for emitted output.",
    )
    parser.add_argument(
        "--stdout",
        action="store_true",
        help="Also print emitted output to stdout.",
    )
    return parser


def _print_targets() -> None:
    for target in iter_targets():
        print(f"{target.name} [{target.status}]")
        print(f"  upstream: {target.upstream}")
        print(f"  entrypoint: {target.entrypoint}")
        print(f"  emits: {target.emits}")
        print(f"  summary: {target.summary}")


def _emit_error(message: str, *, code: int = 2) -> int:
    print(message, file=sys.stderr)
    return code


def _emit_json_error(payload: dict[str, object], *, code: int = 1) -> int:
    json.dump(payload, sys.stderr, indent=2, ensure_ascii=False, sort_keys=True)
    sys.stderr.write("\n")
    return code


def _write_output(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def _lower_source_to_ir(input_path: Path) -> object | int:
    try:
        return lower_file(input_path)
    except LoweringError as error:
        return _emit_json_error(error.payload)


def _run_ir_backend(argv: list[str]) -> int:
    parser = build_ir_backend_argument_parser()
    args, unknown = parser.parse_known_args(argv)

    if unknown:
        return _emit_error(
            "ir-backend does not accept unknown arguments: " + " ".join(unknown)
        )

    if not args.input:
        return _emit_error("--input is required for ir-backend")
    if not args.out and not args.stdout:
        return _emit_error("ir-backend requires --out or --stdout")

    input_path = Path(args.input)
    if not input_path.is_file():
        return _emit_error(f"{input_path}: file not found", code=1)

    output_path = Path(args.out) if args.out else None
    if args.emit_ir and output_path is not None and output_path.suffix.lower() == ".ll":
        return _emit_error(
            "ir-backend --emit-ir emits formal compiler.ir JSON, not textual LLVM IR .ll."
        )
    if args.emit_llvm and output_path is not None and output_path.suffix.lower() != ".ll":
        return _emit_error(
            "ir-backend --emit-llvm should write to a .ll path so the formal textual LLVM IR output is explicit."
        )

    module = _lower_source_to_ir(input_path)
    if isinstance(module, int):
        return module

    if args.emit_ir:
        payload = module_to_json(module)
    else:
        try:
            payload = render_module(lower_module(module))
        except BackendError as error:
            return _emit_json_error(error.payload)

    if output_path is not None:
        _write_output(output_path, payload)
    if args.stdout:
        sys.stdout.write(payload)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_argument_parser()
    args, forwarded = parser.parse_known_args(argv)

    show_boundary = args.describe_boundary
    show_targets = args.list_targets
    if args.target is None and not show_boundary and not show_targets:
        show_boundary = True
        show_targets = True

    if show_boundary:
        print(describe_boundary())

    if show_targets:
        if show_boundary:
            print()
        _print_targets()

    if args.target is None:
        if forwarded:
            return _emit_error("unexpected arguments without --target: " + " ".join(forwarded))
        return 0

    target = get_target(args.target)
    if target.name == "ir-backend":
        return _run_ir_backend(forwarded)

    return llvm_spike_main(forwarded)
