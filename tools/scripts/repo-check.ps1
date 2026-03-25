$ErrorActionPreference = "Stop"

Write-Host "[axiom] repo-check"
python tools/check_spec.py
python tools/check_examples.py
python tools/generate_snapshot_index.py
corepack pnpm docs:build
