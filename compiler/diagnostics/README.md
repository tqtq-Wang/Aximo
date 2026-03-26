# compiler/diagnostics

Structured diagnostics package for the Axiom compiler workspaces.

Current scope for Slice E:

- define schema-aligned diagnostics data structures
- emit deterministic JSON matching `schemas/diagnostics.schema.json`
- provide parser-facing factories for the current invalid fixture set

Out of scope here:

- parser recovery or syntax analysis
- AST construction
- semantic checking beyond the current parser-facing fixture surface

Current parser diagnostic coverage:

- `P001`: missing module declaration at start of file
- `P002`: invalid match arm syntax; expected `=>`
- `E001`: effectful operation requires an explicit effects clause

Wiring contract with Slice D:

- parser gives: fixture-relative file path, selected diagnostic factory, and a
  precise `Span(start, end)` for the primary failure site
- diagnostics returns: a `Diagnostic` value or a `DiagnosticReport`
- JSON shape emitted: `schema_version`, then `diagnostics[]` with
  `level/code/message/location` and optional `help/notes/related`
- diagnostics does not decide parser recovery, error classification beyond the
  selected factory, or span discovery

Planned usage:

```python
from compiler.diagnostics import Span, parser

span = Span.from_bounds(1, 1, 1, 3)
diagnostic = parser.missing_module_declaration(
    "tests/parser/invalid/missing-module.ax",
    span,
)
payload = parser.report(diagnostic).to_json()
```

The parser slice is expected to discover locations and choose which diagnostic
factory to call. This package owns the structured output contract and JSON
emission only.
