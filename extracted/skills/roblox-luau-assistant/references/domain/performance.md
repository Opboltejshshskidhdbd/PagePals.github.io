# Domain rules: performance

Load when the task has frequent updates, many instances, effects or network traffic. Source: v1.6.0-docs main section 12 and enforcement section 10 (restored verbatim).

## Build rules: Performance

Audit particle emission/lifetime, textures/attachments, beam/trail count, Instance cloning, pooling, UI Instance count, RenderStepped/Heartbeat connections, tween creation, camera update frequency, animation loading, sound lifetime, remote frequency, and streaming. Do not use RenderStepped for work that does not need per-frame execution. Bound high-frequency work and avoid unnecessary server-side presentation.

## Proof rules: Performance proof

Audit particle emission/lifetime, texture/attachment count, beam/trail count, cloning/pooling, UI Instance count, RenderStepped/Heartbeat connections, tween creation, camera update frequency, animation loading, sound lifetime, remote frequency, and streaming. Reject unbounded high-frequency work and unnecessary RenderStepped usage.
