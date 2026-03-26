# RFC 0010: Dispatch and Runtime Boundaries

## Status

Draft

## Summary

Define the default dispatch model and runtime boundaries for Axiom so generics, async, error propagation, and backend lowering can evolve without hidden execution costs.

## Goals

- keep generic code fast by default
- make dynamic behavior opt-in and visible
- keep runtime services explicit rather than language-magic
- align frontend contracts with future IR and LLVM work

## Dispatch Direction

### Generic Code

The default direction for generic code should be static dispatch through specialization, monomorphization, or an equivalent implementation strategy that preserves predictable call costs.

### Dynamic Dispatch

If the language later supports trait objects or equivalent runtime-polymorphic values, that boundary should be explicit in source and type form.

The compiler should not silently choose dynamic dispatch as an implementation shortcut for generic code.

## Async Boundary

The language already requires explicit `async fn` and `await`. This RFC adds the implementation guardrail that async lowering should remain documented and predictable.

Direction for MVP:

- async lowering should be representable in IR
- executor or scheduling policy should remain outside the core language contract where practical
- async should not imply hidden effects beyond the operations it performs

## Error Runtime Boundary

Structured business errors should continue to lower as explicit control flow based on `Result<T, E>`.

Direction for MVP:

- normal error propagation should not depend on exception-style runtime unwinding
- unrecoverable crashes may still use dedicated failure machinery

## Effects Boundary

Effects should remain a static contract and analysis feature. They should not turn into an implicit runtime capability framework during MVP.

## Why

Without a documented dispatch and runtime boundary, the project risks drifting into accidental dynamic dispatch, oversized runtime requirements, or backend choices that are convenient in the short term but expensive to unwind later.
