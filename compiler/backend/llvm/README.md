# LLVM Backend Feasibility Spike

This package is a minimal feasibility spike for exploring whether the Aximo repository can emit textual LLVM IR from an isolated backend layer.

Non-goals:

- this is not the formal frontend -> IR -> LLVM contract
- this does not define Aximo language semantics
- this does not integrate with `compiler/parser/*`
- this does not integrate with `compiler/ast/*`
- this does not integrate with `compiler/summary/*`
- this does not attempt optimization passes or backend architecture decisions

What it does:

- exposes a small CLI at `python -m compiler.backend.llvm`
- writes textual LLVM IR `.ll` files
- ships two built-in demos:
  - `add`: minimal integer addition function
  - `hello`: minimal `main`-style hello example

Example usage:

```powershell
python -m compiler.backend.llvm --demo add --emit-ir --out .tmp/add.ll
python -m compiler.backend.llvm --demo hello --emit-ir --out .tmp/hello.ll
```

Notes:

- `--emit-ir` is accepted for spike ergonomics, but the current CLI only emits textual LLVM IR
- if LLVM tools are present locally, validate at least one generated file with the available toolchain
- if no LLVM tools are installed, the spike is still useful as a `.ll` text emitter
