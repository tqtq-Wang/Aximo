# DEC-0001: No Macros

## Status

Accepted

## Decision

Axiom v0.1 does not include a macro system in the repository bootstrap scope.

## Reason

Macros create hidden control flow and hidden semantics, which work against the language's low-magic and AI-readable design goals.

## Consequences

- language design work should prefer explicit syntax and ordinary declarations
- tooling does not need macro expansion logic at bootstrap time
