# Project Layout

## Goal

Axiom uses a fixed or strongly recommended project layout to improve predictability for both human maintainers and AI systems.

## Standard Project Root

```text
my-app/
  axiom.toml
  src/
    app.ax
    domain/
      user/
        model.ax
        service.ax
        repo.ax
        errors.ax
        tests.ax
  docs/
  tests/
```

## Root-Level Files

### `axiom.toml`

Project metadata and workspace-level conventions.

### `src/`

All Axiom source modules for the project.

### `docs/`

Project documentation and generated or curated design notes.

### `tests/`

Repository or project-level fixtures that do not naturally live inside a domain module.

## Module Family Template

Each domain area should prefer the following file family:

- `model.ax`
- `service.ax`
- `repo.ax`
- `errors.ax`
- `tests.ax`

This is a strong convention because it helps AI systems predict where to read and where to place new code.

## Path Rules

- Each `.ax` file must begin with a `module` declaration.
- The module path must match the file path under `src/`.
- `src/app.ax` maps to `module app`.
- `src/domain/user/service.ax` maps to `module domain.user.service`.

## Repository Bootstrap Layout

This language repository is itself a monorepo bootstrap. It contains:

- specification documents
- JSON schemas
- example projects
- compiler work areas
- validation fixtures

That root-level layout is a language project concern, not an Axiom application layout concern.

## Forbidden Drift

The following patterns are discouraged or forbidden in Axiom projects:

- arbitrary per-team naming for equivalent files
- wildcard or implicit module discovery
- moving domain logic into infrastructure directories
- hiding tests in unrelated files

## Assumptions

- Additional files may exist when justified by domain complexity, but the baseline module family remains preferred.
- The compiler should eventually validate the module path to file path invariant.
