# Compiler Summary

## Goal

Compiler summary is a first-class output of the Axiom toolchain. The compiler should not only report errors; it should emit machine-readable semantic summaries that can drive documentation, AI tooling, and compatibility analysis.

## Minimum Module Summary

Each module summary should contain at least:

- module name
- imports
- exports
- type declarations
- function signatures
- effect sets
- error sets
- async flags
- call references
- diagnostics
- breaking-change entries

## Example Shape

```json
{
  "module": "domain.user.service",
  "exports": [
    {
      "name": "create_user",
      "kind": "function",
      "visibility": "public",
      "signature": "(CreateUserInput) -> Result<User, CreateUserError>",
      "effects": ["db.read", "db.write"],
      "errors": [
        "CreateUserError::InvalidName",
        "CreateUserError::InvalidEmail",
        "CreateUserError::AlreadyExists",
        "CreateUserError::StorageUnavailable"
      ],
      "async": false,
      "calls": [
        "domain.user.service.parse_email",
        "domain.user.repo.UserRepo.exists_by_email",
        "domain.user.repo.UserRepo.insert"
      ]
    }
  ],
  "diagnostics": [],
  "breaking_changes": []
}
```

## Why It Exists

Compiler summary exists to make semantic information available without requiring every downstream tool to re-derive it from raw source text.

Expected consumers:

- IDE and LSP tooling
- API diff tools
- documentation generators
- AI planning and refactoring systems
- test snapshot comparisons

## Stability Requirements

- field names should change rarely
- enum-like values should be documented and schema-backed
- public summary shape changes require spec and schema updates
- summary terms must match glossary terms

## Export Entries

Each export entry should describe:

- symbol name
- symbol kind
- visibility
- signature
- async marker
- declared effects
- enumerated errors
- direct call references when known

## Type Entries

Type entries should distinguish at least:

- `struct`
- `enum`
- `newtype`
- `alias` when introduced later

## Breaking-Change Entries

Initial breaking-change kinds referenced by the RFC and this repository:

- `removed_export`
- `signature_changed`
- `effect_expanded`
- `enum_variant_removed`

## Relationship to Diagnostics

Diagnostics remain separate structured artifacts, but module summaries may embed diagnostics relevant to that compilation unit for downstream consumers.

## Canonical Contract

The current machine-readable baseline lives in:

- `schemas/compiler-summary.schema.json`

## Open Questions

- Should there be a build-level aggregate summary in addition to module-level summaries?
- How should generic constraints be rendered in normalized signatures?
- How should trait implementations appear in later summaries?
