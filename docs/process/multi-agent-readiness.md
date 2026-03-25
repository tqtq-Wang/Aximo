# Multi-Agent Readiness

## Purpose

This document defines when Axiom is ready for formal multi-Codex parallel development and what must be true before scaling the number of active agents.

## Readiness Levels

### Level 0: Bootstrap Only

Characteristics:

- repository structure exists
- documents and schemas exist
- no stable validation loop
- no source control workflow

Allowed parallelism:

- at most two or three agents
- documentation-only or fixture-only tasks

### Level 1: Controlled Parallelism

Characteristics:

- git repository initialized
- validation scripts runnable
- CI checks repository contracts
- process docs define ownership

Allowed parallelism:

- documentation, schema, examples, tests, and isolated compiler slices can proceed in parallel

### Level 2: Formal Multi-Codex Development

Characteristics:

- parser and AST pipeline exists
- diagnostics output exists
- snapshot updates are systematic
- schema changes are versioned and review-gated

Allowed parallelism:

- dedicated agents per compiler subsystem
- concurrent work on parser, diagnostics, summary, and fixtures

### Level 3: Product-Directed Parallelism

Characteristics:

- backend-oriented prototypes exist
- compiler summary is consumed by internal AI workflows
- compatibility and release criteria are defined

Allowed parallelism:

- language work and internal service pilot work can run together

## Readiness Checklist

To move into formal multi-Codex development, the following must be true:

- `git` repository exists
- `docs/spec/` is stable enough for at least one implementation sprint
- schema names and top-level fields are stable
- `tools/scripts/validate-spec.sh` runs successfully
- `tools/scripts/validate-examples.sh` runs successfully
- CI runs docs build and validation scripts
- task ownership is assigned by slice, not by vague feature name

## Current Position

The repository is targeting Level 1 after this setup pass:

- structure exists
- process docs exist
- validation scripts exist
- CI exists

The next gate is Level 2, which requires a functioning parser-to-AST pipeline.

## Promotion Gates

### Level 0 -> Level 1

- complete repository bootstrap
- add process docs
- add CI
- initialize git

### Level 1 -> Level 2

- implement parser MVP
- validate AST output against schema
- emit structured parser diagnostics

### Level 2 -> Level 3

- emit compiler summaries from real modules
- validate a small backend-style prototype
- measure AI workflow quality on real change tasks
