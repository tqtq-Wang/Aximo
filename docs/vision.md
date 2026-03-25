# Vision

## Mission

Axiom is a language project for AI-assisted software development with a strong emphasis on backend engineering.

Its central hypothesis is that a language can improve long-term maintainability and AI collaboration quality if it treats structure, effects, errors, visibility, and machine-readable summaries as language-level concerns instead of optional tooling afterthoughts.

## Product Direction

The intended destination is not a toy language. Axiom is being shaped toward practical service-oriented development where a human developer and one or more AI systems can work inside the same codebase with lower ambiguity and lower semantic drift.

That direction implies several priorities:

- domain modules should have predictable layout
- business errors should be modeled explicitly
- side effects should be statically declared
- compiler output should be machine-readable enough for AI tooling
- public API changes should be analyzable before merge

## Primary Users

The project currently serves three user groups:

1. language and compiler implementers
2. toolchain and AI workflow builders
3. early adopters experimenting with backend-style applications

## Design Commitments

The following commitments come directly from the RFC baseline and are treated as repository-wide constraints:

- static strong typing
- default immutability
- `Option` and `Result` as language-level concepts
- explicit error propagation
- explicit effect declarations
- explicit visibility
- fixed project and module structure
- low magic and low hidden control flow
- structured diagnostics and compiler summary output

## Why Backend-Oriented

Backend systems are a practical test bed for Axiom because they force the language to handle:

- domain models
- repository boundaries
- data validation
- structured failure modes
- network and storage effects
- API stability over time

These are exactly the areas where AI systems benefit from explicit contracts and stable repository structure.

## Non-Goals for This Stage

This repository stage is not trying to:

- outperform mature system languages
- maximize syntax compression
- support advanced type-level programming
- standardize a rich runtime ecosystem
- ship a complete compiler

## Success Criteria

The initialization phase is successful if future teams can use this repository to:

- implement parser and analysis components against a stable document surface
- validate examples and snapshots against schemas
- evolve the language without silent naming drift
- experiment with backend-style Axiom services under AI-assisted workflows

## Assumptions

- Axiom will be evaluated first on small to medium backend-style services, not low-level systems code.
- AI tooling will consume structured compiler output as a first-class artifact.
- Stability of layout and terminology is more valuable than early breadth of features.

## Open Questions

- What is the minimal standard library needed for backend viability?
- How should runtime packaging and deployment metadata be standardized?
- How far should interoperability go in the MVP beyond C ABI and schema-driven workflows?
