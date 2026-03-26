"""Structured diagnostics primitives for the Axiom compiler."""

from .models import (
    DEFAULT_SCHEMA_VERSION,
    Diagnostic,
    DiagnosticReport,
    Location,
    Position,
    RelatedLocation,
    Span,
)
from . import parser
from .parser import (
    diagnostic_from_parser_error,
    parse_file_report,
    report_from_parser_error,
)

__all__ = [
    "DEFAULT_SCHEMA_VERSION",
    "Diagnostic",
    "DiagnosticReport",
    "Location",
    "Position",
    "RelatedLocation",
    "Span",
    "diagnostic_from_parser_error",
    "parse_file_report",
    "parser",
    "report_from_parser_error",
]
