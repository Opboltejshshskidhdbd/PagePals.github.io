# Domain rules: adversarial review and final audit gate

Load for substantial or backend deliverables before declaring completion. Source: v1.6.0-docs enforcement sections 13, 14, 15, 16 (restored verbatim).

## Proof rules: Adversarial failure matrix

Attack relevant paths including: duplicate UI connections; stale PlayerGui; respawn during animation; destroyed effect owners; leaked VFX; unused config; animation never consumed; unused audio; camera controller conflicts; duplicate input bindings; keyboard-only assumptions; server result after UI destruction; streaming-missing Instances; rejected client prediction; replication before controller initialization; orphaned remotes; client authority leaks; excessive effect/remote creation; RenderStepped leaks; incorrect effect-pool ownership; partial transactions; reservation leaks; stale sessions; duplicate operations; lost/duplicated ACKs; recovery races; unbounded queues/history.

Trace findings to actual code and patch where possible. Do not turn detection into prose-only fixes.

## Proof rules: Final audit gate

A Requirements — explicit requirements map to implementation.
B Architecture — required components and Studio hierarchy exist.
C Code — required components are real, not prose/placeholders.
D Authority — client/server ownership is correct.
E Invariants — critical state invariants are enforced.
F Concurrency — relevant races are handled.
G Persistence — durable state/recovery exists where required.
H Idempotency — retry semantics match the backend contract where required.
I Security — trust boundaries are enforced.
J Lifecycle — players, characters, Instances, connections, tasks, effects, UI, animations, camera, and sessions clean up.
K Protocol — schema/ACK semantics match code and the backend contract where applicable.
L Presentation — required UI/VFX/SFX/animation/camera/input paths are wired.
M Replication/Streaming — state and dynamic Instances behave correctly.
N Performance — budgets and claims match evidence.
O Recovery — failure paths have executable recovery where required.
P Verification — important failure scenarios are traced against actual code.
Q Regression — known bug classes are checked.

Any failed required gate blocks a complete/production-ready claim.

## Proof rules: Truthful verification

Distinguish STATIC REVIEW, REASONED REVIEW, SIMULATED FAILURE ANALYSIS, and ACTUAL EXECUTION. Never claim Roblox Studio execution, profiler measurements, live API verification, or runtime testing without evidence.

If a requested check was not run, report it as NOT_EXECUTED/UNVERIFIED. A missing tool is not a PASS.

## Proof rules: Reporting contract

Report concise conclusions, actual code-path evidence, status, verification level, limitations, and unresolved findings. Do not expose hidden chain-of-thought.

Permanent rule: **ROBLOX FEATURE ≠ SERVER LOGIC ONLY.**
