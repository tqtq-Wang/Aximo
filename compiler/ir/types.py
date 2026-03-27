from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Literal, Mapping, TypeAlias

IR_SCHEMA_VERSION = "0.2.0"

Visibility = Literal["public", "internal", "private"]

VALUE_KINDS = {
    "ConstructValue",
    "DirectCall",
    "FieldValue",
    "Literal",
    "LocalRef",
    "ParameterRef",
    "SymbolRef",
}
INSTRUCTION_KINDS = {"Bind", "ErrorPropagationPlaceholder", "Eval"}
TERMINATOR_KINDS = {"Branch", "Jump", "Return"}
DECLARATION_KINDS = {
    "EnumType",
    "Function",
    "ImplSurface",
    "Newtype",
    "StructType",
    "TestSurface",
    "TraitSurface",
}
VISIBILITIES = {"public", "internal", "private"}
PROGRAM_KEYS = {"kind", "schema_version", "modules"}
MODULE_KEYS = {
    "kind",
    "name",
    "source_file",
    "imports",
    "declarations",
    "functions",
}
IMPORT_KEYS = {"kind", "module", "names", "alias"}
SYMBOL_REF_KEYS = {"kind", "name", "module"}
TYPE_REF_KEYS = {"kind", "name"}
TYPE_PARAMETER_KEYS = {"kind", "name", "constraint"}
PARAMETER_KEYS = {"kind", "name", "type"}
LOCAL_BINDING_KEYS = {"kind", "name", "type", "mutable"}
BASIC_BLOCK_KEYS = {"kind", "name", "instructions", "terminator"}
BIND_KEYS = {"kind", "binding", "value"}
EVAL_KEYS = {"kind", "value"}
ERROR_PROPAGATION_KEYS = {
    "kind",
    "source",
    "binding",
    "error_adapter",
    "strategy",
    "comment",
}
DIRECT_CALL_KEYS = {"kind", "callee", "arguments", "result_type", "await"}
CONSTRUCT_VALUE_KEYS = {"kind", "type", "constructor", "arguments", "fields"}
FIELD_VALUE_KEYS = {"kind", "base", "field"}
LITERAL_KEYS = {"kind", "type", "value"}
LOCAL_REF_KEYS = {"kind", "name"}
PARAMETER_REF_KEYS = {"kind", "name"}
NAMED_ARGUMENT_KEYS = {"kind", "name", "value"}
BRANCH_KEYS = {"kind", "condition", "then_block", "else_block"}
JUMP_KEYS = {"kind", "target_block"}
RETURN_KEYS = {"kind", "value"}
FUNCTION_KEYS = {
    "kind",
    "name",
    "visibility",
    "type_parameters",
    "parameters",
    "return_type",
    "effects",
    "async",
    "entry_block",
    "blocks",
    "notes",
}
STRUCT_FIELD_KEYS = {"kind", "name", "type", "visibility"}
STRUCT_TYPE_KEYS = {"kind", "name", "visibility", "fields", "notes"}
ENUM_VARIANT_KEYS = {"kind", "name", "payload"}
ENUM_TYPE_KEYS = {"kind", "name", "visibility", "variants", "notes"}
NEWTYPE_KEYS = {"kind", "name", "visibility", "target", "notes"}
TRAIT_MEMBER_KEYS = {
    "kind",
    "name",
    "type_parameters",
    "parameters",
    "return_type",
    "effects",
    "async",
}
TRAIT_SURFACE_KEYS = {
    "kind",
    "name",
    "visibility",
    "type_parameters",
    "members",
    "notes",
}
IMPL_SURFACE_KEYS = {"kind", "trait", "for_type", "methods", "notes"}
TEST_SURFACE_KEYS = {"kind", "name", "entry_block", "blocks", "notes"}

Value: TypeAlias = (
    "ConstructValue | DirectCall | FieldValue | Literal | LocalRef | ParameterRef | SymbolRef"
)
Instruction: TypeAlias = "Bind | ErrorPropagationPlaceholder | Eval"
Terminator: TypeAlias = "Branch | Jump | Return"
Declaration: TypeAlias = (
    "EnumType | Function | ImplSurface | Newtype | StructType | TestSurface | TraitSurface"
)


def _validate_choice(value: str, *, field_name: str, allowed: set[str]) -> str:
    if value not in allowed:
        allowed_values = ", ".join(sorted(allowed))
        raise ValueError(f"{field_name} must be one of: {allowed_values}")
    return value


def _coerce_string_list(values: list[str] | None) -> list[str]:
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


def _require_mapping_field(
    data: Mapping[str, Any],
    key: str,
    *,
    context: str,
) -> Any:
    if key not in data:
        raise ValueError(f"missing required {context} field: {key}")
    return data[key]


def _validate_block_graph(
    *,
    entry_block: str,
    blocks: list["BasicBlock"],
    context: str,
) -> None:
    if not blocks:
        raise ValueError(f"{context}.blocks must not be empty")
    block_names = [block.name for block in blocks]
    if len(block_names) != len(set(block_names)):
        raise ValueError(f"{context}.blocks must have unique names")
    if entry_block not in set(block_names):
        raise ValueError(f"{context}.entry_block must name one of {context}.blocks")


@dataclass(slots=True)
class SymbolRef:
    name: str
    module: str | None = None

    def to_dict(self) -> dict[str, Any]:
        data = {
            "kind": "SymbolRef",
            "name": self.name,
        }
        if self.module is not None:
            data["module"] = self.module
        return data


@dataclass(slots=True)
class TypeRef:
    name: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": "TypeRef",
            "name": self.name,
        }


@dataclass(slots=True)
class TypeParameter:
    name: str
    constraint: SymbolRef | None = None

    def to_dict(self) -> dict[str, Any]:
        data = {
            "kind": "TypeParameter",
            "name": self.name,
        }
        if self.constraint is not None:
            data["constraint"] = self.constraint.to_dict()
        return data


@dataclass(slots=True)
class Import:
    module: str
    names: list[str] = field(default_factory=list)
    alias: str | None = None

    def __post_init__(self) -> None:
        self.names = _coerce_string_list(self.names)

    def to_dict(self) -> dict[str, Any]:
        data = {
            "kind": "Import",
            "module": self.module,
            "names": list(self.names),
        }
        if self.alias is not None:
            data["alias"] = self.alias
        return data


@dataclass(slots=True)
class Parameter:
    name: str
    type: TypeRef

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": "Parameter",
            "name": self.name,
            "type": self.type.to_dict(),
        }


@dataclass(slots=True)
class LocalBinding:
    name: str
    type: TypeRef | None = None
    mutable: bool = False

    def to_dict(self) -> dict[str, Any]:
        data = {
            "kind": "LocalBinding",
            "name": self.name,
            "mutable": self.mutable,
        }
        if self.type is not None:
            data["type"] = self.type.to_dict()
        return data


@dataclass(slots=True)
class LocalRef:
    name: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": "LocalRef",
            "name": self.name,
        }


@dataclass(slots=True)
class ParameterRef:
    name: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": "ParameterRef",
            "name": self.name,
        }


@dataclass(slots=True)
class Literal:
    type: TypeRef
    value: Any

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": "Literal",
            "type": self.type.to_dict(),
            "value": self.value,
        }


@dataclass(slots=True)
class FieldValue:
    base: Value
    field: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": "FieldValue",
            "base": value_to_dict(self.base),
            "field": self.field,
        }


@dataclass(slots=True)
class DirectCall:
    callee: SymbolRef
    arguments: list[Value] = field(default_factory=list)
    result_type: TypeRef | None = None
    await_: bool = False

    def to_dict(self) -> dict[str, Any]:
        data = {
            "kind": "DirectCall",
            "callee": self.callee.to_dict(),
            "arguments": [value_to_dict(argument) for argument in self.arguments],
            "await": self.await_,
        }
        if self.result_type is not None:
            data["result_type"] = self.result_type.to_dict()
        return data


@dataclass(slots=True)
class NamedArgument:
    name: str
    value: Value

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": "NamedArgument",
            "name": self.name,
            "value": value_to_dict(self.value),
        }


@dataclass(slots=True)
class ConstructValue:
    type: TypeRef
    constructor: SymbolRef | None = None
    arguments: list[Value] = field(default_factory=list)
    fields: list[NamedArgument] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        data = {
            "kind": "ConstructValue",
            "type": self.type.to_dict(),
            "arguments": [value_to_dict(argument) for argument in self.arguments],
            "fields": [field_item.to_dict() for field_item in self.fields],
        }
        if self.constructor is not None:
            data["constructor"] = self.constructor.to_dict()
        return data


@dataclass(slots=True)
class Bind:
    binding: LocalBinding
    value: Value

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": "Bind",
            "binding": self.binding.to_dict(),
            "value": value_to_dict(self.value),
        }


@dataclass(slots=True)
class Eval:
    value: Value

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": "Eval",
            "value": value_to_dict(self.value),
        }


@dataclass(slots=True)
class ErrorPropagationPlaceholder:
    source: Value
    binding: LocalBinding | None = None
    error_adapter: SymbolRef | None = None
    strategy: str = "result_branch"
    comment: str | None = None

    def to_dict(self) -> dict[str, Any]:
        data = {
            "kind": "ErrorPropagationPlaceholder",
            "source": value_to_dict(self.source),
            "strategy": self.strategy,
        }
        if self.binding is not None:
            data["binding"] = self.binding.to_dict()
        if self.error_adapter is not None:
            data["error_adapter"] = self.error_adapter.to_dict()
        if self.comment is not None:
            data["comment"] = self.comment
        return data


@dataclass(slots=True)
class Jump:
    target_block: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": "Jump",
            "target_block": self.target_block,
        }


@dataclass(slots=True)
class Branch:
    condition: Value
    then_block: str
    else_block: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": "Branch",
            "condition": value_to_dict(self.condition),
            "then_block": self.then_block,
            "else_block": self.else_block,
        }


@dataclass(slots=True)
class Return:
    value: Value | None = None

    def to_dict(self) -> dict[str, Any]:
        data = {"kind": "Return"}
        if self.value is not None:
            data["value"] = value_to_dict(self.value)
        return data


@dataclass(slots=True)
class BasicBlock:
    name: str
    instructions: list[Instruction] = field(default_factory=list)
    terminator: Terminator = field(default_factory=Return)

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": "BasicBlock",
            "name": self.name,
            "instructions": [
                instruction_to_dict(instruction) for instruction in self.instructions
            ],
            "terminator": terminator_to_dict(self.terminator),
        }


@dataclass(slots=True)
class StructField:
    name: str
    type: TypeRef
    visibility: Visibility = "private"

    def __post_init__(self) -> None:
        _validate_choice(
            self.visibility,
            field_name="struct_field.visibility",
            allowed=VISIBILITIES,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": "StructField",
            "name": self.name,
            "type": self.type.to_dict(),
            "visibility": self.visibility,
        }


@dataclass(slots=True)
class EnumVariant:
    name: str
    payload: list[TypeRef] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": "EnumVariant",
            "name": self.name,
            "payload": [item.to_dict() for item in self.payload],
        }


@dataclass(slots=True)
class Function:
    name: str
    parameters: list[Parameter] = field(default_factory=list)
    return_type: TypeRef | None = None
    effects: list[str] = field(default_factory=list)
    async_: bool = False
    entry_block: str = "entry"
    blocks: list[BasicBlock] = field(default_factory=list)
    visibility: Visibility = "private"
    type_parameters: list[TypeParameter] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        _validate_choice(
            self.visibility,
            field_name="function.visibility",
            allowed=VISIBILITIES,
        )
        self.effects = _coerce_string_list(self.effects)
        self.notes = _coerce_string_list(self.notes)
        _validate_block_graph(
            entry_block=self.entry_block,
            blocks=self.blocks,
            context="function",
        )

    def to_dict(self) -> dict[str, Any]:
        data = {
            "kind": "Function",
            "name": self.name,
            "visibility": self.visibility,
            "type_parameters": [item.to_dict() for item in self.type_parameters],
            "parameters": [parameter.to_dict() for parameter in self.parameters],
            "effects": list(self.effects),
            "async": self.async_,
            "entry_block": self.entry_block,
            "blocks": [block.to_dict() for block in self.blocks],
            "notes": list(self.notes),
        }
        if self.return_type is not None:
            data["return_type"] = self.return_type.to_dict()
        return data


@dataclass(slots=True)
class StructType:
    name: str
    fields: list[StructField] = field(default_factory=list)
    visibility: Visibility = "private"
    notes: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        _validate_choice(
            self.visibility,
            field_name="struct_type.visibility",
            allowed=VISIBILITIES,
        )
        self.notes = _coerce_string_list(self.notes)

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": "StructType",
            "name": self.name,
            "visibility": self.visibility,
            "fields": [field_item.to_dict() for field_item in self.fields],
            "notes": list(self.notes),
        }


@dataclass(slots=True)
class EnumType:
    name: str
    variants: list[EnumVariant] = field(default_factory=list)
    visibility: Visibility = "private"
    notes: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        _validate_choice(
            self.visibility,
            field_name="enum_type.visibility",
            allowed=VISIBILITIES,
        )
        self.notes = _coerce_string_list(self.notes)

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": "EnumType",
            "name": self.name,
            "visibility": self.visibility,
            "variants": [item.to_dict() for item in self.variants],
            "notes": list(self.notes),
        }


@dataclass(slots=True)
class Newtype:
    name: str
    target: TypeRef
    visibility: Visibility = "private"
    notes: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        _validate_choice(
            self.visibility,
            field_name="newtype.visibility",
            allowed=VISIBILITIES,
        )
        self.notes = _coerce_string_list(self.notes)

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": "Newtype",
            "name": self.name,
            "visibility": self.visibility,
            "target": self.target.to_dict(),
            "notes": list(self.notes),
        }


@dataclass(slots=True)
class TraitMember:
    name: str
    parameters: list[Parameter] = field(default_factory=list)
    return_type: TypeRef | None = None
    effects: list[str] = field(default_factory=list)
    async_: bool = False
    type_parameters: list[TypeParameter] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.effects = _coerce_string_list(self.effects)

    def to_dict(self) -> dict[str, Any]:
        data = {
            "kind": "TraitMember",
            "name": self.name,
            "type_parameters": [item.to_dict() for item in self.type_parameters],
            "parameters": [parameter.to_dict() for parameter in self.parameters],
            "effects": list(self.effects),
            "async": self.async_,
        }
        if self.return_type is not None:
            data["return_type"] = self.return_type.to_dict()
        return data


@dataclass(slots=True)
class TraitSurface:
    name: str
    members: list[TraitMember] = field(default_factory=list)
    visibility: Visibility = "private"
    type_parameters: list[TypeParameter] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        _validate_choice(
            self.visibility,
            field_name="trait_surface.visibility",
            allowed=VISIBILITIES,
        )
        self.notes = _coerce_string_list(self.notes)

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": "TraitSurface",
            "name": self.name,
            "visibility": self.visibility,
            "type_parameters": [item.to_dict() for item in self.type_parameters],
            "members": [member.to_dict() for member in self.members],
            "notes": list(self.notes),
        }


@dataclass(slots=True)
class ImplSurface:
    for_type: TypeRef
    methods: list[Function] = field(default_factory=list)
    trait: SymbolRef | None = None
    notes: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.notes = _coerce_string_list(self.notes)

    def to_dict(self) -> dict[str, Any]:
        data = {
            "kind": "ImplSurface",
            "for_type": self.for_type.to_dict(),
            "methods": [method.to_dict() for method in self.methods],
            "notes": list(self.notes),
        }
        if self.trait is not None:
            data["trait"] = self.trait.to_dict()
        return data


@dataclass(slots=True)
class TestSurface:
    name: str
    entry_block: str = "entry"
    blocks: list[BasicBlock] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.notes = _coerce_string_list(self.notes)
        _validate_block_graph(
            entry_block=self.entry_block,
            blocks=self.blocks,
            context="test_surface",
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": "TestSurface",
            "name": self.name,
            "entry_block": self.entry_block,
            "blocks": [block.to_dict() for block in self.blocks],
            "notes": list(self.notes),
        }


@dataclass(slots=True)
class Module:
    name: str
    imports: list[Import] = field(default_factory=list)
    declarations: list[Declaration] = field(default_factory=list)
    source_file: str | None = None

    def to_dict(self) -> dict[str, Any]:
        data = {
            "kind": "Module",
            "name": self.name,
            "imports": [item.to_dict() for item in self.imports],
            "declarations": [
                declaration_to_dict(declaration)
                for declaration in self.declarations
            ],
        }
        if self.source_file is not None:
            data["source_file"] = self.source_file
        return data

    @property
    def functions(self) -> list[Function]:
        return [
            declaration
            for declaration in self.declarations
            if isinstance(declaration, Function)
        ]


@dataclass(slots=True)
class Program:
    modules: list[Module] = field(default_factory=list)
    schema_version: str = IR_SCHEMA_VERSION

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": "Program",
            "schema_version": self.schema_version,
            "modules": [module.to_dict() for module in self.modules],
        }


def value_to_dict(value: Value) -> dict[str, Any]:
    return value.to_dict()


def instruction_to_dict(instruction: Instruction) -> dict[str, Any]:
    return instruction.to_dict()


def terminator_to_dict(terminator: Terminator) -> dict[str, Any]:
    return terminator.to_dict()


def declaration_to_dict(declaration: Declaration) -> dict[str, Any]:
    return declaration.to_dict()


def symbol_ref_from_mapping(data: Mapping[str, Any]) -> SymbolRef:
    _reject_unknown_keys(data, context="symbol ref", allowed=SYMBOL_REF_KEYS)
    if str(_require_mapping_field(data, "kind", context="symbol ref")) != "SymbolRef":
        raise ValueError("symbol ref.kind must be SymbolRef")
    return SymbolRef(
        name=str(_require_mapping_field(data, "name", context="symbol ref")),
        module=(None if "module" not in data else str(data["module"])),
    )


def type_ref_from_mapping(data: Mapping[str, Any]) -> TypeRef:
    _reject_unknown_keys(data, context="type ref", allowed=TYPE_REF_KEYS)
    if str(_require_mapping_field(data, "kind", context="type ref")) != "TypeRef":
        raise ValueError("type ref.kind must be TypeRef")
    return TypeRef(name=str(_require_mapping_field(data, "name", context="type ref")))


def type_parameter_from_mapping(data: Mapping[str, Any]) -> TypeParameter:
    _reject_unknown_keys(data, context="type parameter", allowed=TYPE_PARAMETER_KEYS)
    if (
        str(_require_mapping_field(data, "kind", context="type parameter"))
        != "TypeParameter"
    ):
        raise ValueError("type parameter.kind must be TypeParameter")
    return TypeParameter(
        name=str(_require_mapping_field(data, "name", context="type parameter")),
        constraint=(
            None
            if "constraint" not in data
            else symbol_ref_from_mapping(data["constraint"])
        ),
    )


def import_from_mapping(data: Mapping[str, Any]) -> Import:
    _reject_unknown_keys(data, context="import", allowed=IMPORT_KEYS)
    if str(_require_mapping_field(data, "kind", context="import")) != "Import":
        raise ValueError("import.kind must be Import")
    return Import(
        module=str(_require_mapping_field(data, "module", context="import")),
        names=_coerce_string_list(data.get("names")),
        alias=(None if "alias" not in data else str(data["alias"])),
    )


def parameter_from_mapping(data: Mapping[str, Any]) -> Parameter:
    _reject_unknown_keys(data, context="parameter", allowed=PARAMETER_KEYS)
    if str(_require_mapping_field(data, "kind", context="parameter")) != "Parameter":
        raise ValueError("parameter.kind must be Parameter")
    return Parameter(
        name=str(_require_mapping_field(data, "name", context="parameter")),
        type=type_ref_from_mapping(
            _require_mapping_field(data, "type", context="parameter")
        ),
    )


def local_binding_from_mapping(data: Mapping[str, Any]) -> LocalBinding:
    _reject_unknown_keys(data, context="local binding", allowed=LOCAL_BINDING_KEYS)
    if (
        str(_require_mapping_field(data, "kind", context="local binding"))
        != "LocalBinding"
    ):
        raise ValueError("local binding.kind must be LocalBinding")
    return LocalBinding(
        name=str(_require_mapping_field(data, "name", context="local binding")),
        type=(None if "type" not in data else type_ref_from_mapping(data["type"])),
        mutable=bool(data.get("mutable", False)),
    )


def named_argument_from_mapping(data: Mapping[str, Any]) -> NamedArgument:
    _reject_unknown_keys(data, context="named argument", allowed=NAMED_ARGUMENT_KEYS)
    if (
        str(_require_mapping_field(data, "kind", context="named argument"))
        != "NamedArgument"
    ):
        raise ValueError("named argument.kind must be NamedArgument")
    return NamedArgument(
        name=str(_require_mapping_field(data, "name", context="named argument")),
        value=value_from_mapping(
            _require_mapping_field(data, "value", context="named argument")
        ),
    )


def value_from_mapping(data: Mapping[str, Any]) -> Value:
    kind = str(_require_mapping_field(data, "kind", context="value"))
    _validate_choice(kind, field_name="value.kind", allowed=VALUE_KINDS)

    if kind == "LocalRef":
        _reject_unknown_keys(data, context="local ref", allowed=LOCAL_REF_KEYS)
        return LocalRef(name=str(_require_mapping_field(data, "name", context="local ref")))

    if kind == "ParameterRef":
        _reject_unknown_keys(data, context="parameter ref", allowed=PARAMETER_REF_KEYS)
        return ParameterRef(
            name=str(_require_mapping_field(data, "name", context="parameter ref"))
        )

    if kind == "SymbolRef":
        return symbol_ref_from_mapping(data)

    if kind == "Literal":
        _reject_unknown_keys(data, context="literal", allowed=LITERAL_KEYS)
        return Literal(
            type=type_ref_from_mapping(
                _require_mapping_field(data, "type", context="literal")
            ),
            value=_require_mapping_field(data, "value", context="literal"),
        )

    if kind == "FieldValue":
        _reject_unknown_keys(data, context="field value", allowed=FIELD_VALUE_KEYS)
        return FieldValue(
            base=value_from_mapping(
                _require_mapping_field(data, "base", context="field value")
            ),
            field=str(_require_mapping_field(data, "field", context="field value")),
        )

    if kind == "DirectCall":
        _reject_unknown_keys(data, context="direct call", allowed=DIRECT_CALL_KEYS)
        return DirectCall(
            callee=symbol_ref_from_mapping(
                _require_mapping_field(data, "callee", context="direct call")
            ),
            arguments=[
                value_from_mapping(argument) for argument in data.get("arguments", [])
            ],
            result_type=(
                None
                if "result_type" not in data
                else type_ref_from_mapping(data["result_type"])
            ),
            await_=bool(data.get("await", False)),
        )

    _reject_unknown_keys(data, context="construct value", allowed=CONSTRUCT_VALUE_KEYS)
    return ConstructValue(
        type=type_ref_from_mapping(
            _require_mapping_field(data, "type", context="construct value")
        ),
        constructor=(
            None
            if "constructor" not in data
            else symbol_ref_from_mapping(data["constructor"])
        ),
        arguments=[
            value_from_mapping(argument) for argument in data.get("arguments", [])
        ],
        fields=[
            named_argument_from_mapping(field_item)
            for field_item in data.get("fields", [])
        ],
    )


def instruction_from_mapping(data: Mapping[str, Any]) -> Instruction:
    kind = str(_require_mapping_field(data, "kind", context="instruction"))
    _validate_choice(kind, field_name="instruction.kind", allowed=INSTRUCTION_KINDS)

    if kind == "Bind":
        _reject_unknown_keys(data, context="bind instruction", allowed=BIND_KEYS)
        return Bind(
            binding=local_binding_from_mapping(
                _require_mapping_field(data, "binding", context="bind instruction")
            ),
            value=value_from_mapping(
                _require_mapping_field(data, "value", context="bind instruction")
            ),
        )

    if kind == "Eval":
        _reject_unknown_keys(data, context="eval instruction", allowed=EVAL_KEYS)
        return Eval(
            value=value_from_mapping(
                _require_mapping_field(data, "value", context="eval instruction")
            )
        )

    _reject_unknown_keys(
        data,
        context="error propagation placeholder",
        allowed=ERROR_PROPAGATION_KEYS,
    )
    return ErrorPropagationPlaceholder(
        source=value_from_mapping(
            _require_mapping_field(
                data, "source", context="error propagation placeholder"
            )
        ),
        binding=(
            None
            if "binding" not in data
            else local_binding_from_mapping(data["binding"])
        ),
        error_adapter=(
            None
            if "error_adapter" not in data
            else symbol_ref_from_mapping(data["error_adapter"])
        ),
        strategy=str(data.get("strategy", "result_branch")),
        comment=(None if "comment" not in data else str(data["comment"])),
    )


def terminator_from_mapping(data: Mapping[str, Any]) -> Terminator:
    kind = str(_require_mapping_field(data, "kind", context="terminator"))
    _validate_choice(kind, field_name="terminator.kind", allowed=TERMINATOR_KINDS)

    if kind == "Jump":
        _reject_unknown_keys(data, context="jump terminator", allowed=JUMP_KEYS)
        return Jump(
            target_block=str(
                _require_mapping_field(data, "target_block", context="jump terminator")
            )
        )

    if kind == "Branch":
        _reject_unknown_keys(data, context="branch terminator", allowed=BRANCH_KEYS)
        return Branch(
            condition=value_from_mapping(
                _require_mapping_field(data, "condition", context="branch terminator")
            ),
            then_block=str(
                _require_mapping_field(data, "then_block", context="branch terminator")
            ),
            else_block=str(
                _require_mapping_field(data, "else_block", context="branch terminator")
            ),
        )

    _reject_unknown_keys(data, context="return terminator", allowed=RETURN_KEYS)
    return Return(
        value=(None if "value" not in data else value_from_mapping(data["value"]))
    )


def basic_block_from_mapping(data: Mapping[str, Any]) -> BasicBlock:
    _reject_unknown_keys(data, context="basic block", allowed=BASIC_BLOCK_KEYS)
    if str(_require_mapping_field(data, "kind", context="basic block")) != "BasicBlock":
        raise ValueError("basic block.kind must be BasicBlock")
    return BasicBlock(
        name=str(_require_mapping_field(data, "name", context="basic block")),
        instructions=[
            instruction_from_mapping(instruction)
            for instruction in data.get("instructions", [])
        ],
        terminator=terminator_from_mapping(
            _require_mapping_field(data, "terminator", context="basic block")
        ),
    )


def struct_field_from_mapping(data: Mapping[str, Any]) -> StructField:
    _reject_unknown_keys(data, context="struct field", allowed=STRUCT_FIELD_KEYS)
    if str(_require_mapping_field(data, "kind", context="struct field")) != "StructField":
        raise ValueError("struct field.kind must be StructField")
    return StructField(
        name=str(_require_mapping_field(data, "name", context="struct field")),
        type=type_ref_from_mapping(
            _require_mapping_field(data, "type", context="struct field")
        ),
        visibility=str(data.get("visibility", "private")),
    )


def enum_variant_from_mapping(data: Mapping[str, Any]) -> EnumVariant:
    _reject_unknown_keys(data, context="enum variant", allowed=ENUM_VARIANT_KEYS)
    if str(_require_mapping_field(data, "kind", context="enum variant")) != "EnumVariant":
        raise ValueError("enum variant.kind must be EnumVariant")
    return EnumVariant(
        name=str(_require_mapping_field(data, "name", context="enum variant")),
        payload=[type_ref_from_mapping(item) for item in data.get("payload", [])],
    )


def function_from_mapping(data: Mapping[str, Any]) -> Function:
    _reject_unknown_keys(data, context="function", allowed=FUNCTION_KEYS)
    if str(_require_mapping_field(data, "kind", context="function")) != "Function":
        raise ValueError("function.kind must be Function")
    return Function(
        name=str(_require_mapping_field(data, "name", context="function")),
        visibility=str(data.get("visibility", "private")),
        type_parameters=[
            type_parameter_from_mapping(item)
            for item in data.get("type_parameters", [])
        ],
        parameters=[
            parameter_from_mapping(parameter) for parameter in data.get("parameters", [])
        ],
        return_type=(
            None
            if "return_type" not in data
            else type_ref_from_mapping(data["return_type"])
        ),
        effects=_coerce_string_list(data.get("effects")),
        async_=bool(data.get("async", False)),
        entry_block=str(data.get("entry_block", "entry")),
        blocks=[basic_block_from_mapping(block) for block in data.get("blocks", [])],
        notes=_coerce_string_list(data.get("notes")),
    )


def struct_type_from_mapping(data: Mapping[str, Any]) -> StructType:
    _reject_unknown_keys(data, context="struct type", allowed=STRUCT_TYPE_KEYS)
    if str(_require_mapping_field(data, "kind", context="struct type")) != "StructType":
        raise ValueError("struct type.kind must be StructType")
    return StructType(
        name=str(_require_mapping_field(data, "name", context="struct type")),
        visibility=str(data.get("visibility", "private")),
        fields=[
            struct_field_from_mapping(field_item) for field_item in data.get("fields", [])
        ],
        notes=_coerce_string_list(data.get("notes")),
    )


def enum_type_from_mapping(data: Mapping[str, Any]) -> EnumType:
    _reject_unknown_keys(data, context="enum type", allowed=ENUM_TYPE_KEYS)
    if str(_require_mapping_field(data, "kind", context="enum type")) != "EnumType":
        raise ValueError("enum type.kind must be EnumType")
    return EnumType(
        name=str(_require_mapping_field(data, "name", context="enum type")),
        visibility=str(data.get("visibility", "private")),
        variants=[
            enum_variant_from_mapping(item) for item in data.get("variants", [])
        ],
        notes=_coerce_string_list(data.get("notes")),
    )


def newtype_from_mapping(data: Mapping[str, Any]) -> Newtype:
    _reject_unknown_keys(data, context="newtype", allowed=NEWTYPE_KEYS)
    if str(_require_mapping_field(data, "kind", context="newtype")) != "Newtype":
        raise ValueError("newtype.kind must be Newtype")
    return Newtype(
        name=str(_require_mapping_field(data, "name", context="newtype")),
        visibility=str(data.get("visibility", "private")),
        target=type_ref_from_mapping(
            _require_mapping_field(data, "target", context="newtype")
        ),
        notes=_coerce_string_list(data.get("notes")),
    )


def trait_member_from_mapping(data: Mapping[str, Any]) -> TraitMember:
    _reject_unknown_keys(data, context="trait member", allowed=TRAIT_MEMBER_KEYS)
    if str(_require_mapping_field(data, "kind", context="trait member")) != "TraitMember":
        raise ValueError("trait member.kind must be TraitMember")
    return TraitMember(
        name=str(_require_mapping_field(data, "name", context="trait member")),
        type_parameters=[
            type_parameter_from_mapping(item)
            for item in data.get("type_parameters", [])
        ],
        parameters=[
            parameter_from_mapping(parameter) for parameter in data.get("parameters", [])
        ],
        return_type=(
            None
            if "return_type" not in data
            else type_ref_from_mapping(data["return_type"])
        ),
        effects=_coerce_string_list(data.get("effects")),
        async_=bool(data.get("async", False)),
    )


def trait_surface_from_mapping(data: Mapping[str, Any]) -> TraitSurface:
    _reject_unknown_keys(data, context="trait surface", allowed=TRAIT_SURFACE_KEYS)
    if (
        str(_require_mapping_field(data, "kind", context="trait surface"))
        != "TraitSurface"
    ):
        raise ValueError("trait surface.kind must be TraitSurface")
    return TraitSurface(
        name=str(_require_mapping_field(data, "name", context="trait surface")),
        visibility=str(data.get("visibility", "private")),
        type_parameters=[
            type_parameter_from_mapping(item)
            for item in data.get("type_parameters", [])
        ],
        members=[trait_member_from_mapping(item) for item in data.get("members", [])],
        notes=_coerce_string_list(data.get("notes")),
    )


def impl_surface_from_mapping(data: Mapping[str, Any]) -> ImplSurface:
    _reject_unknown_keys(data, context="impl surface", allowed=IMPL_SURFACE_KEYS)
    if (
        str(_require_mapping_field(data, "kind", context="impl surface"))
        != "ImplSurface"
    ):
        raise ValueError("impl surface.kind must be ImplSurface")
    return ImplSurface(
        trait=(None if "trait" not in data else symbol_ref_from_mapping(data["trait"])),
        for_type=type_ref_from_mapping(
            _require_mapping_field(data, "for_type", context="impl surface")
        ),
        methods=[function_from_mapping(item) for item in data.get("methods", [])],
        notes=_coerce_string_list(data.get("notes")),
    )


def test_surface_from_mapping(data: Mapping[str, Any]) -> TestSurface:
    _reject_unknown_keys(data, context="test surface", allowed=TEST_SURFACE_KEYS)
    if (
        str(_require_mapping_field(data, "kind", context="test surface"))
        != "TestSurface"
    ):
        raise ValueError("test surface.kind must be TestSurface")
    return TestSurface(
        name=str(_require_mapping_field(data, "name", context="test surface")),
        entry_block=str(data.get("entry_block", "entry")),
        blocks=[basic_block_from_mapping(block) for block in data.get("blocks", [])],
        notes=_coerce_string_list(data.get("notes")),
    )


def declaration_from_mapping(data: Mapping[str, Any]) -> Declaration:
    kind = str(_require_mapping_field(data, "kind", context="declaration"))
    _validate_choice(kind, field_name="declaration.kind", allowed=DECLARATION_KINDS)

    if kind == "Function":
        return function_from_mapping(data)
    if kind == "StructType":
        return struct_type_from_mapping(data)
    if kind == "EnumType":
        return enum_type_from_mapping(data)
    if kind == "Newtype":
        return newtype_from_mapping(data)
    if kind == "TraitSurface":
        return trait_surface_from_mapping(data)
    if kind == "ImplSurface":
        return impl_surface_from_mapping(data)
    return test_surface_from_mapping(data)


def module_from_mapping(data: Mapping[str, Any]) -> Module:
    _reject_unknown_keys(data, context="module", allowed=MODULE_KEYS)
    if str(_require_mapping_field(data, "kind", context="module")) != "Module":
        raise ValueError("module.kind must be Module")
    declarations_payload = data.get("declarations")
    if declarations_payload is None and "functions" in data:
        declarations_payload = data["functions"]
    return Module(
        name=str(_require_mapping_field(data, "name", context="module")),
        source_file=(None if "source_file" not in data else str(data["source_file"])),
        imports=[import_from_mapping(item) for item in data.get("imports", [])],
        declarations=[
            declaration_from_mapping(item)
            for item in (declarations_payload or [])
        ],
    )


def program_from_mapping(data: Mapping[str, Any]) -> Program:
    _reject_unknown_keys(data, context="program", allowed=PROGRAM_KEYS)
    if str(_require_mapping_field(data, "kind", context="program")) != "Program":
        raise ValueError("program.kind must be Program")
    return Program(
        schema_version=str(data.get("schema_version", IR_SCHEMA_VERSION)),
        modules=[module_from_mapping(module) for module in data.get("modules", [])],
    )


def program_to_json(program: Program, *, indent: int = 2) -> str:
    return json.dumps(program.to_dict(), indent=indent, ensure_ascii=True) + "\n"


def module_to_json(module: Module, *, indent: int = 2) -> str:
    return json.dumps(module.to_dict(), indent=indent, ensure_ascii=True) + "\n"


def program_from_json(payload: str) -> Program:
    data = json.loads(payload)
    if not isinstance(data, dict):
        raise ValueError("program JSON root must be an object")
    return program_from_mapping(data)


def module_from_json(payload: str) -> Module:
    data = json.loads(payload)
    if not isinstance(data, dict):
        raise ValueError("module JSON root must be an object")
    return module_from_mapping(data)
