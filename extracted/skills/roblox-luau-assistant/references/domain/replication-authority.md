# Domain rules: replication, authority, networking

Load for any client/server interaction. Source: v1.6.0-docs main section 9 (restored verbatim).

## Build rules: Replication, authority, and networking

Classify important state as SERVER AUTHORITATIVE, CLIENT PRESENTATION, CLIENT PREDICTION, REPLICATED STATE, or LOCAL-ONLY STATE.

Choose among engine replication, replicated Instances, Attributes, RemoteEvent, RemoteFunction only when justified, UnreliableRemoteEvent when loss is acceptable, and local-only presentation. Do not manually replicate state Roblox already replicates efficiently; do not use unreliable delivery where loss violates correctness.

Preserve schema validation, sequence handling, operation IDs, ACK semantics, rate limits, backpressure, replay protection, session generations, recovery, reservation safety, and server authority. Backend-specific semantics live in `references/backend-contracts.md` and must not be loaded for unrelated simple/presentation work.
