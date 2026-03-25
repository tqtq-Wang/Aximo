#!/usr/bin/env bash
set -euo pipefail

echo "[axiom] bootstrap"
corepack pnpm install --no-frozen-lockfile
corepack pnpm repo:check
