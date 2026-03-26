# Architecture

## Purpose of This Repository

This monorepo is organized around one principle: specification and machine-readable contracts must mature before large-scale implementation.

The repository therefore separates:

- narrative and normative documents
- machine-readable schemas
- example source fixtures
- compiler work areas
- validation and snapshot tooling

## Information Architecture

### `docs/`

The `docs/` directory is the primary human-readable source of truth and is published through VitePress.

Subareas:

- `docs/spec/`: normative repository-level specification
- `docs/rfc/`: problem statements, rationale, and scope framing
- `docs/decisions/`: short immutable decisions that constrain future design drift

### `schemas/`

The `schemas/` directory defines the machine-readable contracts the future compiler and tools are expected to emit or consume.

Current contracts:

- AST
- diagnostics
- compiler summary

### `examples/`

The `examples/` directory holds small Axiom projects that serve three roles at once:

- documentation examples
- parser and summary fixtures
- AI workflow calibration inputs

### `tests/`

The `tests/` directory is reserved for repository-level fixture contracts rather than application tests.

It is organized into:

- parser validity fixtures
- diagnostics expectation fixtures
- summary snapshots

### `compiler/`

The `compiler/` directory is the implementation surface for future work. At bootstrap time it only defines ownership boundaries:

- `lexer/`
- `parser/`
- `ast/`
- `diagnostics/`
- `summary/`
- `backend/`

The next implementation phase is expected to add:

- `ir/`

## Dependency Direction

The expected dependency flow is:

`docs/spec` -> `schemas` -> `examples` -> `tests` -> `compiler`

This means implementation should follow the documented contracts, not the other way around.

## Document Roles

### Spec Documents

Spec documents should answer:

- what the rule is
- what terminology is canonical
- what is explicitly in scope
- what remains intentionally unspecified

### RFC Documents

RFC documents should answer:

- why the repository chose a direction
- what tradeoff is being made
- which alternatives were consciously rejected

### Decision Records

Decision records should answer:

- which high-level choice is fixed for now
- what follow-on consequences future contributors must preserve

## Compiler Contract Surfaces

The repository currently assumes three structured outputs from the future front-end:

1. AST output for parsed modules
2. diagnostics output for errors and warnings
3. compiler summary output for semantic and public API analysis

The repository also now assumes one internal implementation handoff:

4. IR as the formal frontend-to-backend contract once implementation sprint 2 begins

These outputs are designed to support:

- LSP and IDE tooling
- AI code generation and refactoring agents
- snapshot testing
- breaking-change checks
- documentation generation

## AI Collaboration Shape

The repository is intentionally optimized for multi-agent work:

- module layout is predictable
- examples are narrow and task-oriented
- schema surfaces are centralized
- change synchronization rules live in `CONTRIBUTING_AI.md`

The desired outcome is that independent contributors can work on parser, diagnostics, summaries, and documentation without inventing incompatible local conventions.

## Assumptions

- The root `axiom.toml` acts as workspace metadata for this monorepo bootstrap.
- VitePress is documentation infrastructure only; it does not define language semantics.
- Example projects are normative fixtures only where the spec references them.
