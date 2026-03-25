# Roadmap

## Direction

Axiom is being developed as a language and toolchain for AI-assisted backend engineering. The roadmap favors stable contracts, analyzable semantics, and predictable project structure before advanced optimization or ecosystem breadth.

## Milestones

### M0: Repository Bootstrap

Status: in progress

Goals:

- establish monorepo layout
- publish initial spec set
- publish JSON schema drafts
- add example projects
- define AI collaboration protocol
- define test fixture and snapshot conventions

Exit criteria:

- required root files exist
- spec, RFC, and decision records are cross-referenced
- examples compile conceptually against the current syntax draft
- schema naming matches spec terminology
- repository validation scripts are executable
- minimal CI runs docs build and repository contract checks
- multi-agent workflow documents define task boundaries

### M1: Front-End Compiler Skeleton

Goals:

- define token inventory
- implement parser target grammar for core declarations
- stabilize AST node taxonomy
- parse valid example projects into schema-shaped AST

Exit criteria:

- parser fixtures in `tests/parser/valid/` and `tests/parser/invalid/` are runnable
- AST output can be validated against `schemas/ast.schema.json`

### M2: Name Resolution and Module Validation

Goals:

- module-to-path validation
- import resolution
- visibility checks
- duplicate symbol checks

Exit criteria:

- module and import diagnostics align with `docs/spec/modules.md`
- parser and module diagnostics snapshots are stable

### M3: Type System MVP

Goals:

- structs, enums, newtypes
- `Option` and `Result`
- function signatures
- trait declarations and generic constraints used in examples
- match exhaustiveness baseline

Exit criteria:

- type summaries for examples are emitted
- type diagnostics match `docs/spec/type-system.md`

### M4: Effect and Error Analysis MVP

Goals:

- function effect declaration checks
- effect propagation checks
- error-flow extraction from `Result`
- breaking-change detection for public API effect expansion

Exit criteria:

- compiler summary contains stable effect and error data
- diagnostics align with `docs/spec/effects.md` and `docs/spec/diagnostics.md`

### M5: Compiler Summary and Tooling Contracts

Goals:

- emit module summary JSON
- emit diagnostics JSON
- snapshot public API changes
- provide summary consumption guidance for AI tools

Exit criteria:

- `schemas/compiler-summary.schema.json` is implemented by the compiler
- examples produce stable summary snapshots

### M6: Backend-Oriented Workflow Trial

Goals:

- validate Axiom against small real backend-style services
- evaluate ergonomics for domain modules, repo abstractions, and effect boundaries
- measure AI-assisted development flow against incumbent backend languages

Exit criteria:

- at least one non-trivial internal service prototype exists
- AI workflow gains and pain points are documented

## Open Questions for Later Milestones

- runtime packaging model details
- standard library scope
- interoperability packaging details
- debug build behavior beyond placeholder semantics
- deployment tooling and lockfile format
