# Compiler Backend Spikes

This directory contains backend-facing spike work that is intentionally isolated from the current parser, AST, diagnostics, and summary slices.

Current status:

- `llvm/` is a feasibility spike only
- it emits textual LLVM IR `.ll` files from built-in demos
- it does not define the formal Aximo frontend -> IR -> LLVM contract
- it does not define language semantics
- it does not consume output from `compiler/parser/*`

Scope rules for this directory:

- keep spike code self-contained
- do not use it to backdoor spec or schema changes
- validate feasibility first, then discuss formal contracts separately
