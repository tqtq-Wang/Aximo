# RFC 0007: Compiler Summary

## Status

Draft

## Summary

Require compiler-emitted machine-readable semantic summaries as a first-class output of the language toolchain.

## Minimum Data

- module identity
- exports
- type declarations
- effects
- errors
- async markers
- call references
- diagnostics
- breaking changes

## Why

AI tools, documentation systems, and compatibility checks should not need to reconstruct everything from raw text.

## Consequences

- schema stability becomes important early
- summary output must use canonical terminology
- examples and snapshots should exercise the summary surface
