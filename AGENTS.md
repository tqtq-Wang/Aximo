# AGENTS.md

## Purpose

This file defines repository-local instructions for AI agents working in `Aximo`.

## Current Phase

The repository is still in scaffolding and governance completion mode.

Do:

- improve repository structure
- improve process documents
- improve CI and validation tooling
- improve examples, fixtures, and collaboration rules

Do not:

- start implementing lexer, parser, type checker, effect checker, or runtime code
- invent new language features beyond the documented spec

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

## Validation Before Completion

Run what is relevant:

- `python tools/check_spec.py`
- `python tools/check_examples.py`
- `python tools/generate_snapshot_index.py`
- `corepack pnpm docs:build`

## Windows Notes

- prefer repository scripts and Python entrypoints for validation
- shell wrappers in `tools/scripts/` exist mainly for CI and Unix-style invocation
