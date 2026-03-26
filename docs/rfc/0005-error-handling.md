# RFC 0005: Error Handling

## Status

Draft

## Summary

Adopt structured error handling through `Result<T, E>` rather than exception-driven business control flow.

## Rules

- recoverable failures use `Result`
- error types should be enumerable and documented
- propagation remains explicit
- crashes are reserved for unrecoverable system conditions
- normal business error flow should lower to explicit control flow rather than hidden exception machinery

## Why

Structured errors are easier to analyze, document, diff, and feed into compiler summary output.
