# Roblox Dev Master v1.12.0-gate Coverage Matrix

| Area | Location |
|---|---|
| Intent compiler (short prompt -> Spec Card, defaults, preferences) | skills/roblox-intent-compiler/SKILL.md + skills/roblox-luau-assistant/references/intent-defaults.md |
| UI defaults (compact size, safe area, text overlap, states, motion) | skills/roblox-luau-assistant/references/ui-defaults.md |
| VFX defaults (budgets, feel, cleanup) | skills/roblox-luau-assistant/references/vfx-defaults.md |
| Asset and icon policy (no invented IDs, no emoji icons, IconProvider) | skills/roblox-luau-assistant/references/asset-icon-policy.md |
| Domain build/proof rules (UI, VFX/SFX/animation/camera, input/character/world, replication, lifecycle, performance, assets, audit) | skills/roblox-luau-assistant/references/domain/*.md |
| Syntax validation (full parser, 26-case regression corpus, 32+ executed tests) | scripts/luau_parser.py, scripts/luau_syntax.py, skills/roblox-luau-assistant/references/syntax-regression-corpus.json, tests/ |
| UI/asset/lifecycle lint | scripts/ui_lint.py, tests/test_ui_lint.py |
| Dataset (shards, search, reports) | skills/roblox-luau-assistant/references/dataset/, dataset_report.json, dedupe_report.json, dataset-validation-manifest.json |
| Automatic engineering gate, API truth gate, whole-source exhaustion | skills/roblox-luau-assistant/references/automatic-engineering-gate.md, api-truth-gate.md, whole-source-defect-exhaustion.md |
| Backend contracts | skills/roblox-luau-assistant/references/backend-contracts.md |
| Learning and shared learning | skills/roblox-continuous-learning, skills/roblox-shared-learning, skills/roblox-luau-assistant/references/automatic-learning.md, shared-knowledge-contract.md |
| CI | .github/workflows/luau-validation.yml (tests job real; analyzer job skipped until GLOBAL_TYPES_URL is set; never run by me) |

Documentation traceability, not benchmark evidence.
