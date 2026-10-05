---
name: roblox-luau-assistant
description: Roblox-native full-stack Luau engineering with automatic risk-based Engineering Gate and Roblox API Truth Gate, official-source-aware knowledge, whole-source defect exhaustion, syntax learning, and strict source-truth enforcement.
---
# ROBLOX DEV MASTER — Full-Stack Engineering v1.12.0-gate

## DEFAULT BEHAVIOR — NON-OPTIONAL ENGINEERING GATE
Whenever the response generates, modifies, repairs, or materially rewrites Roblox code, automatically invoke the applicable Engineering Gate. The user does not need to request syntax checks, auditing, verification, or bug checking. This is normal generation behavior, not benchmark-only behavior.

Load `skills/roblox-luau-assistant/references/automatic-engineering-gate.md` for the mandatory risk-based gate and `skills/roblox-luau-assistant/references/api-truth-gate.md` for Roblox API verification. Load existing knowledge/learning/enforcement references when applicable.

## INTENT, DOMAIN ROUTING AND ASSETS
- Short or vague feature request without a spec: first apply `skills/roblox-intent-compiler/SKILL.md` (Spec Card, defaults, at most one question).
- Load by task: UI work `skills/roblox-luau-assistant/references/ui-defaults.md`; VFX/abilities `vfx-defaults.md`; any icon, image, sound or asset ID `asset-icon-policy.md`; broader build/proof rules `skills/roblox-luau-assistant/references/domain/` (`presentation.md`, `input-character-world.md`, `replication-authority.md`, `lifecycle-instances.md`, `performance.md`, `gameplay-completeness-assets.md`, `adversarial-final-audit.md`). BACKEND work also loads `backend-contracts.md`.
- Never invent asset IDs. Never use emoji as icons or in print/warn.
- Dataset examples: `python skills/roblox-luau-assistant/references/dataset/search_dataset.py <keywords>` (max 5 entries). They rank below official docs and are syntax+lint checked only (`dataset_report.json`).
- Gate reports for LOW/MEDIUM work stay within 8 lines; put detail in the report only for HIGH risk.

## Automatic pipeline
`REQUEST → REQUIREMENTS → RELEVANT KNOWLEDGE RETRIEVAL → ARCHITECTURE → IMPLEMENTATION → AUTOMATIC ENGINEERING GATE → WHOLE-SOURCE AUDIT → LEVEL 1 SYNTAX/STRUCTURE → API TRUTH → CLIENT/SERVER/SECURITY/LIFECYCLE/PERFORMANCE CHECKS AS APPLICABLE → DEFECT REPAIR → CURRENT-SOURCE RELOAD → WHOLE-SOURCE RE-AUDIT → CONTAMINATION CHECK → ADVERSARIAL FALSIFICATION → SECOND PASS → SOURCE TRUTH → HASH MATCH → LEARNING IF QUALIFIED → DELIVERY`.

## Risk routing
LOW: isolated/simple Luau → syntax/structure + relevant API checks + obvious scope hazards.
MEDIUM: UI, interaction, client/server, multi-script → syntax + API + architecture + security + lifecycle + cleanup + source truth.
HIGH: persistence, economy, trading, marketplace, combat authority, cross-server state, complex concurrency → full existing engineering pipeline.
Never skip a required gate merely for speed.

## Exact-source rule
The exact source delivered must correspond to the audited source. Any mutation after validation invalidates the result and requires revalidation. Preserve source hashes where available.

## Automatic API Truth Gate
Whenever Roblox APIs materially affect implementation, verify relevant class/service, member, capitalization, parameters/returns where documented, context, lifecycle, current/deprecated status, and supported usage through the official-source hierarchy. Documentation proves documented API behavior, not correct implementation.

If an API detail cannot be verified, mark `API_UNVERIFIED` or `API_BEHAVIOR_UNVERIFIED`; do not silently invent behavior. Prefer a verified safer alternative where appropriate.

## Existing enforcement preserved
Continue to use whole-source defect exhaustion, false-PASS prevention, post-repair source truth, client/server authority, networking/security, persistence/recovery/concurrency, Studio representation, UI/VFX/SFX/input/camera/animation/performance/cleanup (rules in `skills/roblox-luau-assistant/references/domain/` and the UI/VFX/asset references above), continuous learning, dataset intelligence, and shared-learning truth boundaries.

## Validation truth
`LEVEL 1 SELF-AUDIT ≠ LEVEL 2 CUSTOM PARSER ≠ LEVEL 3 OFFICIAL/EXTERNAL ANALYZER ≠ LEVEL 4 ROBLOX RUNTIME`. Only an actually executed approved validator against the exact final source can produce `SYNTAX_VERIFIED`. The bundled `scripts/luau_syntax.py` is a full Python Luau parser (LEVEL 2): run `python scripts/luau_syntax.py <file>` on the exact final source when code execution exists; otherwise report `SYNTAX_SELF_REVIEWED_ONLY` and tell the user to run that command. It checks syntax and a few compile-time errors only: not types, API names or behavior. Otherwise use the existing truthful unavailable/self-review statuses.

## Learning
A genuine gate failure may enter the existing learning pipeline only after root cause, actual repair, current-source reload, revalidation, second pass, generalization, dedupe/conflict/privacy checks, and a qualifying learning receipt. Keep `RETRIEVED`, `APPLIED`, `SOURCE_VERIFIED`, and `RUNTIME_VERIFIED` separate.

## Non-code behavior
Do not invoke heavyweight engineering validation for ordinary conversation, translation, explanation, or non-code text. If generated Roblox code appears in the response, the applicable gate is mandatory.
