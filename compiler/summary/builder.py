from __future__ import annotations

from pathlib import Path
import sys
from typing import Any, Mapping

if __package__ in (None, ""):
    CURRENT_DIR = Path(__file__).resolve().parent
    REPO_ROOT = CURRENT_DIR.parents[1]
    if str(CURRENT_DIR) not in sys.path:
        sys.path.insert(0, str(CURRENT_DIR))
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))
    from contract import (  # type: ignore[no-redef]
        DiagnosticEntry,
        ExportEntry,
        ModuleSummary,
        SourceLocation,
        TypeEntry,
        TypeField,
        TypeVariant,
    )
else:
    from .contract import (
        DiagnosticEntry,
        ExportEntry,
        ModuleSummary,
        SourceLocation,
        TypeEntry,
        TypeField,
        TypeVariant,
    )

_VISIBILITY_MAP = {
    "pub": "public",
    "public": "public",
    "internal": "internal",
    "private": "private",
}
_IGNORED_CALLS = {"", "Ok", "Err", "+", "=="}


def summary_from_source_file(path: str | Path) -> ModuleSummary:
    source_path = Path(path)
    return summary_from_parse_result(
        _parse_source_result(source_path),
        source_path=source_path,
    )


def summary_from_parse_result(
    result: Any,
    *,
    source_path: str | Path | None = None,
) -> ModuleSummary:
    source = None if source_path is None else Path(source_path)
    diagnostics = _diagnostics_from_report(getattr(result, "report", None))
    program = getattr(result, "program", None)
    if not getattr(result, "ok", False) or not isinstance(program, Mapping):
        return ModuleSummary(
            module=_fallback_module_name(source),
            diagnostics=diagnostics,
        )
    return _ProgramSummaryBuilder(program, source, diagnostics).build()


def _parse_source_result(path: Path) -> Any:
    from compiler.parser import parse_file_result

    return parse_file_result(path)


def _fallback_module_name(source_path: Path | None) -> str:
    if source_path is None:
        return "<unknown>"
    try:
        src_root = next(parent for parent in source_path.parents if parent.name == "src")
    except StopIteration:
        return source_path.stem
    rel = source_path.relative_to(src_root)
    return ".".join(rel.with_suffix("").parts)


class _ProgramSummaryBuilder:
    def __init__(
        self,
        program: Mapping[str, Any],
        source_path: Path | None,
        diagnostics: list[DiagnosticEntry],
    ) -> None:
        self.program = program
        self.source_path = source_path
        self.diagnostics = diagnostics
        self.module = str(_mapping(program.get("module")).get("path", _fallback_module_name(source_path)))
        self.imported_symbols = self._build_imported_symbols()
        self.functions = self._build_function_index()
        self.enum_variants = self._build_enum_variant_index()
        self.function_error_cache: dict[str, list[str]] = {}

    def build(self) -> ModuleSummary:
        declarations = list(_list(self.program.get("declarations")))
        exports = [
            self._build_export_entry(decl)
            for decl in declarations
            if _kind(decl) == "FunctionDecl" and self._is_public(decl)
        ]
        types = [
            entry
            for decl in declarations
            for entry in [self._build_type_entry(decl)]
            if entry is not None
        ]
        return ModuleSummary(
            module=self.module,
            imports=[self._render_import(use_decl) for use_decl in _list(self.program.get("uses"))],
            exports=exports,
            types=types,
            diagnostics=self.diagnostics,
        )

    def _build_export_entry(self, decl: Mapping[str, Any]) -> ExportEntry:
        return ExportEntry(
            name=str(decl["name"]),
            kind="function",
            visibility=self._map_visibility(decl.get("visibility")),
            signature=self._render_signature(decl),
            effects=[str(effect) for effect in _list(decl.get("effects"))],
            errors=self._function_errors(str(decl["name"])),
            async_=bool(decl.get("async", False)),
            calls=self._function_calls(decl),
        )

    def _build_type_entry(self, decl: Mapping[str, Any]) -> TypeEntry | None:
        if not self._is_public(decl):
            return None
        kind = _kind(decl)
        if kind == "StructDecl":
            return TypeEntry(
                name=str(decl["name"]),
                kind="struct",
                fields=[
                    TypeField(
                        name=str(field["name"]),
                        type=self._render_type(_mapping(field.get("type"))),
                        visibility=self._map_visibility(field.get("visibility")),
                    )
                    for field in _list(decl.get("fields"))
                ],
            )
        if kind == "EnumDecl":
            return TypeEntry(
                name=str(decl["name"]),
                kind="enum",
                variants=[
                    TypeVariant(
                        name=str(variant["name"]),
                        fields=[
                            self._render_type(_mapping(field.get("type")))
                            for field in _list(variant.get("fields"))
                        ]
                        or None,
                    )
                    for variant in _list(decl.get("variants"))
                ],
            )
        if kind == "NewtypeDecl":
            return TypeEntry(
                name=str(decl["name"]),
                kind="newtype",
                target=self._render_type(_mapping(decl.get("target"))),
            )
        return None

    def _build_imported_symbols(self) -> dict[str, str]:
        symbols: dict[str, str] = {}
        for use_decl in _list(self.program.get("uses")):
            use_mapping = _mapping(use_decl)
            path = str(use_mapping.get("path", ""))
            imports = _list(use_mapping.get("imports"))
            if imports:
                for item in imports:
                    symbols[str(item)] = f"{path}.{item}"
                continue
            leaf = path.rsplit(".", 1)[-1]
            symbols[leaf] = path
        return symbols

    def _build_function_index(self) -> dict[str, Mapping[str, Any]]:
        return {
            str(decl["name"]): decl
            for decl in _list(self.program.get("declarations"))
            if _kind(decl) == "FunctionDecl"
        }

    def _build_enum_variant_index(self) -> dict[str, list[str]]:
        variants: dict[str, list[str]] = {}
        for decl in _list(self.program.get("declarations")):
            if _kind(decl) != "EnumDecl":
                continue
            variants[str(decl["name"])] = [
                f"{decl['name']}::{variant['name']}"
                for variant in _list(decl.get("variants"))
            ]
        return variants

    def _function_calls(self, decl: Mapping[str, Any]) -> list[str]:
        collected: list[str] = []
        seen: set[str] = set()
        for statement in _list(_mapping(decl.get("body")).get("statements")):
            self._collect_calls_from_statement(statement, decl, collected, seen)
        return collected

    def _collect_calls_from_statement(
        self,
        statement: Mapping[str, Any],
        function_decl: Mapping[str, Any],
        collected: list[str],
        seen: set[str],
    ) -> None:
        kind = _kind(statement)
        if kind in {"ExprStmt", "ReturnStmt"}:
            key = "expression" if kind == "ExprStmt" else "value"
            self._collect_calls_from_expression(_mapping(statement.get(key)), function_decl, collected, seen)
            return
        if kind in {"LetStmt", "VarStmt"}:
            self._collect_calls_from_expression(_mapping(statement.get("value")), function_decl, collected, seen)
            return
        if kind == "IfStmt":
            self._collect_calls_from_expression(_mapping(statement.get("condition")), function_decl, collected, seen)
            self._collect_calls_from_block(_mapping(statement.get("thenBlock")), function_decl, collected, seen)
            else_block = statement.get("elseBlock")
            if isinstance(else_block, Mapping):
                self._collect_calls_from_block(else_block, function_decl, collected, seen)

    def _collect_calls_from_block(
        self,
        block: Mapping[str, Any],
        function_decl: Mapping[str, Any],
        collected: list[str],
        seen: set[str],
    ) -> None:
        for statement in _list(block.get("statements")):
            self._collect_calls_from_statement(statement, function_decl, collected, seen)

    def _collect_calls_from_expression(
        self,
        expression: Mapping[str, Any],
        function_decl: Mapping[str, Any],
        collected: list[str],
        seen: set[str],
    ) -> None:
        kind = _kind(expression)
        if kind == "CallExpr":
            call_name = self._canonical_call(expression, function_decl)
            if call_name and call_name not in seen:
                seen.add(call_name)
                collected.append(call_name)
            for argument in _list(expression.get("arguments")):
                self._collect_calls_from_expression(_mapping(argument), function_decl, collected, seen)
            return
        if kind == "MatchExpr":
            self._collect_calls_from_expression(_mapping(expression.get("subject")), function_decl, collected, seen)
            for arm in _list(expression.get("arms")):
                self._collect_calls_from_expression(_mapping(_mapping(arm).get("body")), function_decl, collected, seen)

    def _canonical_call(
        self,
        expression: Mapping[str, Any],
        function_decl: Mapping[str, Any],
    ) -> str | None:
        raw_callee = str(expression.get("callee", ""))
        normalized = self._normalize_callee(raw_callee)
        if normalized in _IGNORED_CALLS:
            return None
        if "." not in normalized:
            if normalized in self.functions:
                return f"{self.module}.{normalized}"
            return self.imported_symbols.get(normalized)

        receiver, _, member = normalized.partition(".")
        receiver_binding = self._receiver_binding(receiver, function_decl)
        if receiver_binding:
            return f"{receiver_binding}.{member}"
        return None

    def _receiver_binding(
        self,
        receiver: str,
        function_decl: Mapping[str, Any],
    ) -> str | None:
        type_parameters = {
            str(item["name"]): str(item["constraint"])
            for item in _list(function_decl.get("typeParameters"))
            if isinstance(item, Mapping) and "constraint" in item
        }
        for parameter in _list(function_decl.get("parameters")):
            param_mapping = _mapping(parameter)
            if str(param_mapping.get("name", "")) != receiver:
                continue
            type_name = self._named_type_name(_mapping(param_mapping.get("type")))
            if type_name is None:
                return None
            if type_name in type_parameters:
                constrained = type_parameters[type_name]
                return self.imported_symbols.get(constrained, f"{self.module}.{constrained}")
            return None
        return None

    def _function_errors(self, function_name: str) -> list[str]:
        if function_name in self.function_error_cache:
            return list(self.function_error_cache[function_name])
        decl = self.functions[function_name]
        error_type = self._result_error_type(decl)
        if error_type is None:
            self.function_error_cache[function_name] = []
            return []

        collected: list[str] = []
        seen: set[str] = set()
        self.function_error_cache[function_name] = []
        self._collect_function_errors_from_block(
            _mapping(decl.get("body")),
            decl,
            error_type,
            collected,
            seen,
        )
        if not collected and error_type in self.enum_variants:
            self._extend_unique(collected, seen, self.enum_variants[error_type])
        self.function_error_cache[function_name] = list(collected)
        return collected

    def _callable_error_refs(self, function_name: str, error_type: str) -> list[str]:
        decl = self.functions[function_name]
        collected: list[str] = []
        seen: set[str] = set()
        self._collect_error_refs_from_block(_mapping(decl.get("body")), error_type, collected, seen)
        return collected

    def _collect_error_refs_from_block(
        self,
        block: Mapping[str, Any],
        error_type: str,
        collected: list[str],
        seen: set[str],
    ) -> None:
        for statement in _list(block.get("statements")):
            self._collect_error_refs_from_statement(statement, error_type, collected, seen)

    def _collect_error_refs_from_statement(
        self,
        statement: Mapping[str, Any],
        error_type: str,
        collected: list[str],
        seen: set[str],
    ) -> None:
        kind = _kind(statement)
        if kind in {"ExprStmt", "ReturnStmt"}:
            key = "expression" if kind == "ExprStmt" else "value"
            self._collect_error_refs_from_expression(_mapping(statement.get(key)), error_type, collected, seen)
            return
        if kind in {"LetStmt", "VarStmt"}:
            self._collect_error_refs_from_expression(_mapping(statement.get("value")), error_type, collected, seen)
            return
        if kind == "IfStmt":
            self._collect_error_refs_from_expression(_mapping(statement.get("condition")), error_type, collected, seen)
            self._collect_error_refs_from_block(_mapping(statement.get("thenBlock")), error_type, collected, seen)
            else_block = statement.get("elseBlock")
            if isinstance(else_block, Mapping):
                self._collect_error_refs_from_block(else_block, error_type, collected, seen)

    def _collect_error_refs_from_expression(
        self,
        expression: Mapping[str, Any],
        error_type: str,
        collected: list[str],
        seen: set[str],
    ) -> None:
        kind = _kind(expression)
        if kind == "IdentifierExpr":
            name = str(expression.get("name", ""))
            if name.startswith(f"{error_type}::") and name not in seen:
                seen.add(name)
                collected.append(name)
            return
        if kind == "CallExpr":
            for argument in _list(expression.get("arguments")):
                self._collect_error_refs_from_expression(_mapping(argument), error_type, collected, seen)
            return
        if kind == "MatchExpr":
            self._collect_error_refs_from_expression(_mapping(expression.get("subject")), error_type, collected, seen)
            for arm in _list(expression.get("arms")):
                body = _mapping(_mapping(arm).get("body"))
                self._collect_error_refs_from_expression(body, error_type, collected, seen)

    def _collect_function_errors_from_block(
        self,
        block: Mapping[str, Any],
        function_decl: Mapping[str, Any],
        error_type: str,
        collected: list[str],
        seen: set[str],
    ) -> None:
        for statement in _list(block.get("statements")):
            self._collect_function_errors_from_statement(
                statement,
                function_decl,
                error_type,
                collected,
                seen,
            )

    def _collect_function_errors_from_statement(
        self,
        statement: Mapping[str, Any],
        function_decl: Mapping[str, Any],
        error_type: str,
        collected: list[str],
        seen: set[str],
    ) -> None:
        kind = _kind(statement)
        if kind in {"ExprStmt", "ReturnStmt"}:
            key = "expression" if kind == "ExprStmt" else "value"
            self._collect_function_errors_from_expression(
                _mapping(statement.get(key)),
                function_decl,
                error_type,
                collected,
                seen,
            )
            return
        if kind in {"LetStmt", "VarStmt"}:
            self._collect_function_errors_from_expression(
                _mapping(statement.get("value")),
                function_decl,
                error_type,
                collected,
                seen,
            )
            return
        if kind == "IfStmt":
            self._collect_function_errors_from_expression(
                _mapping(statement.get("condition")),
                function_decl,
                error_type,
                collected,
                seen,
            )
            self._collect_function_errors_from_block(
                _mapping(statement.get("thenBlock")),
                function_decl,
                error_type,
                collected,
                seen,
            )
            else_block = statement.get("elseBlock")
            if isinstance(else_block, Mapping):
                self._collect_function_errors_from_block(
                    else_block,
                    function_decl,
                    error_type,
                    collected,
                    seen,
                )

    def _collect_function_errors_from_expression(
        self,
        expression: Mapping[str, Any],
        function_decl: Mapping[str, Any],
        error_type: str,
        collected: list[str],
        seen: set[str],
    ) -> None:
        kind = _kind(expression)
        if kind == "IdentifierExpr":
            name = str(expression.get("name", ""))
            if name.startswith(f"{error_type}::") and name not in seen:
                seen.add(name)
                collected.append(name)
            return
        if kind == "CallExpr":
            for argument in _list(expression.get("arguments")):
                self._collect_function_errors_from_expression(
                    _mapping(argument),
                    function_decl,
                    error_type,
                    collected,
                    seen,
                )
            if bool(expression.get("propagateError", False)):
                local_callee = self._local_callee_name(expression)
                if local_callee and local_callee in self.functions:
                    self._extend_unique(collected, seen, self._function_errors(local_callee))
                callback = self._map_err_callback(expression)
                if callback and callback in self.functions:
                    self._extend_unique(
                        collected,
                        seen,
                        self._callable_error_refs(callback, error_type),
                    )
            return
        if kind == "MatchExpr":
            self._collect_function_errors_from_expression(
                _mapping(expression.get("subject")),
                function_decl,
                error_type,
                collected,
                seen,
            )
            for arm in _list(expression.get("arms")):
                self._collect_function_errors_from_expression(
                    _mapping(_mapping(arm).get("body")),
                    function_decl,
                    error_type,
                    collected,
                    seen,
                )

    def _iter_propagating_calls(self, block: Mapping[str, Any]) -> list[Mapping[str, Any]]:
        calls: list[Mapping[str, Any]] = []
        for statement in _list(block.get("statements")):
            self._collect_propagating_calls_from_statement(statement, calls)
        return calls

    def _collect_propagating_calls_from_statement(
        self,
        statement: Mapping[str, Any],
        calls: list[Mapping[str, Any]],
    ) -> None:
        kind = _kind(statement)
        if kind in {"ExprStmt", "ReturnStmt"}:
            key = "expression" if kind == "ExprStmt" else "value"
            self._collect_propagating_calls_from_expression(_mapping(statement.get(key)), calls)
            return
        if kind in {"LetStmt", "VarStmt"}:
            self._collect_propagating_calls_from_expression(_mapping(statement.get("value")), calls)
            return
        if kind == "IfStmt":
            self._collect_propagating_calls_from_expression(_mapping(statement.get("condition")), calls)
            self._collect_propagating_calls_from_block(_mapping(statement.get("thenBlock")), calls)
            else_block = statement.get("elseBlock")
            if isinstance(else_block, Mapping):
                self._collect_propagating_calls_from_block(else_block, calls)

    def _collect_propagating_calls_from_block(
        self,
        block: Mapping[str, Any],
        calls: list[Mapping[str, Any]],
    ) -> None:
        for statement in _list(block.get("statements")):
            self._collect_propagating_calls_from_statement(statement, calls)

    def _collect_propagating_calls_from_expression(
        self,
        expression: Mapping[str, Any],
        calls: list[Mapping[str, Any]],
    ) -> None:
        kind = _kind(expression)
        if kind == "CallExpr":
            if bool(expression.get("propagateError", False)):
                calls.append(expression)
            for argument in _list(expression.get("arguments")):
                self._collect_propagating_calls_from_expression(_mapping(argument), calls)
            return
        if kind == "MatchExpr":
            self._collect_propagating_calls_from_expression(_mapping(expression.get("subject")), calls)
            for arm in _list(expression.get("arms")):
                self._collect_propagating_calls_from_expression(_mapping(_mapping(arm).get("body")), calls)

    def _local_callee_name(self, expression: Mapping[str, Any]) -> str | None:
        normalized = self._normalize_callee(str(expression.get("callee", "")))
        if "." in normalized:
            return None
        return normalized if normalized in self.functions else None

    def _map_err_callback(self, expression: Mapping[str, Any]) -> str | None:
        raw_callee = str(expression.get("callee", ""))
        if not raw_callee.endswith(".map_err"):
            return None
        arguments = _list(expression.get("arguments"))
        if not arguments:
            return None
        first = _mapping(arguments[0])
        if _kind(first) != "IdentifierExpr":
            return None
        return str(first.get("name", ""))

    def _normalize_callee(self, callee: str) -> str:
        normalized = callee.strip()
        if normalized.endswith(".map_err"):
            normalized = normalized[: -len(".map_err")]
        paren_index = normalized.find("(")
        if paren_index != -1:
            normalized = normalized[:paren_index]
        return normalized

    def _render_import(self, use_decl: Mapping[str, Any]) -> str:
        path = str(use_decl.get("path", ""))
        imports = [str(item) for item in _list(use_decl.get("imports"))]
        if not imports:
            return path
        return f"{path}.{{{','.join(imports)}}}"

    def _render_signature(self, decl: Mapping[str, Any]) -> str:
        constrained_type_parameters = {
            str(item["name"])
            for item in _list(decl.get("typeParameters"))
            if isinstance(item, Mapping) and "constraint" in item
        }
        parameters = [
            self._render_type(_mapping(parameter.get("type")))
            for parameter in _list(decl.get("parameters"))
            if self._named_type_name(_mapping(parameter.get("type"))) not in constrained_type_parameters
        ]
        return f"({', '.join(parameters)}) -> {self._render_type(_mapping(decl.get('returnType')))}"

    def _render_type(self, type_expr: Mapping[str, Any]) -> str:
        kind = _kind(type_expr)
        if kind == "NamedType":
            return str(type_expr.get("name", "Unknown"))
        if kind == "GenericType":
            arguments = [
                self._render_type(_mapping(argument))
                for argument in _list(type_expr.get("arguments"))
            ]
            return f"{type_expr.get('name', 'Unknown')}<{', '.join(arguments)}>"
        if kind == "ResultType":
            ok_type = self._render_type(_mapping(type_expr.get("ok")))
            err_type = self._render_type(_mapping(type_expr.get("err")))
            return f"Result<{ok_type}, {err_type}>"
        if kind == "OptionType":
            return f"Option<{self._render_type(_mapping(type_expr.get('item')))}>"
        if kind == "UnitType":
            return "Unit"
        return "Unknown"

    def _result_error_type(self, decl: Mapping[str, Any]) -> str | None:
        return_type = _mapping(decl.get("returnType"))
        if _kind(return_type) != "ResultType":
            return None
        error_type = _mapping(return_type.get("err"))
        if _kind(error_type) != "NamedType":
            return None
        return str(error_type.get("name"))

    def _named_type_name(self, type_expr: Mapping[str, Any]) -> str | None:
        if _kind(type_expr) != "NamedType":
            return None
        return str(type_expr.get("name"))

    def _map_visibility(self, value: Any) -> str:
        return _VISIBILITY_MAP.get(str(value), "private")

    def _is_public(self, decl: Mapping[str, Any]) -> bool:
        return self._map_visibility(decl.get("visibility")) == "public"

    def _extend_unique(self, target: list[str], seen: set[str], values: list[str]) -> None:
        for value in values:
            if value not in seen:
                seen.add(value)
                target.append(value)


def _diagnostics_from_report(report: Any) -> list[DiagnosticEntry]:
    payloads = _diagnostic_payloads(report)
    diagnostics: list[DiagnosticEntry] = []
    for payload in payloads:
        location = _location_from_payload(_mapping(payload.get("location")))
        diagnostics.append(
            DiagnosticEntry(
                level=str(payload.get("level", "error")),
                code=str(payload.get("code", "P999")),
                message=str(payload.get("message", "")),
                location=location,
            )
        )
    return diagnostics


def _diagnostic_payloads(report: Any) -> list[Mapping[str, Any]]:
    if isinstance(report, Mapping):
        diagnostics = report.get("diagnostics")
        if isinstance(diagnostics, list):
            return [item for item in diagnostics if isinstance(item, Mapping)]
        if {"level", "code", "message", "location"} <= set(report):
            return [report]
        return []
    if isinstance(report, list):
        return [item for item in report if isinstance(item, Mapping)]
    return []


def _location_from_payload(location: Mapping[str, Any]) -> SourceLocation:
    file_path = str(location.get("file", "<memory>"))
    if "line" in location and "column" in location:
        return SourceLocation(file=file_path, line=int(location["line"]), column=int(location["column"]))
    start = _mapping(location.get("start"))
    if "line" in start and "column" in start:
        return SourceLocation(file=file_path, line=int(start["line"]), column=int(start["column"]))
    return SourceLocation(file=file_path, line=1, column=1)


def _kind(data: Mapping[str, Any]) -> str:
    return str(data.get("kind", ""))


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}
