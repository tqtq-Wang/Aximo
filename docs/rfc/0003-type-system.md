# RFC 0003: Type System

## Status

Draft

## Summary

Define a conservative type-system baseline centered on structs, enums, newtypes, `Option`, `Result`, generics, and trait-based abstraction.

## Included

- static strong typing
- product and sum types
- distinct domain wrappers through newtypes
- trait constraints in direct signature form
- structured error modeling

## Deferred

- advanced inference tricks
- higher-kinded types
- dependent types
- detailed ownership and lifetime semantics, to be refined in RFC 0009
- final dispatch strategy details, to be refined in RFC 0010

## Why

The language should optimize for clarity, documentation, and mechanical analysis, not maximal type expressiveness.
