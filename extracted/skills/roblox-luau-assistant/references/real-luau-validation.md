# Real Luau Validation + Final-Code Execution Gate

## Four-layer truth model
1. `VALIDATOR_PRESENT` — validator files are packaged.
2. `VALIDATOR_LOCALLY_EXECUTABLE` — package-local validator execution has actually occurred.
3. `VALIDATOR_HOST_CALLABLE` — an approved host/plugin-generation action actually invoked the validator.
4. `VALIDATION_ENFORCED` — the callable result is mandatory before final delivery.

Only layers 3 + 4, plus a passing exact-source result and matching final hash, permit `SYNTAX_VERIFIED` during ordinary generation.

## Current host audit
The audited 1.9.2 package had a real local validator but no verified host-callable validator action. The current Plugin Creator tool surface exposes package creation, inspection, archive retrieval, release listing, and package update; it does not expose a validator-specific MCP action, arbitrary process/Python execution action, or a tool-registration action for this package. See `skills/roblox-luau-assistant/references/host-capability-report.md`.

Truthful current state: `VALIDATOR_PRESENT=YES`, `VALIDATOR_LOCALLY_EXECUTABLE=YES`, `VALIDATOR_HOST_CALLABLE=NO PROOF`, `VALIDATION_ENFORCED=NO PROOF`.

## Exact-source gate
`GENERATE → FREEZE EXACT SOURCE → HASH → CALL APPROVED VALIDATOR → REPAIR ACTUAL SOURCE IF FAILED → RELOAD → VALIDATE CURRENT SOURCE → WHOLE-SOURCE EXHAUSTION → CONTAMINATION CHECK → FALSIFY → SECOND PASS → FINAL HASH MATCH → DELIVERY`.

Any mutation after validation causes `VALIDATION_INVALIDATED`.

## Security
The custom validator parses/analyzes source only. It never executes generated Roblox game code, uses `loadstring`, or runs arbitrary shell/network operations as part of syntax validation.

## Analyzer separation
The custom parser is a `CUSTOM LUAU SYNTAX VALIDATOR`, not the official Roblox compiler/runtime, not a complete type checker, and not a behavioral verifier. `luau-lsp` + Roblox type definitions are a separate stronger static-analysis layer and must be marked `ANALYZER_UNAVAILABLE` unless actually executed.
