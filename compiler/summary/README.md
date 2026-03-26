# compiler/summary

Minimal implementation scaffold for compiler summary generation.

Current responsibilities:

- keep the summary contract aligned with `schemas/compiler-summary.schema.json`
- provide a stable in-memory model for module summaries
- normalize summary JSON output for later parser, type, and effect stages
- write `.summary.json` artifacts without inventing new fields

Current files:

- `contract.py`: schema-aligned data model and JSON serialization helpers
- `main.py`: minimal CLI for writing normalized summary output
- `INTEGRATION.md`: shortest hand-off note for future parser and semantic inputs

Example:

```powershell
python compiler/summary/main.py --module app --out .tmp/app.summary.json
```

Notes:

- output path is always explicit via `--out`; summary does not derive filenames from module names
- mapping input rejects fields outside the checked-in schema contract

This scaffold intentionally does not parse source files or infer semantics.
