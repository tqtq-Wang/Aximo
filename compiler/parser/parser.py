from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re

from compiler import ast

from .lexer import Lexer, LexerError, Token
from .types import ParseResult, ParserError, Position, Span


@dataclass
class Parser:
    source: str
    file_path: str = "<memory>"

    def __post_init__(self) -> None:
        try:
            self.tokens = Lexer(self.source).tokenize()
        except LexerError as error:
            raise ParserError(
                error.code,
                error.message,
                error.help,
                self.file_path,
                error.span,
            ) from error
        self.index = 0
        self.function_contexts: list[dict[str, object]] = []

    @property
    def normalized_file_path(self) -> str:
        return self.file_path.replace("\\", "/")

    @property
    def current(self) -> Token:
        return self.tokens[self.index]

    def peek(self, offset: int = 1) -> Token:
        target = self.index + offset
        if target >= len(self.tokens):
            return self.tokens[-1]
        return self.tokens[target]

    def advance(self) -> Token:
        token = self.current
        if self.current.kind != "EOF":
            self.index += 1
        return token

    def match(self, *kinds: str) -> Token | None:
        if self.current.kind in kinds:
            return self.advance()
        return None

    def expect(self, kind: str, message: str) -> Token:
        token = self.match(kind)
        if token is None:
            raise self.error(message)
        return token

    def token_end_position(self, token: Token) -> Position:
        if token.end <= token.start:
            return Position(token.line, token.column)
        line = token.line
        column = token.column
        for char in self.source[token.start:token.end]:
            if char == "\n":
                line += 1
                column = 1
            else:
                column += 1
        return Position(line, max(column - 1, 1))

    def token_start_position(self, token: Token) -> Position:
        return Position(token.line, token.column)

    def make_error(
        self,
        code: str,
        message: str,
        help_text: str | None,
        start: Position,
        end: Position,
    ) -> ParserError:
        return ParserError(code, message, help_text, self.file_path, Span(start, end))

    def generic_error(
        self,
        message: str,
        start: Position,
        end: Position,
        help_text: str | None = None,
    ) -> ParserError:
        return self.make_error("P999", message, help_text, start, end)

    def error(
        self,
        message: str,
        token: Token | None = None,
        end_token: Token | None = None,
    ) -> ParserError:
        target = token or self.current
        return self.generic_error(
            message,
            self.token_start_position(target),
            self.token_end_position(end_token or target),
        )

    def current_index(self) -> int:
        if self.index >= len(self.tokens):
            return len(self.tokens) - 1
        return self.index

    def consumed_end_index(self, start_index: int) -> int:
        return max(self.index - 1, start_index)

    def schema_position(self, position: Position) -> dict:
        return ast.position(position.line, position.column)

    def schema_span(self, start: Position, end: Position) -> dict:
        return ast.span(
            self.normalized_file_path,
            self.schema_position(start),
            self.schema_position(end),
        )

    def span_from_token_indexes(
        self,
        start_index: int,
        end_index: int | None = None,
    ) -> dict:
        start_token = self.tokens[start_index]
        end_token = self.tokens[
            self.consumed_end_index(start_index) if end_index is None else end_index
        ]
        return self.schema_span(
            self.token_start_position(start_token),
            self.token_end_position(end_token),
        )

    def consume_separators(self) -> None:
        while self.current.kind in {"NEWLINE", "SEMICOLON"}:
            self.advance()

    def parse_program(self) -> dict:
        self.consume_separators()
        if self.current.kind != "MODULE":
            first_token = self.current
            raise self.make_error(
                "P001",
                "missing module declaration at start of file",
                "add a `module ...` declaration before any imports or declarations",
                self.token_start_position(first_token),
                self.token_end_position(first_token),
            )
        module = self.parse_module_decl()
        uses: list[dict] = []
        declarations: list[dict] = []
        self.consume_separators()
        while self.current.kind == "USE":
            uses.append(self.parse_use_decl())
            self.consume_separators()
        while self.current.kind != "EOF":
            self.consume_separators()
            if self.current.kind == "EOF":
                break
            declarations.append(self.parse_declaration())
            self.consume_separators()
        return ast.program(module, uses, declarations)

    def parse_module_decl(self) -> dict:
        start_index = self.current_index()
        self.expect("MODULE", "Expected 'module'")
        path = self.parse_qualified_name()
        return ast.module_decl(path, span=self.span_from_token_indexes(start_index))

    def parse_use_decl(self) -> dict:
        start_index = self.current_index()
        self.expect("USE", "Expected 'use'")
        path_parts = [self.expect("IDENTIFIER", "Expected import path segment").value]
        while self.current.kind == "DOT" and self.peek().kind == "IDENTIFIER":
            self.advance()
            path_parts.append(self.advance().value)
        imports: list[str] | None = None
        if self.current.kind == "DOT" and self.peek().kind == "LBRACE":
            self.advance()
            self.advance()
            imports = self.parse_identifier_list("RBRACE", "Expected imported name")
            self.expect("RBRACE", "Expected '}' after import list")
        return ast.use_decl(
            ".".join(path_parts),
            imports,
            span=self.span_from_token_indexes(start_index),
        )

    def parse_declaration(self) -> dict:
        visibility = self.parse_visibility()
        async_flag = self.match("ASYNC") is not None
        if self.current.kind == "STRUCT":
            if async_flag:
                raise self.error("'async' is only valid on functions")
            return self.parse_struct_decl(visibility)
        if self.current.kind == "ENUM":
            if async_flag:
                raise self.error("'async' is only valid on functions")
            return self.parse_enum_decl(visibility)
        if self.current.kind == "NEWTYPE":
            if async_flag:
                raise self.error("'async' is only valid on functions")
            return self.parse_newtype_decl(visibility)
        if self.current.kind == "TRAIT":
            if async_flag:
                raise self.error("'async' is only valid on functions")
            return self.parse_trait_decl(visibility)
        if self.current.kind == "IMPL":
            if visibility != "private":
                raise self.error("'impl' does not support explicit visibility")
            if async_flag:
                raise self.error("'async' is only valid on functions")
            return self.parse_impl_decl()
        if self.current.kind == "TEST":
            if visibility != "private":
                raise self.error("'test' does not support explicit visibility")
            if async_flag:
                raise self.error("'async' is only valid on functions")
            return self.parse_test_decl()
        if self.current.kind == "FN":
            return self.parse_function_decl(visibility, async_flag)
        if async_flag:
            raise self.error("Expected 'fn' after 'async'")
        raise self.error("Unsupported or unexpected declaration")

    def parse_visibility(self) -> str:
        if self.match("PUB"):
            return "pub"
        if self.match("INTERNAL"):
            return "internal"
        return "private"

    def parse_struct_decl(self, visibility: str) -> dict:
        start_index = self.current_index()
        self.expect("STRUCT", "Expected 'struct'")
        name = self.expect("IDENTIFIER", "Expected struct name").value
        self.expect("LBRACE", "Expected '{' after struct name")
        fields: list[dict] = []
        self.consume_separators()
        while self.current.kind != "RBRACE":
            fields.append(self.parse_field_decl())
            self.consume_separators()
            self.match("COMMA")
            self.consume_separators()
        self.expect("RBRACE", "Expected '}' after struct fields")
        return ast.struct_decl(
            name,
            fields,
            visibility,
            span=self.span_from_token_indexes(start_index),
        )

    def parse_field_decl(self) -> dict:
        start_index = self.current_index()
        visibility = self.parse_visibility()
        name = self.expect("IDENTIFIER", "Expected field name").value
        self.expect("COLON", "Expected ':' after field name")
        return ast.field_decl(
            name,
            self.parse_type_expr(),
            visibility,
            span=self.span_from_token_indexes(start_index),
        )

    def parse_enum_decl(self, visibility: str) -> dict:
        start_index = self.current_index()
        self.expect("ENUM", "Expected 'enum'")
        name = self.expect("IDENTIFIER", "Expected enum name").value
        self.expect("LBRACE", "Expected '{' after enum name")
        variants: list[dict] = []
        self.consume_separators()
        while self.current.kind != "RBRACE":
            variants.append(self.parse_variant_decl())
            self.consume_separators()
            self.match("COMMA")
            self.consume_separators()
        self.expect("RBRACE", "Expected '}' after enum variants")
        return ast.enum_decl(
            name,
            variants,
            visibility,
            span=self.span_from_token_indexes(start_index),
        )

    def parse_newtype_decl(self, visibility: str) -> dict:
        start_index = self.current_index()
        self.expect("NEWTYPE", "Expected 'newtype'")
        name = self.expect("IDENTIFIER", "Expected newtype name").value
        self.expect("EQUALS", "Expected '=' after newtype name")
        target = self.parse_type_expr()
        return ast.newtype_decl(
            name,
            target,
            visibility,
            span=self.span_from_token_indexes(start_index),
        )

    def parse_variant_decl(self) -> dict:
        start_index = self.current_index()
        name = self.expect("IDENTIFIER", "Expected enum variant name").value
        fields: list[dict] = []
        if self.match("LPAREN"):
            self.consume_separators()
            while self.current.kind != "RPAREN":
                fields.append(self.parse_type_expr())
                self.consume_separators()
                if not self.match("COMMA"):
                    break
                self.consume_separators()
            self.expect("RPAREN", "Expected ')' after enum variant fields")
        return ast.variant_decl(
            name,
            fields or None,
            span=self.span_from_token_indexes(start_index),
        )

    def parse_function_decl(self, visibility: str, async_flag: bool) -> dict:
        start_index = self.current_index()
        self.expect("FN", "Expected 'fn'")
        name = self.expect("IDENTIFIER", "Expected function name").value
        type_parameters = self.parse_type_parameters()
        self.expect("LPAREN", "Expected '(' after function name")
        parameters = self.parse_parameters()
        self.expect("RPAREN", "Expected ')' after function parameters")
        self.expect("ARROW", "Expected '->' before function return type")
        return_type = self.parse_type_expr()
        self.consume_separators()
        effects: list[str] = []
        if self.current.kind == "EFFECTS":
            effects = self.parse_effects_clause()
            self.consume_separators()
        self.function_contexts.append({"name": name, "effects": effects})
        try:
            body = self.parse_block()
        finally:
            self.function_contexts.pop()
        return ast.function_decl(
            name=name,
            parameters=parameters,
            return_type=return_type,
            effects=effects,
            async_flag=async_flag,
            body=body,
            visibility=visibility,
            type_parameters=type_parameters or None,
            span=self.span_from_token_indexes(start_index),
        )

    def parse_trait_decl(self, visibility: str) -> dict:
        start_index = self.current_index()
        self.expect("TRAIT", "Expected 'trait'")
        name = self.expect("IDENTIFIER", "Expected trait name").value
        type_parameters = self.parse_type_parameters()
        self.expect("LBRACE", "Expected '{' after trait name")
        members: list[dict] = []
        self.consume_separators()
        while self.current.kind != "RBRACE":
            members.append(self.parse_trait_member())
            self.consume_separators()
        self.expect("RBRACE", "Expected '}' after trait body")
        return ast.trait_decl(
            name,
            members,
            visibility,
            type_parameters or None,
            span=self.span_from_token_indexes(start_index),
        )

    def parse_trait_member(self) -> dict:
        self.expect("FN", "Expected 'fn' in trait body")
        name = self.expect("IDENTIFIER", "Expected trait member name").value
        if self.current.kind == "LT":
            raise self.error("Trait members do not support type parameters in current schema")
        self.expect("LPAREN", "Expected '(' after trait member name")
        parameters = self.parse_parameters()
        self.expect("RPAREN", "Expected ')' after trait member parameters")
        self.expect("ARROW", "Expected '->' before trait member return type")
        return_type = self.parse_type_expr()
        self.consume_separators()
        effects: list[str] = []
        if self.current.kind == "EFFECTS":
            effects = self.parse_effects_clause()
        return ast.trait_member(name, parameters, return_type, effects)

    def parse_impl_decl(self) -> dict:
        start_index = self.current_index()
        self.expect("IMPL", "Expected 'impl'")
        trait_name = self.parse_name_like()
        self.expect("FOR", "Expected 'for' in impl declaration")
        for_type = self.parse_name_like()
        self.expect("LBRACE", "Expected '{' after impl header")
        members: list[dict] = []
        self.consume_separators()
        while self.current.kind != "RBRACE":
            member_visibility = self.parse_visibility()
            async_flag = self.match("ASYNC") is not None
            if self.current.kind != "FN":
                raise self.error("Only functions are allowed inside impl blocks")
            members.append(self.parse_function_decl(member_visibility, async_flag))
            self.consume_separators()
        self.expect("RBRACE", "Expected '}' after impl body")
        return ast.impl_decl(
            trait_name,
            for_type,
            members,
            span=self.span_from_token_indexes(start_index),
        )

    def parse_test_decl(self) -> dict:
        start_index = self.current_index()
        self.expect("TEST", "Expected 'test'")
        name = self.expect("STRING", "Expected test name string").value
        body = self.parse_block()
        return ast.test_decl(name, body, span=self.span_from_token_indexes(start_index))

    def parse_type_parameters(self) -> list[dict]:
        if not self.match("LT"):
            return []
        parameters: list[dict] = []
        self.consume_separators()
        while self.current.kind != "GT":
            name = self.expect("IDENTIFIER", "Expected type parameter name").value
            constraint = None
            if self.match("COLON"):
                constraint = self.parse_qualified_name()
            parameters.append(ast.type_parameter(name, constraint))
            self.consume_separators()
            if not self.match("COMMA"):
                break
            self.consume_separators()
        self.expect("GT", "Expected '>' after type parameters")
        return parameters

    def parse_parameters(self) -> list[dict]:
        parameters: list[dict] = []
        self.consume_separators()
        while self.current.kind != "RPAREN":
            start_index = self.current_index()
            name = self.expect("IDENTIFIER", "Expected parameter name").value
            self.expect("COLON", "Expected ':' after parameter name")
            parameters.append(
                ast.parameter(
                    name,
                    self.parse_type_expr(),
                    span=self.span_from_token_indexes(start_index),
                )
            )
            self.consume_separators()
            if not self.match("COMMA"):
                break
            self.consume_separators()
        return parameters

    def parse_effects_clause(self) -> list[str]:
        self.expect("EFFECTS", "Expected 'effects'")
        self.expect("LBRACKET", "Expected '[' after 'effects'")
        effects: list[str] = []
        self.consume_separators()
        while self.current.kind != "RBRACKET":
            effects.append(self.parse_qualified_name())
            self.consume_separators()
            if not self.match("COMMA"):
                break
            self.consume_separators()
        self.expect("RBRACKET", "Expected ']' after effect list")
        return effects

    def parse_type_expr(self) -> dict:
        self.consume_separators()
        name = self.parse_name_like()
        self.consume_separators()
        if name == "Unit":
            return ast.unit_type()
        if self.match("LT"):
            arguments: list[dict] = []
            self.consume_separators()
            while self.current.kind != "GT":
                arguments.append(self.parse_type_expr())
                self.consume_separators()
                if not self.match("COMMA"):
                    break
                self.consume_separators()
            self.expect("GT", "Expected '>' after generic type arguments")
            if name == "Result":
                if len(arguments) != 2:
                    raise self.error("Result type expects exactly two type arguments")
                return ast.result_type(arguments[0], arguments[1])
            if name == "Option":
                if len(arguments) != 1:
                    raise self.error("Option type expects exactly one type argument")
                return ast.option_type(arguments[0])
            if "." in name:
                raise self.error("Generic type names must be unqualified identifiers")
            return ast.generic_type(name, arguments)
        return ast.named_type(name)

    def parse_block(self) -> dict:
        self.expect("LBRACE", "Expected '{' to start block")
        statements: list[dict] = []
        self.consume_separators()
        while self.current.kind != "RBRACE":
            statements.append(self.parse_statement())
            self.consume_separators()
        self.expect("RBRACE", "Expected '}' to close block")
        return ast.block(statements)

    def parse_statement(self) -> dict:
        if self.current.kind == "LET":
            self.advance()
            name = self.expect("IDENTIFIER", "Expected binding name").value
            self.expect("EQUALS", "Expected '=' in let binding")
            expression_tokens = self.collect_statement_expression()
            expression = self.parse_expression_tokens(expression_tokens)
            self.validate_effect_usage(expression, expression_tokens)
            return ast.let_stmt(name, expression)
        if self.current.kind == "VAR":
            self.advance()
            name = self.expect("IDENTIFIER", "Expected binding name").value
            self.expect("EQUALS", "Expected '=' in var binding")
            expression_tokens = self.collect_statement_expression()
            expression = self.parse_expression_tokens(expression_tokens)
            self.validate_effect_usage(expression, expression_tokens)
            return ast.var_stmt(name, expression)
        if self.current.kind == "RETURN":
            self.advance()
            expression_tokens = self.collect_statement_expression()
            expression = self.parse_expression_tokens(expression_tokens)
            self.validate_effect_usage(expression, expression_tokens)
            return ast.return_stmt(expression)
        if self.current.kind == "IF":
            self.advance()
            condition_tokens = self.collect_until_block_start()
            condition = self.parse_expression_tokens(condition_tokens)
            self.validate_effect_usage(condition, condition_tokens)
            then_block = self.parse_block()
            self.consume_separators()
            else_block = None
            if self.match("ELSE"):
                self.consume_separators()
                else_block = self.parse_block()
            return ast.if_stmt(condition, then_block, else_block)
        expression_tokens = self.collect_statement_expression()
        expression = self.parse_expression_tokens(expression_tokens)
        self.validate_effect_usage(expression, expression_tokens)
        return ast.expr_stmt(expression)

    def collect_until_block_start(self) -> list[Token]:
        tokens: list[Token] = []
        paren_depth = 0
        bracket_depth = 0
        while True:
            token = self.current
            if token.kind == "EOF":
                raise self.error("Unexpected end of file while reading condition")
            if token.kind == "LBRACE" and paren_depth == 0 and bracket_depth == 0:
                break
            if token.kind == "LPAREN":
                paren_depth += 1
            elif token.kind == "RPAREN":
                paren_depth = max(paren_depth - 1, 0)
            elif token.kind == "LBRACKET":
                bracket_depth += 1
            elif token.kind == "RBRACKET":
                bracket_depth = max(bracket_depth - 1, 0)
            tokens.append(self.advance())
        return tokens

    def collect_statement_expression(self) -> list[Token]:
        tokens: list[Token] = []
        paren_depth = 0
        bracket_depth = 0
        brace_depth = 0
        while True:
            token = self.current
            if token.kind == "EOF":
                break
            if token.kind in {"NEWLINE", "SEMICOLON"} and paren_depth == bracket_depth == brace_depth == 0:
                if token.kind == "NEWLINE" and self.peek_non_separator().kind == "DOT":
                    tokens.append(self.advance())
                    continue
                break
            if token.kind == "RBRACE" and paren_depth == bracket_depth == brace_depth == 0:
                break
            if token.kind == "LPAREN":
                paren_depth += 1
            elif token.kind == "RPAREN":
                paren_depth = max(paren_depth - 1, 0)
            elif token.kind == "LBRACKET":
                bracket_depth += 1
            elif token.kind == "RBRACKET":
                bracket_depth = max(bracket_depth - 1, 0)
            elif token.kind == "LBRACE":
                brace_depth += 1
            elif token.kind == "RBRACE":
                brace_depth = max(brace_depth - 1, 0)
            tokens.append(self.advance())
        return tokens

    def parse_expression_tokens(self, tokens: list[Token]) -> dict:
        filtered = self.trim_expression_tokens(tokens)
        if not filtered:
            return ast.identifier_expr("")
        if filtered[0].kind == "MATCH":
            return self.parse_match_expression(filtered)
        for operator_kind, callee in (("DOUBLE_EQUALS", "=="), ("PLUS", "+")):
            split_index = self.find_top_level_operator(filtered, operator_kind)
            if split_index is not None:
                left = self.parse_expression_tokens(filtered[:split_index])
                right = self.parse_expression_tokens(filtered[split_index + 1 :])
                return ast.call_expr(callee, [left, right])
        await_flag = False
        propagate_error = False
        if filtered and filtered[0].kind == "AWAIT":
            await_flag = True
            filtered = self.trim_expression_tokens(filtered[1:])
        if filtered and filtered[-1].kind == "QUESTION":
            propagate_error = True
            filtered = self.trim_expression_tokens(filtered[:-1])
        if len(filtered) == 2 and filtered[0].kind == "LPAREN" and filtered[1].kind == "RPAREN":
            return ast.identifier_expr("()")
        if len(filtered) == 1 and filtered[0].kind == "STRING":
            return ast.string_literal_expr(filtered[0].value)
        if len(filtered) == 1 and filtered[0].kind in {"TRUE", "FALSE"}:
            return ast.bool_literal_expr(filtered[0].kind == "TRUE")
        call_bounds = self.find_call_bounds(filtered)
        if call_bounds is not None:
            left_index, right_index = call_bounds
            callee = self.compact_source(filtered[:left_index])
            arguments = [
                self.parse_expression_tokens(argument_tokens)
                for argument_tokens in self.split_top_level(filtered[left_index + 1 : right_index], "COMMA")
                if self.trim_expression_tokens(argument_tokens)
            ]
            return ast.call_expr(callee, arguments, await_flag=await_flag, propagate_error=propagate_error)
        if await_flag or propagate_error:
            return ast.call_expr(
                self.compact_source(filtered),
                [],
                await_flag=await_flag,
                propagate_error=propagate_error,
            )
        return ast.identifier_expr(self.compact_source(filtered))

    def parse_match_expression(self, tokens: list[Token]) -> dict:
        brace_index = self.find_first_top_level(tokens[1:], "LBRACE")
        if brace_index is None:
            raise self.error("Match expression requires a body", tokens[0])
        brace_index += 1
        if tokens[-1].kind != "RBRACE":
            raise self.error("Match expression must end with '}'", tokens[-1])
        subject = self.parse_expression_tokens(tokens[1:brace_index])
        arms_tokens = tokens[brace_index + 1 : -1]
        arms: list[dict] = []
        for group in self.split_top_level(arms_tokens, "COMMA"):
            group = self.trim_expression_tokens(group)
            if not group:
                continue
            arrow_index = self.find_top_level_operator(group, "FAT_ARROW")
            if arrow_index is None:
                body_index = 1
                while body_index + 1 < len(group):
                    if group[body_index].kind == "DOUBLE_COLON" and group[body_index + 1].kind == "IDENTIFIER":
                        body_index += 2
                        continue
                    break
                body_start = group[body_index] if body_index < len(group) else group[-1]
                synthetic_end = Position(body_start.line, body_start.column + 1)
                raise self.make_error(
                    "P002",
                    "invalid match arm syntax; expected `=>`",
                    "write each arm as `pattern => expr`",
                    self.token_start_position(body_start),
                    synthetic_end,
                )
            pattern = self.compact_source(group[:arrow_index])
            body = self.parse_expression_tokens(group[arrow_index + 1 :])
            arms.append(ast.match_arm(pattern, body))
        return ast.match_expr(subject, arms)

    def parse_qualified_name(self) -> str:
        token = self.expect("IDENTIFIER", "Expected identifier")
        parts = [token.value]
        while self.current.kind == "DOT":
            self.advance()
            parts.append(self.expect("IDENTIFIER", "Expected identifier after '.'").value)
        return ".".join(parts)

    def parse_name_like(self) -> str:
        token = self.expect("IDENTIFIER", "Expected identifier")
        parts = [token.value]
        while self.current.kind in {"DOT", "DOUBLE_COLON"}:
            separator = self.advance().value
            parts.append(separator)
            parts.append(self.expect("IDENTIFIER", f"Expected identifier after '{separator}'").value)
        return "".join(parts)

    def parse_identifier_list(self, closing_kind: str, error_message: str) -> list[str]:
        items: list[str] = []
        self.consume_separators()
        while self.current.kind != closing_kind:
            items.append(self.expect("IDENTIFIER", error_message).value)
            self.consume_separators()
            if not self.match("COMMA"):
                break
            self.consume_separators()
        return items

    def peek_non_separator(self) -> Token:
        offset = 1
        while True:
            token = self.peek(offset)
            if token.kind not in {"NEWLINE", "SEMICOLON"}:
                return token
            offset += 1

    def trim_expression_tokens(self, tokens: list[Token]) -> list[Token]:
        start = 0
        end = len(tokens)
        while start < end and tokens[start].kind in {"NEWLINE", "SEMICOLON"}:
            start += 1
        while end > start and tokens[end - 1].kind in {"NEWLINE", "SEMICOLON"}:
            end -= 1
        return tokens[start:end]

    def find_top_level_operator(self, tokens: list[Token], operator_kind: str) -> int | None:
        paren_depth = 0
        bracket_depth = 0
        brace_depth = 0
        for index in range(len(tokens) - 1, -1, -1):
            token = tokens[index]
            if token.kind == "RPAREN":
                paren_depth += 1
            elif token.kind == "LPAREN":
                paren_depth -= 1
            elif token.kind == "RBRACKET":
                bracket_depth += 1
            elif token.kind == "LBRACKET":
                bracket_depth -= 1
            elif token.kind == "RBRACE":
                brace_depth += 1
            elif token.kind == "LBRACE":
                brace_depth -= 1
            elif (
                token.kind == operator_kind
                and paren_depth == 0
                and bracket_depth == 0
                and brace_depth == 0
            ):
                return index
        return None

    def find_call_bounds(self, tokens: list[Token]) -> tuple[int, int] | None:
        if not tokens or tokens[-1].kind != "RPAREN":
            return None
        paren_depth = 0
        for index in range(len(tokens) - 1, -1, -1):
            token = tokens[index]
            if token.kind == "RPAREN":
                paren_depth += 1
            elif token.kind == "LPAREN":
                paren_depth -= 1
                if paren_depth == 0:
                    return index, len(tokens) - 1
        return None

    def find_first_top_level(self, tokens: list[Token], target_kind: str) -> int | None:
        paren_depth = 0
        bracket_depth = 0
        for index, token in enumerate(tokens):
            if token.kind == "LPAREN":
                paren_depth += 1
            elif token.kind == "RPAREN":
                paren_depth -= 1
            elif token.kind == "LBRACKET":
                bracket_depth += 1
            elif token.kind == "RBRACKET":
                bracket_depth -= 1
            elif token.kind == target_kind and paren_depth == 0 and bracket_depth == 0:
                return index
        return None

    def split_top_level(self, tokens: list[Token], separator_kind: str) -> list[list[Token]]:
        groups: list[list[Token]] = []
        current: list[Token] = []
        paren_depth = 0
        bracket_depth = 0
        brace_depth = 0
        for token in tokens:
            if token.kind == "LPAREN":
                paren_depth += 1
            elif token.kind == "RPAREN":
                paren_depth -= 1
            elif token.kind == "LBRACKET":
                bracket_depth += 1
            elif token.kind == "RBRACKET":
                bracket_depth -= 1
            elif token.kind == "LBRACE":
                brace_depth += 1
            elif token.kind == "RBRACE":
                brace_depth -= 1
            if (
                token.kind == separator_kind
                and paren_depth == 0
                and bracket_depth == 0
                and brace_depth == 0
            ):
                groups.append(current)
                current = []
                continue
            current.append(token)
        groups.append(current)
        return groups

    def compact_source(self, tokens: list[Token]) -> str:
        if not tokens:
            return ""
        raw = self.source[tokens[0].start : tokens[-1].end]
        compact = re.sub(r"\s+", " ", raw).strip()
        compact = re.sub(r"\s*\.\s*", ".", compact)
        compact = re.sub(r"\s*::\s*", "::", compact)
        return compact

    def expr_contains_undeclared_effect(self, expr: dict) -> bool:
        if expr["kind"] == "CallExpr":
            if expr.get("propagateError") and "." in expr["callee"]:
                return True
            return any(self.expr_contains_undeclared_effect(argument) for argument in expr["arguments"])
        if expr["kind"] == "MatchExpr":
            if self.expr_contains_undeclared_effect(expr["subject"]):
                return True
            return any(self.expr_contains_undeclared_effect(arm["body"]) for arm in expr["arms"])
        return False

    def validate_effect_usage(self, expr: dict, tokens: list[Token]) -> None:
        if not self.function_contexts:
            return
        context = self.function_contexts[-1]
        if context["effects"]:
            return
        if not self.expr_contains_undeclared_effect(expr):
            return
        relevant = self.trim_expression_tokens(tokens)
        if relevant and relevant[-1].kind == "QUESTION":
            relevant = relevant[:-1]
        if not relevant:
            return
        raise self.make_error(
            "E001",
            "effectful operation requires an explicit effects clause",
            "declare the required effect set, for example `effects [db.write]`",
            self.token_start_position(relevant[0]),
            self.token_end_position(relevant[-1]),
        )


def parse_source_result(source: str, file_path: str = "<memory>") -> ParseResult:
    try:
        program = Parser(source=source, file_path=file_path).parse_program()
    except ParserError as error:
        return ParseResult(file_path=file_path, error=error)
    return ParseResult(file_path=file_path, program=program)


def parse_source(source: str, file_path: str = "<memory>") -> dict:
    result = parse_source_result(source, file_path=file_path)
    if result.error is not None:
        raise result.error
    assert result.program is not None
    return result.program


def parse_file_result(path: str | Path) -> ParseResult:
    file_path = Path(path)
    source = file_path.read_text(encoding="utf-8")
    return parse_source_result(source, str(file_path))


def parse_file(path: str | Path) -> dict:
    result = parse_file_result(path)
    if result.error is not None:
        raise result.error
    assert result.program is not None
    return result.program
