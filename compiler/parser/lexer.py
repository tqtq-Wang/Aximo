from __future__ import annotations

from dataclasses import dataclass


KEYWORDS = {
    "async",
    "await",
    "else",
    "effects",
    "enum",
    "false",
    "fn",
    "for",
    "if",
    "impl",
    "internal",
    "let",
    "match",
    "module",
    "newtype",
    "pub",
    "return",
    "struct",
    "test",
    "trait",
    "true",
    "use",
    "var",
}


SINGLE_CHAR_TOKENS = {
    "{": "LBRACE",
    "}": "RBRACE",
    "(": "LPAREN",
    ")": "RPAREN",
    "[": "LBRACKET",
    "]": "RBRACKET",
    ",": "COMMA",
    ".": "DOT",
    ":": "COLON",
    "<": "LT",
    ">": "GT",
    "=": "EQUALS",
    "+": "PLUS",
    "?": "QUESTION",
    ";": "SEMICOLON",
}


@dataclass(frozen=True)
class Token:
    kind: str
    value: str
    line: int
    column: int
    start: int
    end: int


class LexerError(ValueError):
    pass


class Lexer:
    def __init__(self, source: str) -> None:
        self.source = source
        self.length = len(source)
        self.index = 0
        self.line = 1
        self.column = 1

    def tokenize(self) -> list[Token]:
        tokens: list[Token] = []
        while self.index < self.length:
            char = self.source[self.index]
            if char in " \t\r":
                self._advance()
                continue
            if char == "\n":
                start = self.index
                line = self.line
                column = self.column
                self._advance()
                tokens.append(Token("NEWLINE", "\n", line, column, start, self.index))
                continue
            if char == "/" and self._peek(1) == "/":
                self._skip_comment()
                continue
            if char == '"':
                tokens.append(self._read_string())
                continue
            if char.isalpha() or char == "_":
                tokens.append(self._read_identifier())
                continue
            two_char = char + self._peek(1)
            if two_char == "->":
                tokens.append(self._make_token("ARROW", two_char, self.index, self.index + 2))
                self._advance(2)
                continue
            if two_char == "=>":
                tokens.append(self._make_token("FAT_ARROW", two_char, self.index, self.index + 2))
                self._advance(2)
                continue
            if two_char == "::":
                tokens.append(self._make_token("DOUBLE_COLON", two_char, self.index, self.index + 2))
                self._advance(2)
                continue
            if two_char == "==":
                tokens.append(self._make_token("DOUBLE_EQUALS", two_char, self.index, self.index + 2))
                self._advance(2)
                continue
            token_kind = SINGLE_CHAR_TOKENS.get(char)
            if token_kind is not None:
                tokens.append(self._make_token(token_kind, char, self.index, self.index + 1))
                self._advance()
                continue
            raise LexerError(f"Unexpected character {char!r} at {self.line}:{self.column}")
        tokens.append(Token("EOF", "", self.line, self.column, self.length, self.length))
        return tokens

    def _skip_comment(self) -> None:
        while self.index < self.length and self.source[self.index] != "\n":
            self._advance()

    def _read_identifier(self) -> Token:
        start = self.index
        line = self.line
        column = self.column
        while self.index < self.length:
            char = self.source[self.index]
            if not (char.isalnum() or char == "_"):
                break
            self._advance()
        value = self.source[start:self.index]
        kind = value.upper() if value in KEYWORDS else "IDENTIFIER"
        return Token(kind=kind, value=value, line=line, column=column, start=start, end=self.index)

    def _read_string(self) -> Token:
        start = self.index
        line = self.line
        column = self.column
        self._advance()
        value_chars: list[str] = []
        while self.index < self.length:
            char = self.source[self.index]
            if char == '"':
                self._advance()
                return Token("STRING", "".join(value_chars), line, column, start, self.index)
            if char == "\\":
                escape = self._peek(1)
                if escape == "":
                    break
                value_chars.append(
                    {
                        '"': '"',
                        "\\": "\\",
                        "n": "\n",
                        "r": "\r",
                        "t": "\t",
                    }.get(escape, escape)
                )
                self._advance(2)
                continue
            value_chars.append(char)
            self._advance()
        raise LexerError(f"Unterminated string literal at {line}:{column}")

    def _peek(self, offset: int) -> str:
        target = self.index + offset
        if target >= self.length:
            return ""
        return self.source[target]

    def _make_token(self, kind: str, value: str, start: int, end: int) -> Token:
        return Token(kind, value, self.line, self.column, start, end)

    def _advance(self, amount: int = 1) -> None:
        for _ in range(amount):
            if self.index >= self.length:
                return
            char = self.source[self.index]
            self.index += 1
            if char == "\n":
                self.line += 1
                self.column = 1
            else:
                self.column += 1
