# RFC 0006: Async

## Status

Draft

## Summary

Use explicit `async fn` and `await` syntax with no implicit async lifting.

## Rules

- async functions must be marked `async`
- suspension points must be marked `await`
- async and effects remain separate concerns
- async lowering should stay representable in compiler IR and should not force an oversized implicit runtime contract

## Why

The async boundary should remain visible in source and in summary output.
