# RFC 0004: Effects

## Status

Draft

## Summary

Treat effect declarations as part of the function contract rather than optional comments or framework metadata.

## Requirements

- functions declare effects with `effects [...]`
- pure functions remain effect-free by omission
- callers must cover callee effects
- effect expansion on public APIs is compatibility-relevant

## Why

Effect visibility improves local reasoning, review quality, and AI-assisted change safety.

## Tradeoffs

- more verbosity in function declarations
- better static analysis and review confidence
