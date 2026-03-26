# Implementation Kickoff

## Purpose

This document defines the conditions under which Axiom can formally transition from scaffolding into language implementation work.

## Kickoff Decision

The repository is considered implementation-ready when all of the following are true:

- source-of-truth spec documents exist
- machine-readable schemas exist
- example projects and fixtures exist
- repository checks pass locally
- CI passes on `main` for supported platforms
- task slices and ownership rules are documented
- branching and commit conventions are documented

## Current Readiness

With the current repository scaffolding, the next approved phase is:

- parser and AST implementation
- parser-facing diagnostics
- compiler summary generation scaffolding

The repository should not go backwards into uncontrolled scaffolding churn unless a concrete blocker is found.

## Allowed First Implementation Slices

### Slice D

- `compiler/parser/*`
- `compiler/ast/*`

Goal:

- parse existing `.ax` examples and fixtures into schema-aligned AST output

### Slice E

- `compiler/diagnostics/*`

Goal:

- emit structured parser diagnostics aligned with checked-in fixture JSON

### Slice F

- `compiler/summary/*`

Goal:

- prepare the first module summary pipeline shape against existing snapshot contracts

## Rules For First Implementation Sprint

- do not expand the language surface while implementing the parser
- prefer supporting existing examples over inventing new syntax
- treat fixture mismatches as either implementation bugs or spec bugs, never as silent cleanup
- if a slice needs a contract change, update spec first, then schema, then fixtures

## Exit Criteria For Implementation Sprint 1

- valid parser fixtures are accepted
- invalid parser fixtures produce structured diagnostics
- AST output can be validated against `schemas/ast.schema.json`
- no uncontrolled spec drift was introduced

## Status Update

The repository now has integrated parser, diagnostics, and summary implementations on `main`, plus an isolated LLVM feasibility spike.

That means implementation sprint 1 is no longer the main coordination problem.

The next coordination problem is sprint 2:

- formal IR introduction
- lowering boundaries
- backend adaptation through IR rather than parser or AST

Use [IR Implementation Kickoff](./ir-implementation-kickoff) together with RFC 0008 through RFC 0011 before assigning new backend-facing work.
