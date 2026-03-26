# IR Implementation Kickoff

## Purpose

This document defines the next implementation phase after the initial parser, diagnostics, and summary bootstrap.

Its job is to keep worker execution bounded while the repository introduces a formal compiler IR and prepares backend work to consume it.

## Phase Statement

Implementation sprint 1 is considered complete when the repository has:

- parser output through a public result API
- structured diagnostics output
- compiler summary generation against checked-in snapshots
- an isolated LLVM feasibility spike that is explicitly not yet integrated

The next approved phase is:

- IR contract definition
- IR implementation scaffolding
- bounded lowering from current frontend outputs into IR
- backend preparation to consume IR instead of parser or AST directly

## Hard Rules For This Phase

- do not bypass IR by wiring AST directly into a formal backend path
- do not use the existing LLVM spike as a de facto language contract
- do not expand the language surface to justify IR work
- do not move diagnostics or summary responsibilities into backend code
- if a worker needs a language contract change, update docs first, then schema if needed, then implementation

## Recommended Sprint Sequence

### Phase 2A: Contract Freeze

Merge order:

1. RFC and spec updates for cost model, memory/value semantics, dispatch/runtime boundaries, and IR boundary
2. any required schema work if IR becomes machine-readable in-repo
3. implementation slices

### Phase 2B: IR Introduction

Active slices should stay narrow and non-overlapping.

#### Slice H: IR Core

Write scope:

- `compiler/ir/__init__.py`
- `compiler/ir/types.py`
- `compiler/ir/README.md`

Goal:

- define the minimal in-repo IR data model and public API

Out of scope:

- parser changes
- backend lowering
- runtime execution

#### Slice I: IR Lowering

Write scope:

- `compiler/ir/lowering.py`
- `compiler/ir/__main__.py`
- `compiler/ir/cli.py`

Goal:

- lower the current public parser result into IR without importing parser internals beyond the public API

Out of scope:

- changing parser contracts
- adding unsupported language constructs
- backend code

#### Slice J: Backend Adapter

Write scope:

- `compiler/backend/*`

Goal:

- adapt backend work to consume IR and keep the existing LLVM spike isolated until the IR contract is ready

Out of scope:

- changing frontend semantics
- making LLVM output the source of truth for language design

## Validation Expectations

All implementation slices in this phase should run what is relevant:

- `python tools/check_spec.py`
- `python tools/check_examples.py`
- `python tools/generate_snapshot_index.py`
- `corepack pnpm docs:build`
- `corepack pnpm repo:check`

Slice-specific validation:

- Slice H should prove IR objects can be constructed and serialized in a deterministic way
- Slice I should prove current example sources lower into IR through the public parser API
- Slice J should prove backend code consumes IR rather than parser or AST directly

## Worker Prompt Requirements

Every worker prompt for this phase should include:

- exact write scope
- exact forbidden paths
- explicit reference to RFC 0008, RFC 0009, RFC 0010, and RFC 0011
- a statement that AST is not the backend contract
- a statement that the LLVM spike is not normative

## Exit Criteria For Implementation Sprint 2

- a formal `compiler/ir/*` surface exists
- current example-backed frontend output can lower into IR
- backend work can point to IR as its upstream contract
- no worker introduced direct parser-to-backend coupling
