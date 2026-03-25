# AGENTS.md

## Purpose

This file defines repository-local instructions for AI agents working in `Aximo`.

## Current Phase

The repository is implementation-ready, but implementation should begin only when the task explicitly requests language development.

Do:

- maintain repository structure and governance
- improve CI and validation tooling
- improve examples, fixtures, and collaboration rules
- start bounded implementation work only when explicitly requested

Do not:

- invent new language features beyond the documented spec
- bypass slice boundaries when implementation begins

## Source of Truth

Use this precedence:

1. `docs/spec/*.md`
2. `docs/decisions/*.md`
3. `docs/rfc/*.md`
4. `schemas/*.json`
5. `examples/*`
6. `tests/*`

## Commit Convention

Use Alibaba-style Chinese commit subjects in the form:

- `feat: 中文描述`
- `fix: 中文描述`
- `docs: 中文描述`
- `chore: 中文描述`
- `refactor: 中文描述`
- `test: 中文描述`
- `ci: 中文描述`

Keep the message direct and outcome-oriented.

## Multi-Agent Rule

- one agent, one bounded slice
- avoid broad cross-slice edits unless explicitly required
- if you touch spec and schema together, call that out clearly
- for first implementation work, stay within Slice D, E, or F unless explicitly reassigned

## Validation Before Completion

Run what is relevant:

- `python tools/check_spec.py`
- `python tools/check_examples.py`
- `python tools/generate_snapshot_index.py`
- `corepack pnpm docs:build`
- `corepack pnpm repo:check`

## Windows Notes

- prefer repository scripts and Python entrypoints for validation
- shell wrappers in `tools/scripts/` exist mainly for CI and Unix-style invocation
- PowerShell wrappers are available for Windows-first local usage
