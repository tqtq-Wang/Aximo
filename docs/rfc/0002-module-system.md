# RFC 0002: Module System

## Status

Draft

## Summary

Adopt an explicit module system with path-to-file alignment and explicit imports.

## Decisions Captured

- every file has a `module` declaration
- module path must match file path under `src/`
- imports are explicit
- wildcard imports are forbidden
- visibility is explicit through `pub`, `internal`, or omission

## Why

Module predictability is central to Axiom's AI-friendly design. Hidden namespace behavior increases ambiguity for both humans and tooling.

## Tradeoffs

- more explicit import maintenance
- less convenience for ad hoc coding
- better tooling stability and refactoring reliability
