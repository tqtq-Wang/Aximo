# Branching And Commits

## Purpose

This document defines the repository-level branching and commit conventions for multi-Codex parallel work.

## Branch Strategy

Use short-lived branches with explicit ownership.

Recommended patterns:

- `docs/spec-freeze`
- `schema/summary-contract`
- `examples/user-service-alignment`
- `ci/repo-checks`
- `process/multi-codex-rules`

Branch names should reveal the slice, not a vague intention.

## Merge Expectations

- merge small, bounded changes
- prefer one slice per branch
- escalate cross-slice changes before merge
- re-run repository checks before merging to `main`

## Commit Convention

Use Alibaba-style Chinese commit subjects:

- `feat: 中文描述`
- `fix: 中文描述`
- `docs: 中文描述`
- `chore: 中文描述`
- `refactor: 中文描述`
- `test: 中文描述`
- `ci: 中文描述`

## Commit Rules

- use one clear intent per commit
- keep the subject short and outcome-focused
- do not mix scaffolding and implementation work in the same commit
- when changing contracts, prefer explicit wording such as `修复` or `补充` over vague wording

## Recommended Examples

- `docs: 补充多 Codex 并行开发流程说明`
- `ci: 增加仓库校验与文档构建缓存`
- `chore: 补充 CODEOWNERS 与 PR 模板`

## Forbidden Examples

- `update`
- `misc`
- `fix stuff`
- `一些修改`

## Validation Before Push

Run at least one of the following depending on your slice:

- `pnpm repo:validate-spec`
- `pnpm repo:validate-examples`
- `pnpm repo:generate-snapshots`
- `pnpm repo:check`
