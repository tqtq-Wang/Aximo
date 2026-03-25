# Type System

## Scope

This document defines the initial type-system surface needed by the repository bootstrap. It intentionally stays within RFC v0.1 boundaries.

## Core Properties

- static
- strong
- explicit
- oriented toward readable domain modeling rather than advanced type-level tricks

## Type Forms in Scope

### Named Product Types

`struct` declarations with named fields.

### Named Sum Types

`enum` declarations with explicit variants.

### Distinct Wrapper Types

`newtype` declarations for domain-specific wrappers.

### Function Types

Function signatures include:

- parameters
- return type
- async marker when applicable
- effect clause when applicable

### Generic Parameters

Generic parameters are allowed where directly expressed in signatures.

Current bootstrap assumption:

- generic constraints use a direct `T: Trait` style
- advanced higher-kinded or dependent type features are out of scope

### Trait-Based Abstraction

Traits provide interface and constraint semantics without hidden inference machinery.

## Language-Level Special Types

### `Option<T>`

Represents an explicit optional value.

### `Result<T, E>`

Represents a success-or-error value where `E` is a structured error type.

## Canonical Domain Modeling Guidance

Prefer:

- enums for finite business states and errors
- newtypes for domain identifiers and validated wrappers
- explicit input and output structs for service boundaries

Avoid:

- using raw scalar types where domain meaning matters
- overly generic error unions that destroy documentation quality

## Open Areas Intentionally Deferred

This bootstrap does not finalize:

- full primitive type catalog
- numeric coercion rules
- trait object or dynamic dispatch semantics
- ownership or memory semantics
- advanced inference rules

## Implications for Tooling

Future compiler work should ensure the type system can be summarized structurally in compiler output:

- exported type names
- kind of each type
- fields or variants
- referenced error types
- generic parameter list when relevant
