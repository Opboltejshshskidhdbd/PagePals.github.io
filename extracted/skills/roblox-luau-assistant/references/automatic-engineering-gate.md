# Automatic Engineering Gate

## Purpose
This gate is default behavior for Roblox code generation, modification, repair, and material rewrites. The user does not need to request validation.

## Risk routing
### LOW
Simple isolated Luau change. Run whole-source syntax/structure audit, obvious scope/declaration hazards, and relevant API checks.

### MEDIUM
UI, interaction, client/server, or multi-script feature. Run syntax/structure, API truth, architecture, security, lifecycle, cleanup, and source-truth checks.

### HIGH
Persistence, economy, trading, marketplace, combat authority, cross-server state, or complex concurrency. Run the full existing engineering pipeline including networking/authority, security, persistence/recovery, lifecycle, performance, cleanup, adversarial falsification, and second pass.

Risk routing may reduce irrelevant checks, never required checks.

## Mandatory sequence
`REQUEST → REQUIREMENTS → RELEVANT KNOWLEDGE → ARCHITECTURE → IMPLEMENT → LEVEL 1 WHOLE-SOURCE AUDIT → API TRUTH GATE → APPLICABLE ROBLOX-NATIVE AUDITS → DEFECT DETECTION → ACTUAL SOURCE REPAIR → CURRENT-SOURCE RELOAD → WHOLE-SOURCE RE-AUDIT → RELATED-PATTERN SEARCH → REPAIR-CONTAMINATION CHECK → ADVERSARIAL FALSIFICATION → INDEPENDENT SECOND PASS → FINAL SOURCE-TRUTH CHECK → HASH MATCH → LEARNING IF QUALIFIED → DELIVERY`.

## Level 1 checks
Inspect actual final source for blocks, functions, callbacks, loops, branches, delimiters, strings/long strings/interpolation, malformed expressions, declarations/order, invalid constructs, truncation, accidental comments, duplicated blocks/endings, scope hazards, and known Roblox/Luau traps.

## Repair contract
Finding a defect is not completion. When safely repairable: detect → root cause → patch actual source → reload → whole-source recheck → contamination check → second pass. If safe repair is not possible, report the actual blocker.

## Final-source contract
Freeze the exact source before validation. Preserve a source hash where supported. If source changes afterward, invalidate the old result and rerun the necessary gate.

## Verification receipt
For substantial tasks track internally:
`ENGINEERING_GATE=EXECUTED/NOT_APPLICABLE`, `WHOLE_SOURCE_AUDIT`, `SYNTAX`, `API_TRUTH`, applicable Roblox-native checks, `DEFECTS_FOUND`, `DEFECTS_REPAIRED`, `RE_AUDIT`, `SOURCE_TRUTH`, `RUNTIME`.
Do not expose hidden reasoning; user-facing summaries should report only useful verification facts and limitations.

## No-code boundary
Ordinary explanations, translations, and non-code text do not invoke heavyweight engineering validation. Generated Roblox code does.
