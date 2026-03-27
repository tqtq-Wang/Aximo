# IR Core

`compiler/ir` defines the formal internal IR contract for Axiom.

This layer exists so semantic lowering, backend adaptation, and later contract checks all meet on one in-repo shape instead of inventing parallel dictionaries or coupling directly to parser/AST nodes.

## Role

Version 1 of the IR is intended to be:

- readable in code review
- constructable directly by Slice I lowering
- serializable and round-trippable through deterministic JSON
- explicit about control flow, direct call boundaries, and error-propagation boundaries
- broad enough to describe the current example-backed module surface, not just executable functions

The public API is exposed from `compiler.ir`.

## IR Is Not AST

AST remains source-shaped. It preserves parser-facing declaration syntax, source terminology, and source-local facts.

IR is the compiler-facing contract after frontend structure starts getting normalized:

- `Module` carries explicit `imports` and `declarations`
- executable code uses explicit `BasicBlock` plus terminator structure
- direct calls are operational values
- `?` is represented by `ErrorPropagationPlaceholder` instead of remaining parser sugar
- declaration nodes have stable Python types instead of untyped dict payloads

That means AST is still the frontend contract, while IR is the internal handoff contract.

## IR Is Not LLVM IR

This IR is still language-shaped.

It intentionally does not model:

- SSA or PHI nodes
- registers or virtual registers
- target ABI details
- LLVM instruction sets or type encodings
- backend-specific calling conventions
- optimizer-specific data structures

The goal is to be stable enough for lowering and backend preparation without leaking LLVM concerns upward.

## Why Module Needs Imports And Declarations

Slice H cannot stop at `Module(functions=[...])`.

Current examples already require module-level facts beyond executable bodies:

- imports matter for symbol resolution and stable module contracts
- structs, enums, newtypes, traits, impls, and tests exist at top level in the checked-in examples
- Slice I needs one official declaration surface to target instead of creating ad hoc parallel shapes

For that reason the normative module shape is:

- `Module.imports: list[Import]`
- `Module.declarations: list[Declaration]`

`Module.functions` still exists as a derived convenience property, but `declarations` is the formal contract.

## Current Declaration Contract

The first declaration set is intentionally small but formal:

- `Function`: backend-facing executable declaration with blocks, terminators, parameters, effects, async marker, and type parameters
- `StructType`: backend-facing type declaration for named fields
- `EnumType`: backend-facing type declaration for variants and optional payload types
- `Newtype`: backend-facing declaration for a named wrapper target
- `TraitSurface`: surface-only placeholder for trait API shape
- `ImplSurface`: surface-only placeholder for impl ownership plus method bodies
- `TestSurface`: surface-only placeholder for test entry/body structure

`TraitSurface`, `ImplSurface`, and `TestSurface` are formal IR nodes, but they do not claim that full lowering/runtime/backend semantics are complete. They exist so the IR contract can carry the current module surface without forcing Slice I to invent a shadow schema.

## Current Scope

The first IR version covers the minimum concepts required by RFC 0011 and the current examples:

- `Program` and `Module`
- `Import`
- declaration nodes listed above
- `TypeParameter`, `Parameter`, `LocalBinding`
- `BasicBlock`
- `Bind` and `Eval` instructions
- `Branch`, `Jump`, and `Return` terminators
- `DirectCall`
- references for parameters, locals, symbols, literals, and field reads
- `ConstructValue` for constructor-style values such as enum/newtype/aggregate construction
- `ErrorPropagationPlaceholder` as the explicit pre-lowering marker for `Result`-style propagation

`ErrorPropagationPlaceholder` is deliberate. Slice H still does not lower `?` into explicit control flow. Slice I can consume this node and expand it into blocks and branches without inventing another upstream contract.

## Non-Goals In V1

This module does not:

- perform lowering from parser output
- define a machine-level backend IR
- commit to SSA
- finalize async lowering strategy
- finalize ownership or runtime implementation details
- replace diagnostics or compiler summary responsibilities

## Serialization

Every public node supports `to_dict()`. The module also provides:

- `program_to_json()`
- `module_to_json()`
- `program_from_mapping()` / `program_from_json()`
- `module_from_mapping()` / `module_from_json()`
- `declaration_from_mapping()`

The JSON format is internal and versioned by `IR_SCHEMA_VERSION`. It is stable enough for in-repo consumers, but it is not yet a repository-wide external schema contract.

## Example

```python
from compiler.ir import (
    BasicBlock,
    Function,
    Import,
    Module,
    Parameter,
    ParameterRef,
    Program,
    Return,
    StructField,
    StructType,
    SymbolRef,
    TraitMember,
    TraitSurface,
    TypeParameter,
    TypeRef,
    program_to_json,
)

program = Program(
    modules=[
        Module(
            name="app",
            imports=[
                Import(module="domain.user.repo", names=["UserRepo"]),
            ],
            declarations=[
                StructType(
                    name="CreateUserInput",
                    visibility="public",
                    fields=[
                        StructField(name="email", type=TypeRef("String"), visibility="public"),
                    ],
                ),
                TraitSurface(
                    name="UserRepo",
                    visibility="public",
                    members=[
                        TraitMember(
                            name="exists_by_email",
                            parameters=[
                                Parameter(name="email", type=TypeRef("Email")),
                            ],
                            return_type=TypeRef("Result<Bool, RepoError>"),
                        )
                    ],
                ),
                Function(
                    name="bootstrap",
                    visibility="public",
                    type_parameters=[
                        TypeParameter(
                            name="R",
                            constraint=SymbolRef(module="domain.user.repo", name="UserRepo"),
                        )
                    ],
                    parameters=[
                        Parameter(name="repo", type=TypeRef("R")),
                        Parameter(name="input", type=TypeRef("CreateUserInput")),
                    ],
                    return_type=TypeRef("Result<User, CreateUserError>"),
                    blocks=[
                        BasicBlock(
                            name="entry",
                            terminator=Return(ParameterRef("input")),
                        )
                    ],
                ),
            ],
        )
    ]
)

payload = program_to_json(program)
```

