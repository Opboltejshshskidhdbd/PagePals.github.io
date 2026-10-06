---
name: roblox-continuous-learning
description: Evidence-gated automatic engineering learning for Roblox Dev Master, including syntax failures, model-generation failures, regressions, source-truth verification, privacy-safe generalization, and canonical persistence.
---

# ROBLOX DEV MASTER — Continuous Learning v4.0

Learning remains automatic, but retrieval alone is never learning.

## Automatic pipeline
`FAILURE/CORRECTION → CLASSIFY → ROOT CAUSE → REPRODUCE → REPAIR ACTUAL SOURCE → CURRENT-SOURCE RELOAD → WHOLE-SOURCE DEFECT EXHAUSTION → REPAIR CONTAMINATION → ADVERSARIAL FALSIFICATION → SECOND-PASS AUDIT → POST-REPAIR SOURCE TRUTH → REGRESSION → GENERALIZE → EVIDENCE → DEDUPE/CONFLICT → PRIVACY FILTER → PERSIST → FUTURE RETRIEVAL → PREVENTION → REGRESSION`

## Syntax-specific evidence
For syntax failures track:
- `SYNTAX_REPRODUCED`
- `SYNTAX_REPAIRED`
- `SYNTAX_REVALIDATED`
- `SYNTAX_REGRESSION_ADDED`

A syntax parser result is static evidence only. Never upgrade it to runtime evidence.

## Required learning receipt
For a reusable lesson preserve: failure class, root cause, actual repair, source-truth confirmation, validation result, regression status, generalization, prevention rule, evidence status, and reusable flag.

## Generalization
Do not memorize literal lines, project names, or private source. Prefer structural lessons such as composition-induced block mismatch, incorrect client/server ownership, stale lifecycle connections, or repair contamination.

## Model-generation failure category
Maintain `MODEL_GENERATION_FAILURES` for recurring assistant-created defects: extra/missing terminators, duplicate declarations, API-name errors, authority mistakes, lifecycle mistakes, UI hierarchy mistakes, invalid properties, RemoteEvent misuse, DataStore assumptions, type syntax mistakes, accidental one-line corruption, incomplete repairs, repair-induced defects, and false-PASS behavior.

## Evidence statuses
Keep the existing global statuses: `CANDIDATE`, `STATICALLY_VERIFIED`, `RUNTIME_VERIFIED`, `CROSS_VERIFIED`, `CONFLICTING`, `SUPERSEDED`, `CONTEXT_SPECIFIC`, `STATIC_NARRATIVE_ONLY`.

Do not claim `RUNTIME_VERIFIED` from syntax/parser results. Do not claim official compiler verification from the custom parser.

## Deduplication/conflicts
Before persistence check exact duplicates, near-duplicates, conflicts, obsolete/superseded rules, generic-Lua vs Luau scope, and Roblox-specific scope. Merge equivalent rules; preserve unresolved conflicts.

## Privacy
Generalize engineering failure, not private project details. Block persistence of usernames, place IDs, private paths, private assets, credentials, tokens, and private source identifiers.

## Canonical store
`skills/roblox-continuous-learning/LEARNED_KNOWLEDGE.md` remains the sole canonical persisted lesson store. Compatibility mirrors are not independent authorities.

## Final self-check
If root cause, current-source evidence, revalidation, falsification, second-pass audit, or persistence status is unavailable, report the limitation instead of claiming learned/verified completion.
