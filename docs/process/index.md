# Process Overview

This section defines how Axiom should be developed with multiple Codex agents in parallel.

The repository is explicitly structured for parallelism, but parallelism is only safe when:

- specification changes have a clear owner
- machine-readable contracts are stable enough for downstream work
- validation scripts are run before merge
- cross-workstream edits are treated as escalations instead of casual cleanup

Read in this order:

1. [Multi-Agent Readiness](./multi-agent-readiness)
2. [Multi-Codex Workflow](./multi-codex-workflow)
3. [Multi-Agent CLI Playbook](./multi-agent-cli-playbook)
4. [Task Slices](./task-slices)
5. [Branching and Commits](./branching-and-commits)
6. [Development Environment](./development-environment)
7. [Implementation Kickoff](./implementation-kickoff)
8. [IR Implementation Kickoff](./ir-implementation-kickoff)
