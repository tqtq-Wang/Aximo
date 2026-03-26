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

__all__ = [
    "DEFAULT_SCHEMA_VERSION",
    "Diagnostic",
    "DiagnosticReport",
    "Location",
    "Position",
    "RelatedLocation",
    "Span",
    "parser",
]
