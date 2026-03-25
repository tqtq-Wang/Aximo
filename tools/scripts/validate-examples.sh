#!/usr/bin/env bash
set -euo pipefail

echo "[axiom] validate-examples"
python tools/check_examples.py
