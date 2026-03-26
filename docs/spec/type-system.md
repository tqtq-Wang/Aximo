# Type System

## Scope

This document defines the initial type-system surface needed by the repository bootstrap. It intentionally stays within RFC v0.1 boundaries.

## Core Properties

- static
- strong
- explicit
- oriented toward readable domain modeling rather than advanced type-level tricks
- intended to preserve a predictable cost model as backend work matures

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
- future implementation should prefer static dispatch by default; see RFC 0010

### Trait-Based Abstraction

Traits provide interface and constraint semantics without hidden inference machinery.

## Language-Level Special Types

### `Option<T>`

Represents an explicit optional value.

### `Result<T, E>`

Represents a success-or-error value where `E` is a structured error type.

The intended runtime direction is explicit control-flow lowering rather than exception-style business logic.

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
- trait object or dynamic dispatch semantics, pending RFC 0010
- ownership or memory semantics, pending RFC 0009
- advanced inference rules

## Implications for Tooling

Future compiler work should ensure the type system can be summarized structurally in compiler output:

- exported type names
- kind of each type
- fields or variants
- referenced error types
- generic parameter list when relevant
