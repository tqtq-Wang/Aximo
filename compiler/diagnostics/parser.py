"""Parser-facing factories for schema-aligned diagnostics."""

from __future__ import annotations

from dataclasses import dataclass

from .models import Diagnostic, DiagnosticReport, Location, Span

__all__ = [
    "effect_requires_explicit_clause",
    "invalid_match_arm_syntax",
    "missing_module_declaration",
    "report",
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


def missing_module_declaration(file: str, span: Span) -> Diagnostic:
    return _build(file, span, _MISSING_MODULE_DECLARATION)


def invalid_match_arm_syntax(file: str, span: Span) -> Diagnostic:
    return _build(file, span, _INVALID_MATCH_ARM_SYNTAX)


def effect_requires_explicit_clause(file: str, span: Span) -> Diagnostic:
    return _build(file, span, _EFFECT_REQUIRES_EXPLICIT_CLAUSE)


def _build(file: str, span: Span, spec: _ParserDiagnosticSpec) -> Diagnostic:
    return Diagnostic(
        level="error",
        code=spec.code,
        message=spec.message,
        location=Location.from_span(file, span),
        help=spec.help,
    )
