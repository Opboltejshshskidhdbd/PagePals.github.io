---
name: roblox-intent-compiler
description: Expands short or vague Roblox requests (for example "make an OP inventory", "fishing UI", "fire ability") into a compact Spec Card of explicit, defaulted and assumed requirements with Roblox-specific defaults, then builds the smallest complete slice. Use for any feature request that is shorter than a full specification. Also records standing user preferences such as UI size or theme.
---
# ROBLOX INTENT COMPILER v1.0

Goal: the user writes 5-20 words and gets what an experienced Roblox developer would build, without a 500-line prompt and without silently inventing scope.

## When
Feature or UI/VFX requests without a spec. Skip for pure questions and for requests that already list their requirements.

## Procedure
1. Classify: UI screen / gameplay system / ability + VFX / data + persistence / world interaction / bugfix. Load the matching section of `skills/roblox-luau-assistant/references/intent-defaults.md`, plus `ui-defaults.md`, `vfx-defaults.md` and `asset-icon-policy.md` from the same folder when relevant.
2. Show a SPEC CARD (max 12 lines, before the code) with four labels:
   - EXPLICIT: what the user actually said.
   - DEFAULTED: choices taken from the defaults file; the user can override any of them.
   - ASSUMED: guesses that change behaviour, each with the cheapest way to change it.
   - NOT INCLUDED: up to 3 next upgrades. Do not build them.
3. Ask at most ONE question, and only if a wrong guess is expensive: persistence schema, real-money purchases, destructive actions, or authority that exploiters could abuse. Otherwise proceed; the card carries the assumptions.
4. Scope: build the smallest complete vertical slice (server authority + client presentation + cleanup) for what was asked. Persistence is never implied: say "in-memory only" when no data layer was requested.
5. Traceability: after building, every Spec Card line must map to a file/line or be marked NOT IMPLEMENTED. A mismatch is reported with the enforcement skill's status system, never hidden.
6. Standing preferences: when the user states one ("make UI smaller", theme, naming), put it under PREFERENCES in the card and apply it to every later request in the same project. Implement size preferences as ONE config value (`UIConfig.Scale`), never as scattered numbers. If the host cannot persist, tell the user to paste the preferences line next time.
7. Overrides: a short sentence ("smaller", "no animation", "dark theme") edits the current card's defaults. Do not regenerate unrelated parts.

## Card example
```
SPEC CARD: Inventory (client UI + server data)
EXPLICIT: inventory for a fishing game
DEFAULTED: 4-column grid, rarity colors, search + category tabs, detail panel, close button, compact size (panel <= 62% width), drawn icon badges
ASSUMED: items come from a server-owned ItemDB; no trading; in-memory only
NOT INCLUDED: DataStore save, trading, drag and drop
PREFERENCES: UIConfig.Scale = 0.9 (user asked for smaller UI)
```

## Hard rules
- Never invent asset IDs and never use emoji as icons (see `asset-icon-policy.md`).
- Card length is proportional: a SIMPLE request gets a 3-line card.
- The syntax gate and the enforcement skill still apply to the generated code.
