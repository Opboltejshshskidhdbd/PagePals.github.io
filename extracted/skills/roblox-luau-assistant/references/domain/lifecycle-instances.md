# Domain rules: Roblox-native runtime model, Instances, lifecycle

Load for substantial features. Source: v1.6.0-docs main sections 4, 5 and enforcement sections 5, 6 (restored verbatim).

## Build rules: Roblox-native runtime model

When applicable:
PLAYER INPUT → CLIENT CONTROLLER → CLIENT PREDICTION/PRESENTATION → SERVER INTENT → SERVER VALIDATION → AUTHORITATIVE STATE → REPLICATION/ACK → CLIENT STATE → UI/VFX/SFX/ANIMATION/CAMERA → CLEANUP.

Not every feature needs every layer. Determine the required layers from the feature contract.

Use correct Roblox boundaries: ServerScriptService, ServerStorage, ReplicatedStorage, StarterPlayer, StarterPlayerScripts, StarterCharacterScripts, StarterGui, PlayerGui, Workspace, Lighting, SoundService, Teams, TextChatService when relevant, CollectionService, RunService. Distinguish Script, LocalScript, and ModuleScript execution.

## Build rules: Instances, hierarchy, and lifecycle

Treat the Studio hierarchy and Instances as implementation state. Audit creation, parenting, cloning, Attributes, tags, descendants, replication, StreamingEnabled, ownership, destruction, and cleanup. Prefer Attributes over unnecessary ValueBase objects and event/tag registration over repeated large scans when appropriate.

Every connection/task/timer/temporary Instance/effect/cloned asset/subscription needs CREATE → OWNER → USE → RELEASE. Character systems must survive required spawn/death/respawn/leave paths. Validate dynamic references rather than assuming permanent character or PlayerGui objects.

## Proof rules: Full-stack feature contract

Audit, as relevant:
FEATURE REQUIREMENT → STUDIO HIERARCHY → SERVER SYSTEM → CLIENT CONTROLLER → SHARED CONFIG/TYPES → REMOTE PROTOCOL → AUTHORITATIVE STATE → REPLICATION → UI → ANIMATION → VFX → SFX → CAMERA → INPUT → CHARACTER/WORLD → LIFECYCLE → CLEANUP → PERFORMANCE → SECURITY → FAILURE BEHAVIOR.

The Studio hierarchy is part of the contract. Referenced Instances/folders must exist, be documented, or be explicit dependencies; code and hierarchy must agree.

## Proof rules: Lifecycle and resource proof

Audit Instance creation/parenting/cloning/attributes/tags/replication/streaming/ownership/destruction. Prefer event/tag registration over large repeated scans where appropriate.

Every temporary Instance, connection, task, timer, effect, cloned asset, and subscription must have CREATE → OWNER → USE → RELEASE. Check character, PlayerGui, UI, animation, camera, effect, and player leave/respawn paths.
