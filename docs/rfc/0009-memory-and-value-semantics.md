# RFC 0009: Memory and Value Semantics

## Status

Draft

## Summary

Define an MVP memory and value model that keeps ordinary backend development approachable while avoiding performance cliffs caused by unclear copy, move, and allocation behavior.

## Goals

- distinguish cheap value movement from potentially expensive duplication
- avoid hidden deep-copy semantics for heap-backed data
- keep ownership rules simpler than a full borrow-checker-first design
- give IR and backend work a stable semantic basis

## Proposed Direction

### Cheap Value Types

Small scalar-like values and clearly cheap wrappers should remain inexpensive to pass and return.

Examples that are likely to fit this category once finalized:

- primitive numeric scalars
- booleans
- explicit domain newtypes over finalized cheap scalar types

The exact primitive set remains deferred.

### Heap-Backed Values

Strings, collections, and other heap-backed aggregates should not rely on implicit deep-copy behavior.

MVP direction:

- moving such values should be cheaper than duplicating them
- potentially expensive duplication should require an explicit operation such as `clone`
- tooling and diagnostics should eventually be able to highlight obvious accidental duplication risks

### Mutation and Sharing

The existing `let` and `var` model should remain the visible source-level entrypoint for local mutation.

This RFC does not propose a full ownership-and-borrowing surface today. Instead, it sets the constraint that any future sharing model must preserve predictable cost and avoid invisible aliasing semantics that are hard to analyze.

## Explicit Deferrals

This RFC does not yet finalize:

- full ownership and borrowing rules
- lifetime syntax
- allocator APIs
- collection ABI details
- stack versus heap placement guarantees

## Why

The current repository intentionally deferred ownership and memory semantics. That was acceptable for parser and summary bootstrap work, but it becomes a real blocker once IR and backend lowering need a stable cost model.
