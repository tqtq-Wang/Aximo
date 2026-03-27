# Compiler Backend Boundary

This directory defines the backend-side boundary for Aximo implementation sprint 2.

Formal direction:

- the backend's upstream contract is `compiler/ir/*` once Slice H and Slice I land
- backend code must not treat `compiler/parser/*` or `compiler/ast/*` as a direct execution input
- the backend layer should consume a lowered IR handoff, not source-shaped frontend structures

Current structure:

- `cli.py`: top-level backend entry for boundary and target discovery
- `boundary.py`: backend-local target registry and boundary text
- `llvm/`: isolated feasibility spike retained for textual LLVM IR demos only

Current status:

- `llvm/` remains a feasibility spike only
- `llvm/` emits textual LLVM IR `.ll` files from built-in demos
- `llvm/` does not define the formal Aximo IR contract
- no formal IR-consuming backend adapter is executable yet because `compiler/ir/*` is still being introduced

Scope rules for this directory:

- keep backend-facing contracts pointed at IR rather than parser or AST
- keep the LLVM spike self-contained until it is reconnected through the IR boundary
- do not use backend code to backdoor spec, schema, or language-semantics changes
- do not let spike ergonomics become the source of truth for language design

Recommended entrypoints:

```powershell
python -m compiler.backend --describe-boundary
python -m compiler.backend --list-targets
python -m compiler.backend --target llvm-spike --demo add --out .tmp/add.ll
```

The direct `python -m compiler.backend.llvm` entrypoint remains available for compatibility with the isolated spike, but it is not the formal backend integration path.
