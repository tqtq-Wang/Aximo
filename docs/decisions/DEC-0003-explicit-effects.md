# DEC-0003: Explicit Effects

## Status

Accepted

## Decision

Function-level effects must be declared explicitly with `effects [...]`.

## Reason

Backend code often interacts with storage, network, logging, or stateful subsystems. Making those boundaries visible is critical for both review and automation.

## Consequences

- future compiler phases must validate effect declarations
- compiler summary must report effect sets
- examples should demonstrate effect boundaries directly
