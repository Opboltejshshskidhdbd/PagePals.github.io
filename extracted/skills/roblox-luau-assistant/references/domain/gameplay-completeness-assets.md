# Domain rules: gameplay feel, completeness, assets/content

Load for GAMEPLAY features and any task that references assets. Source: v1.6.0-docs main sections 10, 13 and enforcement section 3 (restored verbatim).

## Build rules: Gameplay feel and full-stack completeness

For player-facing mechanics assess responsiveness, anticipation, impact feedback, animation/VFX/SFX timing, camera/UI/cooldown feedback, hit/movement feedback, and transitions only where justified.

A subsystem counts as implemented only when the actual runtime path exists:
requirement → object/module → caller → state/presentation mutation → Roblox Instance/state → cleanup → failure behavior.

Examples of incomplete wiring: VFX service with no caller; animation config with no Animator consumer; UI controller with no matching hierarchy; camera service overwritten by another loop; sound config with no Sound consumer; remote with no valid producer/consumer path.

Use statuses: IMPLEMENTED, PARTIALLY IMPLEMENTED, NOT IMPLEMENTED, NOT WIRED, CONFLICTING, UNVERIFIED; engineering defects use FIXED, PARTIALLY_FIXED, OPEN, UNVERIFIED.

## Build rules: Asset/content and API accuracy

Never invent asset IDs. Use clearly marked placeholders when unavailable and identify the production replacement. Configuration is not implementation until a runtime consumer uses it.

Authority order for API behavior:
1. Official Roblox Creator Hub / Engine API / Luau documentation
2. Packaged Roblox dataset
3. Curated external references
4. Curated GitHub references
5. General model knowledge

**Dataset authority:** the packaged dataset contains **illustrative patterns, unvalidated until a dataset_report exists; never above official Roblox docs**. Do not claim live retrieval, Studio execution, profiler results, or API verification without evidence.

## Proof rules: Detection is not a fix

A proposed fix, explanation, TODO, comment, architectural recommendation, or future-work note is never a patch. When a defect is found: identify root cause, locate exact code path, modify actual implementation, trace affected callers/state boundaries, rerun the relevant failure scenario against changed code, and only then mark FIXED. Otherwise use OPEN, PARTIALLY_FIXED, or UNVERIFIED.
