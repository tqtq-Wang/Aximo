# Effects

## Goal

Axiom uses explicit effect declarations to make side effects visible in signatures and available to compiler analysis.

## Syntax

```axiom
pub fn create_user(input: CreateUserInput) -> Result<User, CreateUserError>
    effects [db.read, db.write]
{
    ...
}
```

## Why Effects Matter

Effects answer questions that both humans and AI systems need quickly:

- does this function perform I/O?
- does it read from or write to storage?
- does it make network calls?
- is it suitable for pure reuse?

## Effect Naming

The RFC examples use dotted identifiers such as:

- `db.read`
- `db.write`
- `net.call`
- `log.write`

This bootstrap treats effect names as stable dotted identifiers in source and structured outputs.

## Semantic Rules

- a function body may not perform undeclared effects
- an effectful callee requires the caller to declare a covering effect set
- pure functions must not accidentally contain effectful calls
- effect changes on public functions are relevant to breaking-change analysis

## Categories in Current Examples

### Storage

- `db.read`
- `db.write`

### Network

- `net.call`

### Logging

- `log.write`

## What Effects Are Not

Effects are not:

- hidden runtime annotations
- permissionless comments
- macro-expanded behavior

They are part of the callable interface and must be reflected in compiler summaries.

## Tooling Expectations

The future compiler should expose:

- declared effect set per function
- effect propagation through calls
- undeclared effect diagnostics
- public API effect diffs

## Open Questions

- Should effect subsets or aliases exist in a later phase?
- How should standard effect vocabularies be versioned?
- How should async runtime interactions map onto effect categories?
