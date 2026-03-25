# Task Slices

## Purpose

This document defines the initial parallel work decomposition for Axiom.

## Slice Principles

- each slice should have a narrow write surface
- each slice should have a clear validation target
- cross-slice edits require explicit coordination

## Recommended Initial Slices

### Slice A: Specification Stewardship

Write scope:

- `docs/spec/*.md`
- `docs/decisions/*.md`
- `docs/rfc/*.md`

Responsibilities:

- freeze terminology
- refine open questions
- prevent semantic drift

Validation target:

- `bash tools/scripts/validate-spec.sh`

### Slice B: Schema Contracts

Write scope:

- `schemas/*.json`

Responsibilities:

- stabilize AST contract
- stabilize diagnostics contract
- stabilize compiler summary contract

Validation target:

- `bash tools/scripts/validate-spec.sh`

### Slice C: Examples and Fixtures

Write scope:

- `examples/*`
- `tests/parser/*`
- `tests/diagnostics/*`
- `tests/snapshots/*`

Responsibilities:

- keep example projects aligned with spec
- maintain parser fixtures
- maintain diagnostics fixtures
- maintain snapshot inventory

Validation target:

- `bash tools/scripts/validate-examples.sh`
- `bash tools/scripts/generate-snapshots.sh`

### Slice D: Parser and AST

Write scope:

- `compiler/parser/*`
- `compiler/ast/*`

Responsibilities:

- parse core declarations
- serialize AST in schema-aligned form
- support valid and invalid parser fixtures

Validation target:

- parser fixture execution once implementation starts

### Slice E: Diagnostics

Write scope:

- `compiler/diagnostics/*`

Responsibilities:

- diagnostic code strategy
- source-span formatting
- JSON diagnostics emission

Validation target:

- diagnostics fixture comparison once implementation starts

### Slice F: Compiler Summary

Write scope:

- `compiler/summary/*`

Responsibilities:

- semantic export summary
- type summary
- breaking-change summary
- snapshot output alignment

Validation target:

- summary snapshot comparison once implementation starts

### Slice G: Tooling and CI

Write scope:

- `.github/workflows/*`
- `tools/scripts/*`
- root config files tied to automation

Responsibilities:

- validation automation
- docs build automation
- workflow hardening

Validation target:

- GitHub Actions
- local script execution

## Assignment Guidance

- give one worker one slice
- use the integrator for cross-slice tasks
- keep Slice A and Slice B tightly coordinated
- avoid assigning Slice C to the same worker as Slice D when parser behavior is still unstable
