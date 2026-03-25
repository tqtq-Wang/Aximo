# DEC-0004: No Implicit Imports

## Status

Accepted

## Decision

Axiom does not support implicit imports or wildcard imports in the bootstrap design.

## Reason

Import behavior must remain stable and mechanically inspectable. Hidden namespace injection harms predictability for both humans and AI systems.

## Consequences

- every non-local symbol reference should have a visible import path
- module and parser tooling can rely on explicit dependency declarations
