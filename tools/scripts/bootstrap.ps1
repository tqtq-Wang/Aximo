$ErrorActionPreference = "Stop"

Write-Host "[axiom] bootstrap"
corepack pnpm install --no-frozen-lockfile
corepack pnpm repo:check
