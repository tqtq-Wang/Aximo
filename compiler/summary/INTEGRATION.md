# Summary Integration

This directory owns summary shaping and JSON emission only.

## Minimum upstream input

Future parser and semantic layers must provide, at minimum:

- `module`: canonical module path string
- `imports`: imported module strings
- `exports`: export entries using only schema fields
- `types`: type entries using only schema fields
- `diagnostics`: diagnostic entries using only schema fields
- `breaking_changes`: breaking-change entries using only schema fields

Rules:

- omitted collections are normalized to empty arrays
- no extra fields are accepted
- `schema_version` defaults to `0.1.0` unless an explicit schema-aligned value is passed

## Consumption modes

Preferred:

- instantiate `ModuleSummary`, `ExportEntry`, `TypeEntry`, `DiagnosticEntry`, and `BreakingChange` directly in Python

Fallback:

- pass a mapping through `module_summary_from_mapping(...)`

## Output contract

- write path is explicit; use `write_summary(summary, destination)` or CLI `--out`
- `build_summary_output_path(output_dir, summary_name)` only joins an explicit summary name to a directory
- summary does not define `module -> filename`

## Non-goals in this layer

- parsing source text
- inferring signatures, effects, errors, or calls
- inventing defaults beyond empty collections and `schema_version`
