# DEC-0002: Default Immutable

## Status

Accepted

## Decision

Bindings are immutable by default through `let`. Mutation requires `var`.

## Reason

Default immutability improves local reasoning, reduces accidental state changes, and makes AI-generated changes easier to review.

## Consequences

- examples should prefer `let`
- semantics and diagnostics should treat mutation as explicit behavior
