# RFC 0001: Language Goals

## Status

Draft

## Summary

Define Axiom as a statically typed compiled language optimized for AI collaboration and backend-oriented engineering workflows.

## Goals

- make code structure predictable
- make errors and effects visible in signatures
- support machine-readable semantic outputs
- keep the language readable and low-magic
- keep runtime costs explainable and hard to hide
- enable gradual use in real backend service development

## Non-Goals

- advanced type-level programming as an MVP priority
- macro-heavy metaprogramming
- implicit framework behavior
- shortest possible syntax

## Rationale

AI systems work better when source layout, call contracts, and error boundaries are explicit and stable. Backend services benefit heavily from these same constraints.

## Consequences

- repository structure becomes part of the product
- compiler summary becomes a first-class output
- examples and schemas are not secondary artifacts
- performance work should start from a documented cost model rather than ad hoc optimization folklore
