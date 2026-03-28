# LLVM Backend Feasibility Spike

This package is a minimal feasibility spike for exploring whether the Aximo repository can emit textual LLVM IR from an isolated backend layer.

Non-goals:

- this is not the formal frontend -> IR -> LLVM contract
- this does not define Aximo language semantics
- this does not integrate with `compiler/parser/*`
- this does not integrate with `compiler/ast/*`
- this does not integrate with `compiler/summary/*`
- this does not attempt optimization passes or backend architecture decisions
- this is not the canonical `compiler/backend` entrypoint for future backend integration

What it does:

- exposes a compatibility CLI at `python -m compiler.backend.llvm`
- reports local LLVM tool availability for `clang`, `llc`, `opt`, `llvm-as`, and `lli`
- writes textual LLVM IR `.ll` files
- defaults demo artifacts to `.tmp/llvm-spike/<demo>.ll` when `--out` is omitted
- accepts `compiler.ir` `Module` JSON and lowers the currently supported IR subset into textual `.ll`
- ships two built-in demos:
  - `add`: minimal integer addition function
  - `hello`: minimal `main`-style hello example

Example usage:

```powershell
python -m compiler.backend --list-targets
python -m compiler.backend --target llvm-spike --demo add --out .tmp/add.ll
python -m compiler.backend --target llvm-spike --demo hello --emit-ir --out .tmp/hello.ll

# compatibility entrypoint kept for the isolated spike
python -m compiler.backend.llvm --check-toolchain
python -m compiler.backend.llvm --demo add
python -m compiler.backend.llvm --demo add --emit-ir --out .tmp/add.ll
python -m compiler.backend.llvm --demo hello --emit-ir --out .tmp/hello.ll
python -m compiler.backend.llvm --input-ir-json .tmp/module.ir.json --out .tmp/module.ll
python -m compiler.backend.llvm --input-ir-json .tmp/module.ir.json --stdout
```

Notes:

- use `python -m compiler.backend` to inspect the formal backend boundary and target status
- `--emit-ir` is accepted for spike ergonomics, but the current CLI only emits textual LLVM IR
- the direct CLI now reports whether the resolved command is demo mode or IR-input mode, and whether it only writes `.ll` artifacts or also mirrors output to stdout
- `--check-toolchain` is informational; missing LLVM tools do not block demo `.ll` emission
- `--input-ir-json` now reads `compiler.ir` `Module` JSON, calls the formal LLVM lowering core, and writes textual `.ll`
- if the lowering core rejects the current IR subset, the CLI prints the structured backend error payload instead of emitting partial or incorrect LLVM text
- if LLVM tools are present locally, validate at least one generated file with the available toolchain
- if no LLVM tools are installed, the spike is still useful as a `.ll` text emitter
- no parser, AST, or future IR contract should be inferred from these demos

Current IR subset notes:

- lowered successfully today:
  - function declarations
  - direct calls with representable argument and result types
  - integer and bool literals
  - string literals lowered as module-level global constants
  - `String + String` lowered to the explicit runtime symbol `@ax_runtime_string_concat`
  - local bindings and block terminators supported by the current LLVM core
- accepted but currently non-executable for LLVM output:
  - `StructType`
  - `EnumType`
  - `Newtype`
  - `TraitSurface`
- currently rejected with clear backend errors:
  - `ImplSurface`
  - `TestSurface`
  - generic functions
  - async functions
  - mutable locals
  - unexpanded `ErrorPropagationPlaceholder`
  - unsupported IR values such as field reads or symbol values in executable positions

Current runtime expectation:

- textual LLVM output may declare `@ax_runtime_string_concat(ptr, ptr) -> ptr`
- the repository now provides a minimal stub at `runtime/minimal/string_runtime.c`
- this stub is only a linking aid for the current backend slice, not the final runtime ABI

Minimal link example:

```powershell
python -m compiler.backend --target ir-backend --input examples/hello-world/src/app.ax --emit-llvm --out .tmp/hello.ll

@'
#include <stdio.h>

extern char* app__build_greeting(const char* subject);

int main(void) {
    puts(app__build_greeting("World"));
    return 0;
}
'@ | Set-Content -LiteralPath .tmp/hello_main.c -Encoding utf8

clang .tmp/hello.ll runtime/minimal/string_runtime.c .tmp/hello_main.c -o .tmp/hello.exe
.tmp/hello.exe
```
