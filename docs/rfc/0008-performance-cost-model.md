# RFC 0008: Performance Cost Model

## Status

Draft

## Summary

Define a predictable performance model for Axiom so the language remains practical for backend engineering without forcing MVP users and implementers into maximal-complexity semantics.

## Goals

- make common runtime costs explainable from source
- keep hidden allocation and dispatch boundaries rare
- preserve a thin runtime surface where possible
- guide IR and backend design before LLVM integration expands

## Non-Goals

- freezing the final optimizer strategy
- promising zero-cost abstraction for every future language feature
- deciding all low-level ABI details in this document

## Principles

### Predictability Over Cleverness

The language should prefer behavior that a human can reason about from signatures, type shapes, and explicit operations.

### Explicit Expensive Boundaries

Potentially expensive behavior should be visible in source or contract form when practical, including:

- heap-backed data duplication
- dynamic dispatch
- async suspension
- effectful I/O boundaries

### Thin Runtime by Default

Axiom should not depend on a large implicit runtime for normal business control flow. Runtime services may exist, but their boundaries should remain explicit and replaceable.

### Static Analysis First

Where tradeoffs exist, MVP design should bias toward semantics that can be represented clearly in diagnostics, compiler summary output, IR, and backend lowering.

## MVP Guardrails

- hidden deep copies should be avoided for heap-backed data
- dynamic dispatch should never be selected implicitly by compiler convenience alone
- error propagation should lower to explicit control flow rather than exception-style hidden machinery
- async should remain a source-visible boundary with a documented lowering strategy

## Relationship to Other RFCs

- RFC 0009 should define value and memory semantics consistent with this cost model
- RFC 0010 should define dispatch and runtime boundary rules consistent with this cost model

## Why

The project already commits to explicit errors, explicit effects, and low-magic source structure. A documented cost model extends those same values to runtime behavior and reduces future churn in IR and backend work.
