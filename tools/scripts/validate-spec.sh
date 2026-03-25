#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

echo "[axiom] validate-spec"

python - "$ROOT_DIR" <<'PY'
import json
import pathlib
import sys

root = pathlib.Path(sys.argv[1])

required_files = [
    "README.md",
    "ROADMAP.md",
    "CONTRIBUTING_AI.md",
    "axiom.toml",
    ".editorconfig",
    ".gitattributes",
    ".github/workflows/ci.yml",
    "docs/index.md",
    "docs/vision.md",
    "docs/architecture.md",
    "docs/spec/glossary.md",
    "docs/spec/project-layout.md",
    "docs/spec/syntax.md",
    "docs/spec/semantics.md",
    "docs/spec/type-system.md",
    "docs/spec/effects.md",
    "docs/spec/modules.md",
    "docs/spec/diagnostics.md",
    "docs/spec/compiler-summary.md",
    "docs/process/index.md",
    "docs/process/multi-agent-readiness.md",
    "docs/process/multi-codex-workflow.md",
    "docs/process/task-slices.md",
    "schemas/ast.schema.json",
    "schemas/diagnostics.schema.json",
    "schemas/compiler-summary.schema.json",
]

missing = [path for path in required_files if not (root / path).exists()]
if missing:
    raise SystemExit("missing required files:\n- " + "\n- ".join(missing))

json_targets = [
    root / "schemas" / "ast.schema.json",
    root / "schemas" / "diagnostics.schema.json",
    root / "schemas" / "compiler-summary.schema.json",
]
for path in json_targets:
    with path.open("r", encoding="utf-8") as handle:
        json.load(handle)

config_text = (root / "docs" / ".vitepress" / "config.mts").read_text(encoding="utf-8")
required_links = [
    "/spec/glossary",
    "/spec/project-layout",
    "/spec/syntax",
    "/spec/semantics",
    "/spec/type-system",
    "/spec/effects",
    "/spec/modules",
    "/spec/diagnostics",
    "/spec/compiler-summary",
    "/process/",
    "/process/multi-agent-readiness",
    "/process/multi-codex-workflow",
    "/process/task-slices",
]
missing_links = [link for link in required_links if link not in config_text]
if missing_links:
    raise SystemExit("vitepress config is missing links:\n- " + "\n- ".join(missing_links))

print("validated required files, schema json, and VitePress navigation")
PY
