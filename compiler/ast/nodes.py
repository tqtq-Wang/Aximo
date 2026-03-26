from __future__ import annotations


def _with_optional(base: dict, **optional: object) -> dict:
    for key, value in optional.items():
        if value is not None:
            base[key] = value
    return base


def position(line: int, column: int) -> dict:
    return {
        "line": line,
        "column": column,
    }


def span(file: str, start: dict, end: dict) -> dict:
    return {
        "file": file,
        "start": start,
        "end": end,
    }


def program(module: dict, uses: list[dict], declarations: list[dict]) -> dict:
    return {
        "kind": "Program",
        "module": module,
        "uses": uses,
        "declarations": declarations,
    }


def module_decl(path: str, span: dict | None = None) -> dict:
    return _with_optional(
        {
            "kind": "ModuleDecl",
            "path": path,
        },
        span=span,
    )


def use_decl(path: str, imports: list[str] | None = None, span: dict | None = None) -> dict:
    return _with_optional(
        {
            "kind": "UseDecl",
            "path": path,
        },
        imports=imports or None,
        span=span,
    )


def named_type(name: str) -> dict:
    return {
        "kind": "NamedType",
        "name": name,
    }


def generic_type(name: str, arguments: list[dict]) -> dict:
    return {
        "kind": "GenericType",
        "name": name,
        "arguments": arguments,
    }


def result_type(ok: dict, err: dict) -> dict:
    return {
        "kind": "ResultType",
        "ok": ok,
        "err": err,
    }


def option_type(item: dict) -> dict:
    return {
        "kind": "OptionType",
        "item": item,
    }


def unit_type() -> dict:
    return {
        "kind": "UnitType",
    }


def field_decl(
    name: str,
    type_expr: dict,
    visibility: str = "private",
    span: dict | None = None,
) -> dict:
    return _with_optional(
        {
            "visibility": visibility,
            "name": name,
            "type": type_expr,
        },
        span=span,
    )


def variant_decl(name: str, fields: list[dict] | None = None, span: dict | None = None) -> dict:
    return _with_optional({"name": name}, fields=fields or None, span=span)


def type_parameter(name: str, constraint: str | None = None) -> dict:
    return _with_optional({"name": name}, constraint=constraint)


def parameter(name: str, type_expr: dict, span: dict | None = None) -> dict:
    return _with_optional(
        {
            "name": name,
            "type": type_expr,
        },
        span=span,
    )


def struct_decl(
    name: str,
    fields: list[dict],
    visibility: str = "private",
    span: dict | None = None,
) -> dict:
    return _with_optional(
        {
            "kind": "StructDecl",
            "visibility": visibility,
            "name": name,
            "fields": fields,
        },
        span=span,
    )


def enum_decl(
    name: str,
    variants: list[dict],
    visibility: str = "private",
    span: dict | None = None,
) -> dict:
    return _with_optional(
        {
            "kind": "EnumDecl",
            "visibility": visibility,
            "name": name,
            "variants": variants,
        },
        span=span,
    )


def newtype_decl(
    name: str,
    target: dict,
    visibility: str = "private",
    span: dict | None = None,
) -> dict:
    return _with_optional(
        {
            "kind": "NewtypeDecl",
            "visibility": visibility,
            "name": name,
            "target": target,
        },
        span=span,
    )


def function_decl(
    name: str,
    parameters: list[dict],
    return_type: dict,
    effects: list[str],
    async_flag: bool,
    body: dict,
    visibility: str = "private",
    type_parameters: list[dict] | None = None,
    span: dict | None = None,
) -> dict:
    return _with_optional(
        {
            "kind": "FunctionDecl",
            "visibility": visibility,
            "name": name,
            "parameters": parameters,
            "returnType": return_type,
            "effects": effects,
            "async": async_flag,
            "body": body,
        },
        typeParameters=type_parameters or None,
        span=span,
    )


def trait_member(
    name: str,
    parameters: list[dict],
    return_type: dict,
    effects: list[str],
) -> dict:
    return {
        "name": name,
        "parameters": parameters,
        "returnType": return_type,
        "effects": effects,
    }


def trait_decl(
    name: str,
    members: list[dict],
    visibility: str = "private",
    type_parameters: list[dict] | None = None,
    span: dict | None = None,
) -> dict:
    return _with_optional(
        {
            "kind": "TraitDecl",
            "visibility": visibility,
            "name": name,
            "members": members,
        },
        typeParameters=type_parameters or None,
        span=span,
    )


def impl_decl(trait: str, for_type: str, members: list[dict], span: dict | None = None) -> dict:
    return _with_optional(
        {
            "kind": "ImplDecl",
            "trait": trait,
            "forType": for_type,
            "members": members,
        },
        span=span,
    )


def test_decl(name: str, body: dict, span: dict | None = None) -> dict:
    return _with_optional(
        {
            "kind": "TestDecl",
            "name": name,
            "body": body,
        },
        span=span,
    )


def block(statements: list[dict]) -> dict:
    return {
        "kind": "Block",
        "statements": statements,
    }


def let_stmt(name: str, value: dict) -> dict:
    return {
        "kind": "LetStmt",
        "name": name,
        "value": value,
    }


def var_stmt(name: str, value: dict) -> dict:
    return {
        "kind": "VarStmt",
        "name": name,
        "value": value,
    }


def return_stmt(value: dict) -> dict:
    return {
        "kind": "ReturnStmt",
        "value": value,
    }


def expr_stmt(expression: dict) -> dict:
    return {
        "kind": "ExprStmt",
        "expression": expression,
    }


def if_stmt(condition: dict, then_block: dict, else_block: dict | None = None) -> dict:
    return _with_optional(
        {
            "kind": "IfStmt",
            "condition": condition,
            "thenBlock": then_block,
        },
        elseBlock=else_block,
    )


def identifier_expr(name: str) -> dict:
    return {
        "kind": "IdentifierExpr",
        "name": name,
    }


def string_literal_expr(value: str) -> dict:
    return {
        "kind": "StringLiteralExpr",
        "value": value,
    }


def bool_literal_expr(value: bool) -> dict:
    return {
        "kind": "BoolLiteralExpr",
        "value": value,
    }


def call_expr(
    callee: str,
    arguments: list[dict],
    await_flag: bool = False,
    propagate_error: bool = False,
) -> dict:
    node = {
        "kind": "CallExpr",
        "callee": callee,
        "arguments": arguments,
    }
    if await_flag:
        node["await"] = True
    if propagate_error:
        node["propagateError"] = True
    return node


def match_expr(subject: dict, arms: list[dict]) -> dict:
    return {
        "kind": "MatchExpr",
        "subject": subject,
        "arms": arms,
    }


def match_arm(pattern: str, body: dict) -> dict:
    return {
        "pattern": pattern,
        "body": body,
    }
