# Changelog

## 1.12.0-gate - real syntax parser, UI/VFX/asset rules, intent compiler

### Why
Generated UIs had overlapping text, panels slightly too large, content under the Roblox top bar, "Loading..." left on screen, empty-box glyphs from unsupported emoji, fabricated asset IDs, and a runtime "missing method Init" error. Generated Luau also had syntax errors that the plugin reported as SYNTAX_VERIFIED.

### Verified problems fixed
- The 1.11.0 block-counting validator accepted 16 of 23 broken test snippets as SYNTAX_VERIFIED and rejected valid if-expressions. Replaced by a full parser (`scripts/luau_parser.py`) behind the same API (`scripts/luau_syntax.py`): 23/23 broken snippets rejected, 0 false rejects on the test set.
- The test files were never executed by CI (functions were defined but not called). Added `tests/run_all.py`; the workflow now runs it.
- The `strong-analyzer` CI job was an `echo` (always green). Replaced by a real job that is skipped until GLOBAL_TYPES_URL is set.
- `validate_dataset.py` looked for code keys the dataset does not have, so it validated nothing. Replaced; dataset is now syntax+lint checked (435 code entries, 0 failures) with near-duplicate report (210 effectively unique).
- The syntax corpus had 4 cases; now 26 cases whose wrong snippets must be rejected and right snippets accepted.
- UI/VFX/input/lifecycle/performance rules were referenced as "preserved" but absent from the package; restored under `references/domain/` and routed from the main skill.

### Added
- `skills/roblox-intent-compiler` (Spec Card: EXPLICIT / DEFAULTED / ASSUMED / NOT INCLUDED, one-question limit, standing preferences) and `intent-defaults.md`.
- `ui-defaults.md` (compact size, UIConfig.Scale, safe area, text rules, state machine, checklist), `vfx-defaults.md`, `asset-icon-policy.md`.
- `scripts/ui_lint.py` + 17 tests (emoji in logs/UI text, repeated/fabricated asset IDs, top-bar overlap, oversized panels, loading never hidden, unguarded Init).
- Dataset shards with search tool; one canonical references folder; stale stray files removed.

### Not verified
- No official Luau compiler, luau-lsp, Roblox Studio or device run. The parser is a Python implementation. The CI workflow was never run. `Enum.ScreenInsets.TopbarSafeInsets` and decal-versus-image behaviour are marked API_UNVERIFIED until checked in the official docs. UI lint is static, not a layout test.

## 1.12.0-gate — Automatic Engineering Gate + API Truth Gate

### Added
- Automatic risk-based Engineering Gate as default behavior for Roblox code generation/modification/repair.
- Automatic whole-source structural/syntax audit before final code delivery.
- Automatic actual-source repair and current-source re-audit contract.
- Automatic Roblox API Truth Gate using the official-source hierarchy.
- Explicit `API_UNVERIFIED` / `API_BEHAVIOR_UNVERIFIED` states.
- Documentation-truth vs implementation-source-truth separation.
- Automatic gate acceptance benchmark A–I.
- Automatic verification-receipt contract for substantial code-generation tasks.

### Preserved
- Whole-source defect exhaustion and false-PASS prevention.
- Level 1/2 syntax truth boundaries and custom Luau parser.
- Exact-source/hash consistency and validator host truth boundary.
- Continuous learning, learning receipts, dataset intelligence, official-source hierarchy, Studio representation, networking/security, lifecycle, persistence, UI/VFX/SFX/input/camera/animation, performance/cleanup, and shared-learning truth boundaries.

### Truth boundary
This release changes default engineering behavior and API verification routing. It does not create an external validator or Roblox runtime capability that the host does not provide. Runtime and external-validator claims remain evidence-gated.
