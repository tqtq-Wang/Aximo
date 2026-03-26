# RFC 0011: IR Design and Lowering Boundary

## Status

Draft

## Summary

Introduce a formal compiler IR layer between the current frontend outputs and future backend work, and define the boundary between parser-facing facts, semantic lowering, and backend consumption.

## Goals

- prevent direct AST-to-LLVM coupling
- give backend work a stable internal contract
- preserve parser, diagnostics, and summary responsibilities without forcing them to own backend lowering
- make control flow, error propagation, async lowering, and call boundaries representable in one internal form

## Non-Goals

- defining the final machine-level backend strategy
- exposing IR as a repository-wide public artifact before its contract is stable
- replacing AST, diagnostics, or compiler summary as user-facing outputs

## Layer Roles

### AST

AST remains source-shaped.

It should preserve:

- declaration structure
- source terminology
- schema-aligned spans where allowed
- parser-facing facts needed by diagnostics and summary

AST should not become the long-term backend contract.

### Diagnostics

Diagnostics remain the structured error output contract for failed frontend work.

Diagnostics should be emitted from parser and later semantic phases before backend work is considered.

### Compiler Summary

Compiler summary remains a machine-readable module contract for tooling, review, and compatibility checks.

It is not the backend IR.

### IR

IR is an internal compiler contract used to represent executable program intent in a form that is more regular than AST and more language-shaped than LLVM IR.

IR should become the formal handoff point for backend work.

### Backend

Backends should consume IR rather than AST.

The current LLVM spike remains a feasibility experiment only until it is reconnected through the IR boundary.

## Dependency Direction

The intended dependency flow for implementation phase 2 is:

`parser/ast -> diagnostics`

`parser/ast -> summary`

`parser/ast -> semantic lowering -> ir`

`ir -> backend`

Backend code should not directly import parser internals once the IR contract exists.

## MVP IR Scope

The first IR iteration should cover only the language surface already exercised by current examples and fixtures.

Direction for minimum representable concepts:

- module identity
- function definitions
- parameters
- local bindings
- blocks
- branches
- returns
- direct calls
- explicit error propagation
- enum construction references as needed by current examples

## Lowering Rules

### Source Sugar Should Be Reduced Before Backend Work

The IR layer should normalize source-facing constructs into a smaller set of operational forms.

Examples:

- expression-oriented returns may lower into explicit terminators
- `?` should lower into explicit control flow over `Result`
- source-level async should lower into a documented intermediate form rather than remain a parser-only flag

### Diagnostics Boundary

Source diagnostics should be produced before lowering whenever they depend on source-level span and syntax context.

IR construction may still produce internal compiler diagnostics, but it should not replace frontend diagnostics responsibilities.

### Summary Boundary

Compiler summary should continue to derive from parser-facing results and semantic facts appropriate for public API description.

Summary should not be reverse-engineered from backend IR.

## Initial IR Design Constraints

- IR should prefer explicit control flow over hidden runtime semantics
- IR should make call boundaries visible
- IR should have a place to record effect-relevant operations
- IR should be suitable for later lowering to LLVM without requiring LLVM concepts to leak upward
- IR should stay small enough for a bounded implementation sprint

## Open Questions

- how much type information the first IR version should carry
- whether async lowering starts as a stubbed representation or a fully executable lowering target
- whether IR should gain its own machine-readable schema during the first implementation pass or immediately after the contract stabilizes

## Why

The repository now has working parser, diagnostics, summary, and an isolated LLVM feasibility spike. The next meaningful step is not more frontend drift or direct backend expansion. It is a formal IR layer that prevents future implementation from coupling source syntax directly to backend internals.
