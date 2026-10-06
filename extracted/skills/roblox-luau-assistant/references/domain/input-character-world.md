# Domain rules: input, character, physics, world

Load for tasks involving input handling, character lifecycle, physics or world systems. Source: v1.6.0-docs main section 8 and enforcement section 9 (restored verbatim).

## Build rules: Input, character, physics, and world

Use UserInputService and/or ContextActionService appropriately; separate input detection from gameplay intent and authority. Support relevant platforms.

For characters handle CharacterAdded/Removing, Humanoid, HumanoidRootPart, Animator, death, respawn, missing descendants, streaming, player leaving, and reinitialization.

For physics/world systems reason about BasePart/assemblies, constraints, collision groups, raycasts, overlap queries, network ownership, Anchored/mass, impulses/forces, Workspace hierarchy, tags, spawn points, Terrain, Lighting, Atmosphere, environmental audio, interactive objects, and StreamingEnabled. Prefer physics primitives/events over polling. Do not trust client-reported authoritative physics outcomes.

## Proof rules: Input/character/physics/replication proof

Verify input detection is separated from intent and authority; relevant platforms are supported. Verify CharacterAdded/Removing, death, respawn, missing descendants, streaming, and player leave behavior where required.

Verify physics/network ownership, raycasts/overlap/constraints/collision groups, and server-authoritative outcomes where required. Verify state classification and correct use of engine replication, Attributes, RemoteEvent/RemoteFunction/UnreliableRemoteEvent, and local presentation.
