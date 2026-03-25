# Multi-Codex Workflow

## Purpose

This document defines how multiple Codex agents should collaborate on the Axiom repository without stepping on each other.

## Roles

### Human Lead

Responsible for:

- prioritization
- accepting design tradeoffs
- resolving conflicts between workstreams
- approving contract changes

### Integrator Codex

Responsible for:

- reading current repository state
- assigning slices to worker Codex instances
- reviewing output against spec and schemas
- merging or reconciling parallel changes

The integrator should avoid large implementation edits unless a task is inherently cross-slice.

### Worker Codex

Responsible for:

- one bounded slice
- one clear write scope
- one validation target

Workers should not perform broad repository cleanup while assigned to a narrow slice.

## Write-Scope Rules

- one worker, one primary write scope
- spec workers do not also change parser code unless explicitly assigned
- compiler workers do not change schemas unless the task is a coordinated contract update
- example workers update fixtures and snapshots only when tied to a documented contract

## Escalation Triggers

The task must return to the integrator if a worker discovers:

- a spec contradiction
- a schema naming mismatch
- a cross-slice breaking change
- an example that requires undocumented language behavior

## Merge Order

Use this order whenever a change spans multiple layers:

1. `docs/spec/`
2. `docs/decisions/`
3. `schemas/`
4. `examples/`
5. `tests/`
6. `compiler/`

## Mandatory Validation Before Merge

- run `bash tools/scripts/validate-spec.sh`
- run `bash tools/scripts/validate-examples.sh`
- run `bash tools/scripts/generate-snapshots.sh`
- run `pnpm docs:build`

## What Workers Should Report Back

Each worker should report:

- files changed
- assumptions made
- validation performed
- open questions discovered

## Anti-Patterns

- broad speculative refactors
- silent terminology changes
- schema edits without spec review
- compiler behavior changes without fixture updates
- using examples to introduce undeclared language features
