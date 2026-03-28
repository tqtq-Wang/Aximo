# Minimal LLVM Runtime Stub

This directory contains the current minimal runtime implementation needed by the
formal LLVM backend path.

Current symbols:

- `ax_runtime_string_concat(const char* left, const char* right) -> char*`

Current scope:

- accepts null-terminated UTF-8 byte strings behind `ptr`
- allocates a new concatenated buffer with `malloc`
- does not define ownership or deallocation policy beyond returning the pointer

This is intentionally a stub, not the final Aximo runtime contract.
