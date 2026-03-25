# Semantics

## Goal

This document records the baseline semantic model needed for parser, analysis, and tooling work.

## Local Reasoning

Axiom prioritizes local reasoning. A reader should be able to understand the main behavior of a function from:

- its signature
- its declared effects
- its error type
- its module imports

## Module Identity

- A module is identified by its declared module path.
- A module path must match the file path under `src/`.
- Import paths are explicit and stable.

## Bindings

### `let`

`let` introduces an immutable binding.

### `var`

`var` introduces a mutable binding. Mutation must remain explicit.

## Visibility

### `pub`

Public API surface visible outside the module or package boundary defined by the eventual toolchain.

### `internal`

Visible within the intended internal compilation boundary. The exact package boundary should remain stable once defined by the compiler.

### Private by Omission

Visible only within the declaring module.

## Data Semantics

### Structs

Structs define named-field product types.

### Enums

Enums define tagged sum types and should support exhaustive matching.

### Newtypes

Newtypes create distinct wrapper types for domain clarity without relying on implicit conversion.

## Error Semantics

Axiom uses structured errors rather than exception-driven control flow for normal business failures.

- recoverable domain failures should be modeled with `Result<T, E>`
- `E` should be enumerable and documented
- propagation must stay explicit

The `?` operator is treated as explicit error propagation because it operates only on `Result` and remains visible in source.

## Option and Result

`Option` and `Result` are language-level concepts rather than ordinary library aliases. Tooling should understand them when building diagnostics, summaries, and control-flow analysis.

## Effects

Effects are part of function semantics, not merely annotations.

- omitted `effects` means the function is intended to be pure
- declared `effects` form part of the callable contract
- calling an effectful function without declaring a covering effect set is an error

## Async Semantics

- asynchronous functions must be declared with `async`
- suspension points must use `await`
- no implicit async lifting is allowed

Async behavior and effect declarations are orthogonal. An async function may still be pure or effectful depending on its operations.

## Match Semantics

`match` is a semantic branching construct over enums, structs, tuples, and other supported patterns.

The intended direction is exhaustive matching for closed enums and explicit handling of branches.

## Trait Semantics

Traits express interfaces and generic constraints.

This repository assumes:

- trait lookup must remain predictable
- import order must not influence type choice
- implementation selection should avoid hidden magic

## Assumptions and Open Questions

- Exact primitive scalar set is not frozen in this bootstrap.
- Ownership, borrowing, and lifetime semantics are intentionally unspecified here.
- The exact boundary of `internal` visibility is deferred to compiler and package model work.
