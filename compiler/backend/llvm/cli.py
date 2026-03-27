from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from compiler.ir import module_from_json

from .demos import DEMOS, get_demo
from .lowering import BackendError, lower_module
from .text import render_module
from .toolchain import format_toolchain_report, probe_toolchain

DEFAULT_ARTIFACT_ROOT = Path(".tmp") / "llvm-spike"


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Run the isolated LLVM spike in a controlled compatibility mode. "
            "This entrypoint supports built-in demos, toolchain detection, and textual .ll "
            "artifact writing only. It does not define the formal compiler.ir -> backend contract."
        )
    )
    parser.add_argument(
        "--demo",
        choices=sorted(DEMOS),
        help="Built-in feasibility demo to emit.",
    )
    parser.add_argument(
        "--input-ir-json",
        help=(
            "Path to a compiler.ir Module JSON payload to lower into textual LLVM IR "
            "through the formal LLVM lowering core."
        ),
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
    parser.add_argument(
        "--check-toolchain",
        action="store_true",
        help="Report whether clang, llc, opt, llvm-as, and lli are available locally.",
    )
    return parser


def _write_ir(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def _resolve_output_path(raw_path: str | None, *, stem: str) -> Path:
    if raw_path is None:
        return DEFAULT_ARTIFACT_ROOT / f"{stem}.ll"

    candidate = Path(raw_path)
    if candidate.exists() and candidate.is_dir():
        return candidate / f"{stem}.ll"
    if candidate.suffix.lower() != ".ll":
        return candidate.with_suffix(".ll")
    return candidate


def _print_command_summary(
    *,
    mode: str,
    artifact_mode: str,
    output_path: Path | None = None,
    demo_name: str | None = None,
    input_ir_json: Path | None = None,
) -> None:
    lines = [
        "LLVM spike command summary",
        f"mode: {mode}",
        f"artifact_mode: {artifact_mode}",
    ]
    if demo_name is not None:
        lines.append(f"demo: {demo_name}")
    if input_ir_json is not None:
        lines.append(f"input_ir_json: {input_ir_json}")
    if output_path is not None:
        lines.append(f"output: {output_path}")
    lines.append("note: llvm-spike remains a controlled compatibility frontend, not a formal backend target")
    print("\n".join(lines), file=sys.stderr)


def _validate_mode_args(parser: argparse.ArgumentParser, args: argparse.Namespace) -> None:
    action_count = sum(
        bool(item)
        for item in (
            args.list_demos,
            args.check_toolchain,
            args.demo,
            args.input_ir_json,
        )
    )
    if action_count == 0:
        parser.error(
            "one of --list-demos, --check-toolchain, --demo, or --input-ir-json is required"
        )
    if args.list_demos and (args.demo or args.input_ir_json or args.out or args.stdout):
        parser.error("--list-demos cannot be combined with emit arguments")
    if args.check_toolchain and (args.demo or args.input_ir_json or args.out or args.stdout):
        parser.error("--check-toolchain cannot be combined with emit arguments")
    if args.demo and args.input_ir_json:
        parser.error("--demo and --input-ir-json are mutually exclusive")


def _handle_ir_json_mode(
    raw_path: str,
    *,
    raw_out: str | None,
    also_stdout: bool,
) -> int:
    input_path = Path(raw_path)
    if not input_path.is_file():
        print(f"{input_path}: file not found", file=sys.stderr)
        return 2

    try:
        module = module_from_json(input_path.read_text(encoding="utf-8"))
    except ValueError as error:
        print(f"{input_path}: invalid compiler.ir Module JSON: {error}", file=sys.stderr)
        return 2

    output_path = _resolve_output_path(raw_out, stem=input_path.stem)
    try:
        llvm_module = lower_module(module)
        llvm_ir = render_module(llvm_module)
    except BackendError as error:
        _print_command_summary(
            mode="ir-json",
            artifact_mode="lowering-error",
            output_path=output_path,
            input_ir_json=input_path,
        )
        json.dump(error.payload, sys.stderr, indent=2, ensure_ascii=False, sort_keys=True)
        sys.stderr.write("\n")
        return 2

    _write_ir(output_path, llvm_ir)
    artifact_mode = "write-ll-file-and-stdout" if also_stdout else "write-ll-file"
    _print_command_summary(
        mode="ir-json",
        artifact_mode=artifact_mode,
        output_path=output_path,
        input_ir_json=input_path,
    )

    if also_stdout:
        sys.stdout.write(llvm_ir)
        if not llvm_ir.endswith("\n"):
            sys.stdout.write("\n")

    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_argument_parser()
    args = parser.parse_args(argv)
    _validate_mode_args(parser, args)

    if args.list_demos:
        for name in sorted(DEMOS):
            demo = DEMOS[name]
            print(f"{demo.name}: {demo.description}")
        return 0

    if args.check_toolchain:
        print(format_toolchain_report(probe_toolchain()))
        return 0

    if args.input_ir_json:
        return _handle_ir_json_mode(
            args.input_ir_json,
            raw_out=args.out,
            also_stdout=args.stdout,
        )

    demo = get_demo(args.demo)
    output_path = _resolve_output_path(args.out, stem=demo.name)
    _write_ir(output_path, demo.ir)
    artifact_mode = "write-ll-file-and-stdout" if args.stdout else "write-ll-file"
    _print_command_summary(
        mode="demo",
        artifact_mode=artifact_mode,
        output_path=output_path,
        demo_name=demo.name,
    )

    if args.stdout:
        sys.stdout.write(demo.ir)
        if not demo.ir.endswith("\n"):
            sys.stdout.write("\n")

    return 0
