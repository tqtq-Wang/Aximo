#!/usr/bin/env bash
set -euo pipefail

echo "[axiom] validate-spec"
python tools/check_spec.py
