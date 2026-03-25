# Diagnostics

## Goal

Diagnostics must be readable by humans and directly consumable by tools.

## Core Shape

Each diagnostic should include:

- level
- code
- message
- primary location
- optional secondary locations
- optional related notes

The canonical machine-readable contract is defined in `schemas/diagnostics.schema.json`.

## Levels

Current baseline levels:

- `error`
- `warning`
- `info`

## Code Naming

Diagnostic codes should be stable identifiers such as:

- `P001`
- `M001`
- `E001`

The exact code namespace may evolve, but codes must remain stable enough for snapshots and tooling.

## Parser-Oriented Diagnostics

Early compiler work is expected to emit diagnostics for:

- missing module declaration
- invalid declaration syntax
- malformed effect clause
- malformed import list
- invalid match arm structure

## Module and Semantic Diagnostics

Later phases should cover:

- unresolved imports
- visibility violations
- undeclared effects
- non-exhaustive matches
- incompatible return types

## Design Principles

- message text should be human-readable
- structured fields should carry machine-relevant detail
- source spans should be precise
- diagnostics should avoid hidden inferred context where possible

## Snapshot Use

Diagnostics are expected to be checked into `tests/diagnostics/` as JSON fixtures for stability testing.
