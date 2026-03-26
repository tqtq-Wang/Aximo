"""Parser-facing factories for schema-aligned diagnostics."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from compiler.parser import ParserError, parse_file

from .models import Diagnostic, DiagnosticReport, Location, Span

__all__ = [
    "diagnostic_from_parser_error",
    "effect_requires_explicit_clause",
    "generic_parser_error",
    "invalid_match_arm_syntax",
    "missing_module_declaration",
    "parse_file_report",
    "report",
    "report_from_parser_error",
]


@dataclass(frozen=True)
class _ParserDiagnosticSpec:
    code: str
    message: str
    help: str | None = None


_MISSING_MODULE_DECLARATION = _ParserDiagnosticSpec(
    code="P001",
    message="missing module declaration at start of file",
    help="add a `module ...` declaration before any imports or declarations",
)

_INVALID_MATCH_ARM_SYNTAX = _ParserDiagnosticSpec(
    code="P002",
    message="invalid match arm syntax; expected `=>`",
    help="write each arm as `pattern => expr`",
)

_EFFECT_REQUIRES_EXPLICIT_CLAUSE = _ParserDiagnosticSpec(
    code="E001",
    message="effectful operation requires an explicit effects clause",
    help="declare the required effect set, for example `effects [db.write]`",
)

def report(*diagnostics: Diagnostic) -> DiagnosticReport:
    return DiagnosticReport(diagnostics=tuple(diagnostics))


def parse_file_report(path: str | Path) -> DiagnosticReport:
    try:
        parse_file(path)
    except ParserError as error:
        return report_from_parser_error(error)
    return DiagnosticReport(diagnostics=())


def report_from_parser_error(error: ParserError) -> DiagnosticReport:
    return report(diagnostic_from_parser_error(error))


def diagnostic_from_parser_error(error: ParserError) -> Diagnostic:
    span = Span.from_bounds(
        error.start.line,
        error.start.column,
        error.end.line,
        error.end.column,
    )
    builder = _KNOWN_PARSER_DIAGNOSTICS.get(error.code)
    if builder is not None:
        return builder(_normalized_file_path(error), span)
    return generic_parser_error(error, span)


def missing_module_declaration(file: str, span: Span) -> Diagnostic:
    return _build(file, span, _MISSING_MODULE_DECLARATION)


def invalid_match_arm_syntax(file: str, span: Span) -> Diagnostic:
    return _build(file, span, _INVALID_MATCH_ARM_SYNTAX)


def effect_requires_explicit_clause(file: str, span: Span) -> Diagnostic:
    return _build(file, span, _EFFECT_REQUIRES_EXPLICIT_CLAUSE)


_KNOWN_PARSER_DIAGNOSTICS = {
    _MISSING_MODULE_DECLARATION.code: missing_module_declaration,
    _INVALID_MATCH_ARM_SYNTAX.code: invalid_match_arm_syntax,
    _EFFECT_REQUIRES_EXPLICIT_CLAUSE.code: effect_requires_explicit_clause,
}


def generic_parser_error(error: ParserError, span: Span | None = None) -> Diagnostic:
    return Diagnostic(
        level="error",
        code=error.code,
        message=error.message,
        location=Location.from_span(
            _normalized_file_path(error),
            span
            or Span.from_bounds(
                error.start.line,
                error.start.column,
                error.end.line,
                error.end.column,
            ),
        ),
        help=error.help,
    )


def _build(file: str, span: Span, spec: _ParserDiagnosticSpec) -> Diagnostic:
    return Diagnostic(
        level="error",
        code=spec.code,
        message=spec.message,
        location=Location.from_span(file, span),
        help=spec.help,
    )


def _normalized_file_path(error: ParserError) -> str:
    if error.file_path.startswith("<") and error.file_path.endswith(">"):
        return error.file_path
    path = Path(error.file_path)
    if not path.is_absolute():
        return error.file_path.replace("\\", "/")
    try:
        return path.resolve().relative_to(Path.cwd().resolve()).as_posix()
    except ValueError:
        return path.as_posix()
