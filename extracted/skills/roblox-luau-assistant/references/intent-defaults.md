# Intent defaults by feature type (starting points, user can override)

## UI screen (inventory, shop, quests, settings, HUD)
- Slice: one ScreenGui, one controller LocalScript, one data ModuleScript; server owns the data, client only renders and requests.
- Inventory: grid + search + category tabs + detail panel; items from a server ItemDB; actions go through a validated RemoteEvent.
- Shop: server validates price, stock and currency; client shows preview only; purchase is a single server transaction; no real-money flow unless asked.
- Quests: server-owned progress; client shows list + progress bars; rewards granted by the server once (idempotent).
- Settings: client-only preferences stored in attributes or a local table; persist only when asked.
- HUD: read-only bindings to attributes/leaderstats; no gameplay logic in UI.
- Always: Loading / Ready / Empty / Error states, open/close with one tween, cleanup of connections on close, compact size per `ui-defaults.md`.

## Gameplay system (combat, interaction, tycoon, pets)
- Server authority for damage, currency, cooldowns, ownership. Client: input, prediction, feedback.
- Remotes: validate types, finite numbers, distance, cooldown, state; rate limit per player.
- Lifecycle: handle CharacterAdded/Removing, PlayerRemoving, respawn, stale references; one Janitor per player/character.

## Ability + VFX
- Slice: server ability module (validate, cooldown, hit detection) + client VFX handler (cosmetic) + SFX + camera feedback.
- Use `vfx-defaults.md` budgets. VFX is cosmetic and client-side; damage is server-side.

## World interaction (ProximityPrompt, doors, pickups)
- Tag objects with CollectionService; bind per-tag behaviour with Instance-added/removed signals; server validates the interaction (distance, state, ownership); debounce per player.

## Data + persistence (only when requested)
- Use `skills/roblox-luau-assistant/references/backend-contracts.md`. Session locking, UpdateAsync, retries, BindToClose. State clearly what is and is not saved.

## Bugfix
- Reproduce from the error text, search the whole source for the same defect class, fix all occurrences, re-parse with `scripts/luau_syntax.py`.
