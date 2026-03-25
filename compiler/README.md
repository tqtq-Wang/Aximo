# Compiler Workspaces

This directory contains the future implementation workspaces for the Axiom compiler front end and semantic output pipeline.

Current status:

- repository structure is ready
- specs and schemas exist
- examples and fixtures exist
- implementation has not started in this bootstrap stage

Implementation ownership is expected to be split as follows:

- `lexer/`: tokenization and source spans
- `parser/`: syntactic parsing into AST
- `ast/`: AST node model and serialization
- `diagnostics/`: structured compiler messages
- `summary/`: machine-readable semantic summaries

Before writing implementation code, review:

- `docs/spec/*`
- `docs/process/multi-codex-workflow.md`
- `docs/process/task-slices.md`
- `docs/process/implementation-kickoff.md`
