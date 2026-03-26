from __future__ import annotations

from dataclasses import dataclass, field
import json
import re


DEFAULT_SCHEMA_VERSION = "0.1.0"
_LEVELS = {"error", "warning", "info"}
_CODE_PATTERN = re.compile(r"^[A-Z][0-9]{3}$")


@dataclass(frozen=True, order=True)
class Position:
    line: int
    column: int

    def __post_init__(self) -> None:
        if self.line < 1:
            raise ValueError("line must be >= 1")
        if self.column < 1:
            raise ValueError("column must be >= 1")

    def to_dict(self) -> dict[str, int]:
        return {
            "line": self.line,
            "column": self.column,
        }


@dataclass(frozen=True)
class Span:
    start: Position
    end: Position

    def __post_init__(self) -> None:
        if self.end < self.start:
            raise ValueError("span end must not precede span start")

    @classmethod
    def from_bounds(
        cls,
        start_line: int,
        start_column: int,
        end_line: int,
        end_column: int,
    ) -> "Span":
        return cls(
            start=Position(start_line, start_column),
            end=Position(end_line, end_column),
        )

    def to_location(self, file: str) -> "Location":
        return Location(file=file, start=self.start, end=self.end)


@dataclass(frozen=True)
class Location:
    file: str
    start: Position
    end: Position

    @classmethod
    def from_span(cls, file: str, span: Span) -> "Location":
        return span.to_location(file)

    def to_dict(self) -> dict[str, object]:
        return {
            "file": self.file,
            "start": self.start.to_dict(),
            "end": self.end.to_dict(),
        }


@dataclass(frozen=True)
class RelatedLocation:
    message: str
    location: Location

    @classmethod
    def from_span(cls, message: str, file: str, span: Span) -> "RelatedLocation":
        return cls(message=message, location=Location.from_span(file, span))

    def to_dict(self) -> dict[str, object]:
        return {
            "message": self.message,
            "location": self.location.to_dict(),
        }


@dataclass(frozen=True)
class Diagnostic:
    level: str
    code: str
    message: str
    location: Location
    notes: tuple[str, ...] = field(default_factory=tuple)
    help: str | None = None
    related: tuple[RelatedLocation, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if self.level not in _LEVELS:
            raise ValueError(f"unsupported diagnostic level: {self.level}")
        if not _CODE_PATTERN.match(self.code):
            raise ValueError(f"unsupported diagnostic code: {self.code}")

    def to_dict(self) -> dict[str, object]:
        payload: dict[str, object] = {
            "level": self.level,
            "code": self.code,
            "message": self.message,
            "location": self.location.to_dict(),
        }
        if self.notes:
            payload["notes"] = list(self.notes)
        if self.help is not None:
            payload["help"] = self.help
        if self.related:
            payload["related"] = [item.to_dict() for item in self.related]
        return payload


@dataclass(frozen=True)
class DiagnosticReport:
    diagnostics: tuple[Diagnostic, ...]
    schema_version: str = DEFAULT_SCHEMA_VERSION

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "diagnostics": [diagnostic.to_dict() for diagnostic in self.diagnostics],
        }

    def to_json(self, *, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent) + "\n"
