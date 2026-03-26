from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, order=True)
class Position:
    line: int
    column: int

    def __post_init__(self) -> None:
        if self.line < 1:
            raise ValueError("line must be >= 1")
        if self.column < 1:
            raise ValueError("column must be >= 1")


@dataclass(frozen=True)
class Span:
    start: Position
    end: Position

    def __post_init__(self) -> None:
        if self.end < self.start:
            raise ValueError("span end must not precede span start")


@dataclass(frozen=True)
class ParserError(ValueError):
    code: str
    message: str
    help: str | None
    file_path: str
    span: Span

    @property
    def normalized_file_path(self) -> str:
        return self.file_path.replace("\\", "/")

    def __str__(self) -> str:
        return (
            f"{self.normalized_file_path}:{self.span.start.line}:{self.span.start.column}-"
            f"{self.span.end.line}:{self.span.end.column}: {self.message}"
        )


@dataclass(frozen=True)
class ParseResult:
    file_path: str
    program: dict | None = None
    error: ParserError | None = None

    @property
    def ok(self) -> bool:
        return self.error is None
