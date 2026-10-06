---
name: roblox-engineering-enforcement
description: Strict default proof/rejection layer for Roblox code generation with automatic Engineering Gate, Roblox API Truth Gate, whole-source defect exhaustion, exact-source verification, and false-PASS prevention.
---
# ROBLOX DEV MASTER — Engineering Enforcement v1.12.0-gate

## Default gate
For every Roblox code generation, modification, repair, or material rewrite: `EXECUTE ENGINEERING GATE` automatically. Do not wait for an audit request.

## Required order
`REQUIRE → RETRIEVE AUTHORITATIVE KNOWLEDGE → IMPLEMENT → LEVEL 1 WHOLE-SOURCE AUDIT → API TRUTH GATE → APPLICABLE ROBLOX-NATIVE CHECKS → FREEZE EXACT SOURCE → HASH → LEVEL 2 CUSTOM VALIDATOR WHEN AVAILABLE → REPAIR ACTUAL SOURCE → RELOAD → WHOLE-SOURCE EXHAUSTION → RELATED-PATTERN SEARCH → CONTAMINATION CHECK → ADVERSARIAL FALSIFICATION → INDEPENDENT SECOND PASS → SOURCE/HASH RECONCILIATION → LEARNING IF QUALIFIED → REPORT/DELIVER`.

## API truth
Official Roblox documentation/API reference outranks community examples. Check existence, class/service, member, signature, context, lifecycle, currentness/deprecation, and documented behavior. Documentation truth and implementation truth are independent gates.

## Unknown state
Unverified API behavior must be labeled `API_UNVERIFIED` or `API_BEHAVIOR_UNVERIFIED`. Never convert uncertainty to confidence.

## Whole-source rule
A reported line is never the defect boundary. Search the full affected source and related files where the root-cause class can cross file boundaries. Repair all confirmed manifestations, reload current source, and check repair contamination.

## PASS rejection
Do not PASS because code looks plausible, one error disappeared, one line was fixed, an API exists in docs, or a static check passed while a required validator was unavailable. Use truthful statuses such as `PARTIAL`, `RUNTIME_UNVERIFIED`, `VALIDATION_UNAVAILABLE`, `HOST_BLOCKED`, `API_UNVERIFIED`, or the existing equivalent.

## Exact-source truth
Never validate source A and deliver source B. Mutation after validation means `VALIDATION_INVALIDATED` and requires a fresh gate.

## UI QA gate (whenever UI is generated)
Check against `skills/roblox-luau-assistant/references/ui-defaults.md`: compact size, safe area, no overlapping text, exactly one visible state, icon policy (no emoji icons, no invented asset IDs, NEEDS ASSETS list). Run `python scripts/ui_lint.py <files>` when code execution exists; FAIL findings must be fixed. Report UI QA as STATIC: it is not layout, device or runtime verification.

## Runtime boundary
Static parser/API-document checks do not prove runtime correctness. Never claim Roblox runtime verification without actual runtime artifacts.
