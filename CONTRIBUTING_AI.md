# AI Collaboration Guide

## Purpose

This repository is intended for parallel development by humans and AI systems. The goal of this guide is to reduce drift, duplicate work, and speculative design changes.

## Non-Negotiable Rules

- Do not add language features that are not grounded in `docs/spec/` or an accepted decision record.
- Do not silently rename terms across spec, schemas, examples, and tests.
- Do not treat examples as freeform demos. They are compiler and documentation fixtures.
- Do not expand effects, visibility rules, or module layout rules without updating the relevant spec files.
- Do not introduce macros, implicit imports, implicit conversions, or hidden effects.

## Source-of-Truth Order

Use this precedence when editing:

1. `docs/spec/*.md`
2. `docs/decisions/*.md`
3. `docs/rfc/*.md`
4. `schemas/*.json`
5. `examples/*`
6. `tests/*`

If a lower-precedence file appears to conflict with a higher-precedence file, fix the lower-precedence file and record the mismatch.

## Workstream Ownership

Parallel work should follow these boundaries:

- `docs/spec/`: semantic source-of-truth authorship
- `schemas/`: machine-readable contract authorship
- `examples/`: language usage fixtures
- `tests/`: parser, diagnostics, and snapshot fixtures
- `compiler/`: implementation work only after spec and schema alignment

Avoid cross-cutting edits unless the task explicitly requires synchronized updates.

See also:

- `AGENTS.md`
- `docs/process/multi-agent-readiness.md`
- `docs/process/multi-codex-workflow.md`
- `docs/process/task-slices.md`
- `docs/process/branching-and-commits.md`

## Required Sync Matrix

If you change one of the following, you must inspect the corresponding files:

- syntax grammar changes:
  - `docs/spec/syntax.md`
  - `schemas/ast.schema.json`
  - `examples/*`
  - `tests/parser/*`
- visibility or module rules:
  - `docs/spec/modules.md`
  - `docs/spec/project-layout.md`
  - `schemas/compiler-summary.schema.json`
- diagnostics shape:
  - `docs/spec/diagnostics.md`
  - `schemas/diagnostics.schema.json`
  - `tests/diagnostics/*`
- effect model:
  - `docs/spec/effects.md`
  - `docs/spec/compiler-summary.md`
  - `schemas/compiler-summary.schema.json`
  - `examples/effect-demo/*`

## Expected Change Style

- Prefer explicit assumptions over hidden guesswork.
- Prefer additive drafts over premature abstraction.
- Prefer localized edits over repository-wide stylistic churn.
- Keep examples readable enough for future AI refactoring tasks.

## Pull Request Checklist

- spec impact reviewed
- schema impact reviewed
- examples updated if language-facing behavior changed
- tests or snapshots updated if contracts changed
- open questions called out explicitly
- ownership boundary respected or explicitly escalated
- validation scripts run locally or in CI

## AI Output Expectations

When an AI updates this repository, it should leave behind:

- clear assumptions
- explicit file synchronization when rules changed
- no invented semantics beyond the accepted design surface
- no claims of implementation completeness without verification

## Branch and Merge Guidance

- Use short-lived topic branches.
- Keep each branch aligned to one workstream whenever possible.
- If a task changes `docs/spec/` and `schemas/`, treat that as a cross-contract change and call it out explicitly.
- Do not merge parser or summary changes that contradict checked-in fixture expectations.

## Commit Convention

Use Alibaba-style Chinese commit subjects:

- `feat: 中文描述`
- `fix: 中文描述`
- `docs: 中文描述`
- `chore: 中文描述`
- `refactor: 中文描述`
- `test: 中文描述`
- `ci: 中文描述`
