#!/usr/bin/env bash
set -euo pipefail

echo "[axiom] generate-snapshots"
python tools/generate_snapshot_index.py
