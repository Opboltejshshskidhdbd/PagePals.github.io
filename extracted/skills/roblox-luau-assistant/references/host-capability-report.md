# Host Capability Report — Real Luau Validator Bridge

## Audited target
- Plugin: `roblox-luau-assistant`
- Display name: Roblox Dev Master
- Audited package version: `1.9.2-docs`
- Current release at audit: `pluginrel_6ac27a11b0588191bd39de9086aa8271`

## Interfaces actually inspected
1. Plugin Creator `get_plugin_metadata`
2. Plugin Creator `get_plugin_files`
3. Plugin Creator `get_owned_plugin_archive`
4. Plugin Creator `list_plugin_releases`
5. Plugin Creator `update_plugin`
6. Plugin Creator `create_plugin`
7. Available tool/action metadata (`ALL_TOOLS`) for Plugin Creator, MCP/server registration, executable/process/Python boundaries, and validator-specific actions
8. Current plugin manifests and executable validator files

## Findings
| Capability | Result | Evidence boundary |
|---|---|---|
| Validator file exists | YES | `scripts/luau_syntax.py` exists |
| Validator can execute locally | YES | Local parser/acceptance execution was reproduced for 1.9.2 |
| Plugin generation flow can call validator | NO PROOF / BLOCKED | No validator-specific callable MCP action is exposed in the inspected host tool surface |
| Validation enforced before ordinary generation delivery | NO PROOF / BLOCKED | No host-callable validator result is available to gate the model's final response |
| Python/process execution exposed to plugin generation | NOT EXPOSED | No approved executable/process action was found in the inspected plugin/tool surface |
| Custom MCP/backend registration through current Plugin Creator mutation API | NOT AVAILABLE | Current mutation API accepts plugin archives; it does not expose a server/tool registration operation |
| Validator-specific MCP action | NOT FOUND | No `validate_luau_source`/equivalent callable action exists in the available tool metadata |

## Architectural blocker
**HOST_CAPABILITY_LIMITATION + TOOL_REGISTRATION_LIMITATION**.

The package can ship Python source and instructions, but packaging a Python file does not register it as a callable MCP tool. The currently exposed Plugin Creator mutation surface can update package contents but does not provision an executable validator action for the ordinary generation flow.

## Required capability to remove the blocker
A supported host/backend tool must be registered and callable by the generation flow, with a contract equivalent to:

`validate_luau_source(source, source_name, source_hash)`

The action must return the exact validated-source hash and structured diagnostics. The generation flow must then make that result a mandatory delivery gate.

## Truth rule
Until such a callable bridge exists and an end-to-end invocation is recorded, the correct states are:
- `VALIDATOR_PRESENT`
- `VALIDATOR_LOCALLY_EXECUTABLE`
- `VALIDATOR_HOST_CALLABLE = false`
- `VALIDATION_ENFORCED = false`
- final generation syntax state: `VALIDATION_UNAVAILABLE` or `VALIDATION_BLOCKED`

`SYNTAX_VERIFIED` must not be emitted for ordinary generation solely from package-local execution.
