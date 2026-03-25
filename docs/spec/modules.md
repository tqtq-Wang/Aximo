# Modules

## Goal

The module system should maximize predictability and minimize hidden namespace behavior.

## Module Declaration

Every source file begins with a `module` declaration:

```axiom
module domain.user.service
```

## Path Mapping Rule

Module path and file path must align.

Examples:

- `src/app.ax` -> `module app`
- `src/domain/user/service.ax` -> `module domain.user.service`

This invariant is a core AI-friendly property of the language and project layout.

## Imports

Imports are explicit:

```axiom
use domain.user.model.{User, UserId}
use domain.user.errors.CreateUserError
```

Rules:

- explicit imports are required
- wildcard imports are forbidden
- import paths should remain stable and predictable

## Visibility

Supported visibility levels:

- `pub`
- `internal`
- private by omission

## Module Family Convention

Domain areas should normally use:

- `model.ax`
- `service.ax`
- `repo.ax`
- `errors.ax`
- `tests.ax`

This convention is not cosmetic. It is used to reduce search cost and improve automated code generation stability.

## Constraints

The initial module system should avoid:

- implicit imports
- import-order-dependent behavior
- reflective module discovery
- framework-generated hidden modules

## Compiler Responsibilities

Future module analysis should check:

- module path and file path consistency
- unresolved imports
- duplicate visible names
- visibility violations

## Open Questions

- What exact compilation unit defines the `internal` boundary?
- How should re-export patterns be modeled in a future phase, if at all?
