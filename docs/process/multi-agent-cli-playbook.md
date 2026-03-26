# Multi-Agent CLI Playbook

## Purpose

This document is the operational playbook for running multiple Codex CLI agents in parallel on the Axiom repository.

It is more concrete than the general workflow documents. The goal is to answer:

- how many terminals to open
- how to split write scopes
- how to isolate each worker
- how to prompt each worker
- how to merge changes back safely

## Recommended Operating Model

Use a hub-and-spoke model:

- one human lead
- one integrator CLI session
- multiple worker CLI sessions
- one git worktree per worker session

Do not run multiple worker sessions in the same working tree.

## Roles

### Human Lead

Responsibilities:

- decide priority
- approve scope changes
- resolve conflicts between slices
- decide merge order

### Integrator CLI

Responsibilities:

- inspect current repository state
- create worktrees and branches
- assign one slice per worker
- review returned diffs
- run final repository checks
- merge into `main`

The integrator should avoid broad implementation work unless a task is inherently cross-slice.

### Worker CLI

Responsibilities:

- work on exactly one slice
- stay inside assigned write scope
- report assumptions and validation performed

## Repository Preconditions

Before starting a multi-agent implementation sprint, verify:

- `corepack pnpm repo:check` passes
- CI is green on `main`
- the implementation slice is documented in `docs/process/task-slices.md`
- the intended phase is allowed by `docs/process/implementation-kickoff.md`

## Directory Isolation Strategy

Use `git worktree` to create one isolated working directory per slice.

Example layout:

```text
E:\code\Aximo                  -> main repository / integrator
E:\code\Aximo-slice-d-parser   -> worker for Slice D
E:\code\Aximo-slice-e-diag     -> worker for Slice E
E:\code\Aximo-slice-f-summary  -> worker for Slice F
```

## Worktree Setup

Run from the main repository:

```powershell
cd E:\code\Aximo

git fetch origin
git worktree add ..\Aximo-slice-d-parser -b slice/d-parser
git worktree add ..\Aximo-slice-e-diag -b slice/e-diagnostics
git worktree add ..\Aximo-slice-f-summary -b slice/f-summary
```

If a branch already exists remotely, use:

```powershell
git worktree add ..\Aximo-slice-d-parser slice/d-parser
```

## Recommended Terminal Layout

Open one terminal window per role:

1. Integrator terminal
   Path: `E:\code\Aximo`
2. Parser terminal
   Path: `E:\code\Aximo-slice-d-parser`
3. Diagnostics terminal
   Path: `E:\code\Aximo-slice-e-diag`
4. Summary terminal
   Path: `E:\code\Aximo-slice-f-summary`

If needed, add a fifth terminal for Examples/Fixtures.

## Standard Worker Assignment Format

Every worker should receive:

- the slice name
- allowed write scope
- forbidden directories
- current sprint goal
- required validation commands

Use a prompt shaped like this:

```text
你当前只负责 Slice D: Parser and AST。

允许修改：
- compiler/parser/*
- compiler/ast/*

禁止修改：
- docs/spec/*
- schemas/*
- compiler/diagnostics/*
- compiler/summary/*
- examples/*
- tests/*

目标：
- 为现有 parser fixtures 打通最小声明解析路径
- 不新增语言特性

要求遵守：
- AGENTS.md
- docs/process/task-slices.md
- docs/process/implementation-kickoff.md
- docs/process/branching-and-commits.md

完成前至少运行：
- corepack pnpm repo:validate-spec
- corepack pnpm docs:build

提交规范：
- 使用阿里中文提交风格，例如 `feat: 实现 parser 基础声明解析`
```

## Slice-Specific Prompt Templates

### Slice D: Parser and AST

```text
你当前只负责 Slice D: Parser and AST。

允许修改：
- compiler/parser/*
- compiler/ast/*

禁止修改：
- docs/spec/*
- schemas/*
- compiler/diagnostics/*
- compiler/summary/*
- examples/*
- tests/*

目标：
- 以现有 examples 和 parser fixtures 为准
- 打通 `.ax -> AST JSON` 的最小路径
- AST 形状必须与 `schemas/ast.schema.json` 对齐

禁止行为：
- 发明新语法
- 通过修改 spec 掩盖实现问题
```

### Slice E: Diagnostics

```text
你当前只负责 Slice E: Diagnostics。

允许修改：
- compiler/diagnostics/*

禁止修改：
- docs/spec/*
- schemas/*
- compiler/parser/*
- compiler/ast/*
- compiler/summary/*

目标：
- 输出 parser 阶段的 structured diagnostics
- 形状与 `schemas/diagnostics.schema.json` 对齐
- 以 `tests/diagnostics/parser/*` 为目标夹具
```

### Slice F: Summary

```text
你当前只负责 Slice F: Compiler Summary。

允许修改：
- compiler/summary/*

禁止修改：
- docs/spec/*
- schemas/*
- compiler/parser/*
- compiler/ast/*
- compiler/diagnostics/*

目标：
- 为后续 parser/type phases 预留 summary 生成骨架
- 输出形状与 `schemas/compiler-summary.schema.json` 对齐
- 以 `tests/snapshots/*` 为目标契约
```

## Daily Operating Loop

### Step 1: Integrator Preflight

Run in main repository:

```powershell
cd E:\code\Aximo
./tools/scripts/repo-check.ps1
git status
git branch
```

Confirm:

- repository is clean
- checks pass
- each planned slice has a dedicated branch/worktree

### Step 2: Assign Work

The integrator sends one bounded prompt to each worker.

Do not assign:

- parser and diagnostics in the same worktree
- schema changes without explicit approval
- broad cleanup together with feature work

### Step 3: Worker Execution

Each worker:

- reads the assigned process docs
- stays inside the assigned directory scope
- commits only slice-relevant work

### Step 4: Worker Self-Check

Before reporting back, the worker should run what is relevant:

```powershell
python tools/check_spec.py
python tools/check_examples.py
python tools/generate_snapshot_index.py
corepack pnpm docs:build
```

In practice:

- Slice D often runs docs build plus any parser-local test command
- Slice E validates diagnostics output against fixtures
- Slice F validates summary output against snapshots

### Step 5: Worker Report Format

Each worker should report back in this structure:

- changed files
- assumptions made
- validations run
- open questions
- whether the branch is ready to merge

### Step 6: Integrator Review

The integrator reviews:

- write scope compliance
- spec/schema drift
- fixture alignment
- commit message quality

### Step 7: Merge Sequence

When multiple slices land together, merge in this order:

1. contract changes
   - `docs/spec/*`
   - `schemas/*`
2. fixture changes
   - `examples/*`
   - `tests/*`
3. implementation changes
   - `compiler/*`

For the first implementation sprint, prefer merging Slice D before Slice E and Slice F if E/F depend on parser output shapes.

## Conflict Handling

If two workers need the same file:

- pause one worker
- re-scope the tasks
- let the integrator own the conflict

Do not let both workers continue and “sort it out later”.

## Rules For Cross-Slice Changes

Cross-slice work must be treated as escalation.

Examples:

- parser work that requires AST schema change
- diagnostics work that requires spec wording change
- summary work that reveals fixture inconsistency

The worker should stop and report:

- what blocked progress
- which files need coordination
- whether the issue is likely spec, schema, or implementation

## First Sprint Recommendation

For Axiom's first implementation sprint, use this sequence:

### Sprint Goal

- begin language implementation without expanding language scope

### Active Slices

- Slice D
- Slice E
- Slice F

### Suggested Scope

Slice D:

- parse `module`
- parse `use`
- parse `struct`
- parse `enum`
- parse `fn`

Slice E:

- parser error envelope
- location formatting
- fixture-aligned diagnostics JSON

Slice F:

- summary data model scaffolding
- export entry builder skeleton
- snapshot writer skeleton

## Example Sprint Checklist

Integrator checklist:

- [ ] repository clean before branching
- [ ] worktrees created
- [ ] worker prompts prepared
- [ ] merge order decided

Worker checklist:

- [ ] read assigned process docs
- [ ] stay in allowed write scope
- [ ] run validation
- [ ] commit with Chinese subject

Merge checklist:

- [ ] review diffs
- [ ] run `corepack pnpm repo:check`
- [ ] push and wait for CI

## Commands Reference

### Create Worktrees

```powershell
git worktree add ..\Aximo-slice-d-parser -b slice/d-parser
git worktree add ..\Aximo-slice-e-diag -b slice/e-diagnostics
git worktree add ..\Aximo-slice-f-summary -b slice/f-summary
```

### List Worktrees

```powershell
git worktree list
```

### Remove Completed Worktree

```powershell
git worktree remove ..\Aximo-slice-d-parser
```

### Push Worker Branch

```powershell
git push -u origin slice/d-parser
```

### Final Integrator Check

```powershell
corepack pnpm repo:check
git status
```

## Anti-Patterns

- multiple workers in one working tree
- one worker editing multiple slices “for convenience”
- changing spec and implementation silently in one pass
- using examples to invent missing language semantics
- merging without running repository checks

## Bottom Line

The simplest safe model is:

- one integrator
- one slice per worker
- one worktree per worker
- one validation loop before merge

If you keep those four invariants, multi-agent CLI development remains manageable.
