from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from compiler.diagnostics import Diagnostic, DiagnosticReport, Location, Position
from compiler.diagnostics import Span as DiagnosticSpan
from compiler.diagnostics import parser as parser_diagnostics

from .parser import parse_file_result
from .types import ParserError


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
    result = parse_file_result(target)
    if result.error is not None:
        json.dump(
            build_diagnostic_report(result.error).to_dict(),
            sys.stderr,
            indent=args.indent,
            ensure_ascii=False,
        )
        sys.stderr.write("\n")
        return 1
    json.dump(result.program, sys.stdout, indent=args.indent, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


def build_diagnostic_report(error: ParserError) -> DiagnosticReport:
    factory = {
        "P001": parser_diagnostics.missing_module_declaration,
        "P002": parser_diagnostics.invalid_match_arm_syntax,
        "E001": parser_diagnostics.effect_requires_explicit_clause,
    }.get(error.code)
    span = DiagnosticSpan.from_bounds(
        error.span.start.line,
        error.span.start.column,
        error.span.end.line,
        error.span.end.column,
    )
    if factory is not None:
        diagnostic = factory(error.normalized_file_path, span)
        return parser_diagnostics.report(diagnostic)
    diagnostic = Diagnostic(
        level="error",
        code=error.code,
        message=error.message,
        location=Location(
            file=error.normalized_file_path,
            start=Position(error.span.start.line, error.span.start.column),
            end=Position(error.span.end.line, error.span.end.column),
        ),
        help=error.help,
    )
    return DiagnosticReport(diagnostics=(diagnostic,))


if __name__ == "__main__":
    raise SystemExit(main())
