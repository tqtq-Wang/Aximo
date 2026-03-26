from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Literal, Mapping

SCHEMA_VERSION = "0.1.0"

ExportKind = Literal["function", "struct", "enum", "trait", "const"]
Visibility = Literal["public", "internal", "private"]
TypeKind = Literal["struct", "enum", "newtype", "alias"]
DiagnosticLevel = Literal["error", "warning", "info"]
BreakingChangeKind = Literal[
    "removed_export",
    "signature_changed",
    "effect_expanded",
    "enum_variant_removed",
]

EXPORT_KINDS = {"function", "struct", "enum", "trait", "const"}
VISIBILITIES = {"public", "internal", "private"}
TYPE_KINDS = {"struct", "enum", "newtype", "alias"}
DIAGNOSTIC_LEVELS = {"error", "warning", "info"}
BREAKING_CHANGE_KINDS = {
    "removed_export",
    "signature_changed",
    "effect_expanded",
    "enum_variant_removed",
}
SUMMARY_KEYS = {
    "schema_version",
    "module",
    "imports",
    "exports",
    "types",
    "diagnostics",
    "breaking_changes",
}
EXPORT_ENTRY_KEYS = {
    "name",
    "kind",
    "visibility",
    "signature",
    "effects",
    "errors",
    "async",
    "calls",
}
TYPE_FIELD_KEYS = {"name", "type", "visibility"}
TYPE_VARIANT_KEYS = {"name", "fields"}
TYPE_ENTRY_KEYS = {"name", "kind", "fields", "variants", "target"}
SOURCE_LOCATION_KEYS = {"file", "line", "column"}
DIAGNOSTIC_ENTRY_KEYS = {"level", "code", "message", "location"}
BREAKING_CHANGE_KEYS = {"kind", "symbol", "message"}


def _validate_choice(value: str, *, field_name: str, allowed: set[str]) -> str:
    if value not in allowed:
        allowed_values = ", ".join(sorted(allowed))
        raise ValueError(f"{field_name} must be one of: {allowed_values}")
    return value


def _coerce_string_list(values: Iterable[str] | None) -> list[str]:
    if values is None:
        return []
    return [str(value) for value in values]


def _reject_unknown_keys(
    data: Mapping[str, Any],
    *,
    context: str,
    allowed: set[str],
) -> None:
    unknown_keys = sorted(set(data) - allowed)
    if unknown_keys:
        rendered = ", ".join(unknown_keys)
        raise ValueError(f"unexpected {context} field(s): {rendered}")


@dataclass(slots=True)
class SourceLocation:
    file: str
    line: int
    column: int

    def __post_init__(self) -> None:
        if self.line < 1:
            raise ValueError("location.line must be >= 1")
        if self.column < 1:
            raise ValueError("location.column must be >= 1")

    def to_dict(self) -> dict[str, Any]:
        return {
            "file": self.file,
            "line": self.line,
            "column": self.column,
        }


@dataclass(slots=True)
class ExportEntry:
    name: str
    kind: ExportKind
    visibility: Visibility
    signature: str
    effects: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    async_: bool = False
    calls: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        _validate_choice(self.kind, field_name="export.kind", allowed=EXPORT_KINDS)
        _validate_choice(
            self.visibility,
            field_name="export.visibility",
            allowed=VISIBILITIES,
        )
        self.effects = _coerce_string_list(self.effects)
        self.errors = _coerce_string_list(self.errors)
        self.calls = _coerce_string_list(self.calls)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "kind": self.kind,
            "visibility": self.visibility,
            "signature": self.signature,
            "effects": list(self.effects),
            "errors": list(self.errors),
            "async": self.async_,
            "calls": list(self.calls),
        }


@dataclass(slots=True)
class TypeField:
    name: str
    type: str
    visibility: Visibility | None = None

    def __post_init__(self) -> None:
        if self.visibility is not None:
            _validate_choice(
                self.visibility,
                field_name="type_field.visibility",
                allowed=VISIBILITIES,
            )

    def to_dict(self) -> dict[str, Any]:
        data = {
            "name": self.name,
            "type": self.type,
        }
        if self.visibility is not None:
            data["visibility"] = self.visibility
        return data


@dataclass(slots=True)
class TypeVariant:
    name: str
    fields: list[str] | None = None

    def __post_init__(self) -> None:
        if self.fields is not None:
            self.fields = _coerce_string_list(self.fields)

    def to_dict(self) -> dict[str, Any]:
        data = {"name": self.name}
        if self.fields is not None:
            data["fields"] = list(self.fields)
        return data


@dataclass(slots=True)
class TypeEntry:
    name: str
    kind: TypeKind
    fields: list[TypeField] | None = None
    variants: list[TypeVariant] | None = None
    target: str | None = None

    def __post_init__(self) -> None:
        _validate_choice(self.kind, field_name="type.kind", allowed=TYPE_KINDS)

    def to_dict(self) -> dict[str, Any]:
        data = {
            "name": self.name,
            "kind": self.kind,
        }
        if self.fields is not None:
            data["fields"] = [field_item.to_dict() for field_item in self.fields]
        if self.variants is not None:
            data["variants"] = [
                variant_item.to_dict() for variant_item in self.variants
            ]
        if self.target is not None:
            data["target"] = self.target
        return data


@dataclass(slots=True)
class DiagnosticEntry:
    level: DiagnosticLevel
    code: str
    message: str
    location: SourceLocation

    def __post_init__(self) -> None:
        _validate_choice(
            self.level,
            field_name="diagnostic.level",
            allowed=DIAGNOSTIC_LEVELS,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "level": self.level,
            "code": self.code,
            "message": self.message,
            "location": self.location.to_dict(),
        }


@dataclass(slots=True)
class BreakingChange:
    kind: BreakingChangeKind
    symbol: str
    message: str

    def __post_init__(self) -> None:
        _validate_choice(
            self.kind,
            field_name="breaking_change.kind",
            allowed=BREAKING_CHANGE_KINDS,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": self.kind,
            "symbol": self.symbol,
            "message": self.message,
        }


@dataclass(slots=True)
class ModuleSummary:
    module: str
    imports: list[str] = field(default_factory=list)
    exports: list[ExportEntry] = field(default_factory=list)
    types: list[TypeEntry] = field(default_factory=list)
    diagnostics: list[DiagnosticEntry] = field(default_factory=list)
    breaking_changes: list[BreakingChange] = field(default_factory=list)
    schema_version: str = SCHEMA_VERSION

    def __post_init__(self) -> None:
        self.imports = _coerce_string_list(self.imports)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "module": self.module,
            "imports": list(self.imports),
            "exports": [entry.to_dict() for entry in self.exports],
            "types": [entry.to_dict() for entry in self.types],
            "diagnostics": [entry.to_dict() for entry in self.diagnostics],
            "breaking_changes": [
                entry.to_dict() for entry in self.breaking_changes
            ],
        }


def new_module_summary(
    module: str,
    *,
    imports: Iterable[str] | None = None,
) -> ModuleSummary:
    return ModuleSummary(module=module, imports=_coerce_string_list(imports))


def build_summary_output_path(output_dir: str | Path, summary_name: str) -> Path:
    return Path(output_dir) / f"{summary_name}.summary.json"


def summary_to_json(summary: ModuleSummary, *, indent: int = 2) -> str:
    return json.dumps(summary.to_dict(), indent=indent, ensure_ascii=True) + "\n"


def write_summary(
    summary: ModuleSummary,
    destination: str | Path,
    *,
    indent: int = 2,
) -> Path:
    output_path = Path(destination)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(summary_to_json(summary, indent=indent), encoding="utf-8")
    return output_path


def _require_mapping_field(
    data: Mapping[str, Any],
    key: str,
    *,
    context: str,
) -> Any:
    if key not in data:
        raise ValueError(f"missing required {context} field: {key}")
    return data[key]


def export_entry_from_mapping(data: Mapping[str, Any]) -> ExportEntry:
    _reject_unknown_keys(data, context="export", allowed=EXPORT_ENTRY_KEYS)
    return ExportEntry(
        name=str(_require_mapping_field(data, "name", context="export")),
        kind=str(_require_mapping_field(data, "kind", context="export")),
        visibility=str(
            _require_mapping_field(data, "visibility", context="export")
        ),
        signature=str(_require_mapping_field(data, "signature", context="export")),
        effects=_coerce_string_list(data.get("effects")),
        errors=_coerce_string_list(data.get("errors")),
        async_=bool(_require_mapping_field(data, "async", context="export")),
        calls=_coerce_string_list(data.get("calls")),
    )


def type_field_from_mapping(data: Mapping[str, Any]) -> TypeField:
    _reject_unknown_keys(data, context="type field", allowed=TYPE_FIELD_KEYS)
    return TypeField(
        name=str(_require_mapping_field(data, "name", context="type field")),
        type=str(_require_mapping_field(data, "type", context="type field")),
        visibility=(
            None if "visibility" not in data else str(data["visibility"])
        ),
    )


def type_variant_from_mapping(data: Mapping[str, Any]) -> TypeVariant:
    _reject_unknown_keys(data, context="type variant", allowed=TYPE_VARIANT_KEYS)
    return TypeVariant(
        name=str(_require_mapping_field(data, "name", context="type variant")),
        fields=(
            None if "fields" not in data else _coerce_string_list(data["fields"])
        ),
    )


def type_entry_from_mapping(data: Mapping[str, Any]) -> TypeEntry:
    _reject_unknown_keys(data, context="type", allowed=TYPE_ENTRY_KEYS)
    fields = None
    if "fields" in data:
        fields = [
            type_field_from_mapping(field_item)
            for field_item in data["fields"]
        ]

    variants = None
    if "variants" in data:
        variants = [
            type_variant_from_mapping(variant_item)
            for variant_item in data["variants"]
        ]

    return TypeEntry(
        name=str(_require_mapping_field(data, "name", context="type")),
        kind=str(_require_mapping_field(data, "kind", context="type")),
        fields=fields,
        variants=variants,
        target=(None if "target" not in data else str(data["target"])),
    )


def source_location_from_mapping(data: Mapping[str, Any]) -> SourceLocation:
    _reject_unknown_keys(data, context="location", allowed=SOURCE_LOCATION_KEYS)
    return SourceLocation(
        file=str(_require_mapping_field(data, "file", context="location")),
        line=int(_require_mapping_field(data, "line", context="location")),
        column=int(_require_mapping_field(data, "column", context="location")),
    )


def diagnostic_entry_from_mapping(data: Mapping[str, Any]) -> DiagnosticEntry:
    _reject_unknown_keys(
        data,
        context="diagnostic",
        allowed=DIAGNOSTIC_ENTRY_KEYS,
    )
    return DiagnosticEntry(
        level=str(_require_mapping_field(data, "level", context="diagnostic")),
        code=str(_require_mapping_field(data, "code", context="diagnostic")),
        message=str(_require_mapping_field(data, "message", context="diagnostic")),
        location=source_location_from_mapping(
            _require_mapping_field(data, "location", context="diagnostic")
        ),
    )


def breaking_change_from_mapping(data: Mapping[str, Any]) -> BreakingChange:
    _reject_unknown_keys(
        data,
        context="breaking change",
        allowed=BREAKING_CHANGE_KEYS,
    )
    return BreakingChange(
        kind=str(_require_mapping_field(data, "kind", context="breaking change")),
        symbol=str(_require_mapping_field(data, "symbol", context="breaking change")),
        message=str(
            _require_mapping_field(data, "message", context="breaking change")
        ),
    )


def module_summary_from_mapping(data: Mapping[str, Any]) -> ModuleSummary:
    _reject_unknown_keys(data, context="summary", allowed=SUMMARY_KEYS)
    return ModuleSummary(
        schema_version=str(data.get("schema_version", SCHEMA_VERSION)),
        module=str(_require_mapping_field(data, "module", context="summary")),
        imports=_coerce_string_list(data.get("imports")),
        exports=[
            export_entry_from_mapping(export_item)
            for export_item in data.get("exports", [])
        ],
        types=[
            type_entry_from_mapping(type_item)
            for type_item in data.get("types", [])
        ],
        diagnostics=[
            diagnostic_entry_from_mapping(diagnostic_item)
            for diagnostic_item in data.get("diagnostics", [])
        ],
        breaking_changes=[
            breaking_change_from_mapping(change_item)
            for change_item in data.get("breaking_changes", [])
        ],
    )
