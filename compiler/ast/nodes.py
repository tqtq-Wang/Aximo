from __future__ import annotations


def _with_optional(base: dict, **optional: object) -> dict:
    for key, value in optional.items():
        if value is not None:
            base[key] = value
    return base


def program(module: dict, uses: list[dict], declarations: list[dict]) -> dict:
    return {
        "kind": "Program",
        "module": module,
        "uses": uses,
        "declarations": declarations,
    }


def module_decl(path: str) -> dict:
    return {
        "kind": "ModuleDecl",
        "path": path,
    }


def use_decl(path: str, imports: list[str] | None = None) -> dict:
    return _with_optional(
        {
            "kind": "UseDecl",
            "path": path,
        },
        imports=imports or None,
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


def field_decl(name: str, type_expr: dict, visibility: str = "private") -> dict:
    return {
        "visibility": visibility,
        "name": name,
        "type": type_expr,
    }


def variant_decl(name: str, fields: list[dict] | None = None) -> dict:
    return _with_optional({"name": name}, fields=fields or None)


def type_parameter(name: str, constraint: str | None = None) -> dict:
    return _with_optional({"name": name}, constraint=constraint)


def parameter(name: str, type_expr: dict) -> dict:
    return {
        "name": name,
        "type": type_expr,
    }


def struct_decl(name: str, fields: list[dict], visibility: str = "private") -> dict:
    return {
        "kind": "StructDecl",
        "visibility": visibility,
        "name": name,
        "fields": fields,
    }


def enum_decl(name: str, variants: list[dict], visibility: str = "private") -> dict:
    return {
        "kind": "EnumDecl",
        "visibility": visibility,
        "name": name,
        "variants": variants,
    }


def newtype_decl(name: str, target: dict, visibility: str = "private") -> dict:
    return {
        "kind": "NewtypeDecl",
        "visibility": visibility,
        "name": name,
        "target": target,
    }


def function_decl(
    name: str,
    parameters: list[dict],
    return_type: dict,
    effects: list[str],
    async_flag: bool,
    body: dict,
    visibility: str = "private",
    type_parameters: list[dict] | None = None,
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
) -> dict:
    return _with_optional(
        {
            "kind": "TraitDecl",
            "visibility": visibility,
            "name": name,
            "members": members,
        },
        typeParameters=type_parameters or None,
    )


def impl_decl(trait: str, for_type: str, members: list[dict]) -> dict:
    return {
        "kind": "ImplDecl",
        "trait": trait,
        "forType": for_type,
        "members": members,
    }


def test_decl(name: str, body: dict) -> dict:
    return {
        "kind": "TestDecl",
        "name": name,
        "body": body,
    }


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
