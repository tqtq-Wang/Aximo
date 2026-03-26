# Glossary

## Purpose

This glossary defines canonical repository terminology. Other documents should prefer these terms exactly to avoid drift across docs, schemas, examples, and compiler outputs.

## Terms

### Axiom

The language and toolchain project defined by this repository.

### Module

A source file with a `module` declaration whose module path matches its file path under `src/`.

### Module Path

A dotted identifier path such as `domain.user.service`.

### Symbol

A named program element such as a function, struct, enum, trait, newtype, or test.

### Visibility

The access level of a symbol.

Canonical values:

- `pub`
- `internal`
- private by omission

### Effect

A statically declared capability or side-effect category attached to a function through an `effects [...]` clause.

Examples used in the RFC and this repository:

- `db.read`
- `db.write`
- `net.call`
- `log.write`

### Pure Function

A function with no declared effects and no effectful operations in its body.

### Structured Error

A documented, enumerable error outcome modeled through `Result<T, E>`, usually where `E` is an enum.

### Diagnostic

A structured compiler message describing an error, warning, or informational issue, with machine-readable location data.

### Compiler Summary

A machine-readable semantic summary of a module containing exports, types, effects, errors, calls, diagnostics, and breaking-change analysis.

### Breaking Change

A public API change that invalidates existing clients, such as removed exports, changed signatures, or expanded effects on public functions.

### Project Layout

The fixed directory and file organization convention for Axiom projects.

### Local Reasoning

The property that a human or AI can understand a code fragment mainly from the current file and a small set of direct dependencies.

### Low Magic

An explicit design stance against hidden control flow and hidden semantics such as strong macro systems, implicit imports, or implicit conversions.

### Cost Model

The documented explanation of which language operations are expected to be cheap, which may allocate or dispatch dynamically, and which boundaries should remain explicit to users and tooling.

### Runtime Boundary

The point where language semantics rely on executor, scheduler, allocator, panic, or other runtime services rather than plain lowered control flow.

### Fixture

A repository artifact used as an input or expected output for compiler and tooling validation.

### Snapshot

A checked-in expected structured output, typically compiler summary JSON, used to detect semantic drift.
