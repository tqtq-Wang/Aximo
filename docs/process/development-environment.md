# Development Environment

## Purpose

This document defines the minimum local environment expected before starting language implementation work.

## Required Tools

- `git`
- `python` 3.14 or newer in the current local setup
- `node` 22
- `corepack`
- `pnpm` via `corepack`

## Recommended Local Commands

### Initial Bootstrap

PowerShell:

```powershell
./tools/scripts/bootstrap.ps1
```

Git Bash:

```bash
bash tools/scripts/bootstrap.sh
```

### Repository Checks

PowerShell:

```powershell
./tools/scripts/repo-check.ps1
```

Cross-platform direct commands:

```bash
python tools/check_spec.py
python tools/check_examples.py
python tools/generate_snapshot_index.py
corepack pnpm docs:build
```

## Expected Outcomes

After bootstrap succeeds:

- dependencies are installed
- docs build passes
- snapshot index is generated
- repository checks pass
- local Windows workflow matches the supported CI path closely

## Windows Notes

- use PowerShell wrappers if you do not want to rely on Git Bash
- line endings are normalized by `.gitattributes` and `.editorconfig`
- the Python entrypoints in `tools/` are the primary validation source of truth

## Before Starting Implementation

Run:

- `./tools/scripts/repo-check.ps1` on Windows
- or `corepack pnpm repo:check`

Do not start parser or diagnostics implementation on a dirty branch that has not passed repository checks.
