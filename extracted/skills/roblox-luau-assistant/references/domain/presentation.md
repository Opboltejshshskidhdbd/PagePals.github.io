# Domain rules: presentation (UI, VFX, SFX, animation, camera)

Load for PRESENTATION or GAMEPLAY tasks that touch UI, VFX, audio, animation, camera or feedback. Source: v1.6.0-docs main sections 6, 7, 11 and enforcement sections 7, 8 (restored verbatim).

## Build rules: UI engineering

Treat GUI as a real subsystem. When required, provide actual ScreenGui/PlayerGui hierarchy and controllers using Frame, TextLabel, TextButton, ImageLabel/ImageButton, ScrollingFrame, ViewportFrame, layouts, constraints, CanvasGroup, BillboardGui, SurfaceGui, and other appropriate primitives.

Complex UI should model explicit states such as CLOSED, OPENING, OPEN, CLOSING, LOADING, READY, ERROR, DISABLED where applicable. Prevent duplicate connections, stale callbacks, destroyed references, competing tweens, duplicate RemoteEvent listeners, and PlayerGui/respawn bugs. Support keyboard/mouse, touch, and gamepad where relevant. Prefer stable UI trees and state updates over rebuilding large trees every frame.

UI is never an authority boundary: UI → controller → validated request → server → result → UI update.

## Build rules: VFX, audio, animation, and camera

When visual/audio feedback is part of the feature, implement it rather than leaving comments. Use Roblox primitives such as ParticleEmitter, Beam, Trail, Attachment, Highlight, lights, TweenService, RunService only where per-frame work is truly required, models, Sound/SoundService, Animator/Animation/AnimationTrack, and camera effects.

Every temporary VFX/SFX resource defines owner, creation, activation, lifetime, and cleanup; use pooling when justified. Audit particle/attachment/beam/trail counts and effect lifetime.

Animation requires a runtime consumer that loads/plays/controls tracks; audit priority, looping, blending, markers, playback speed, respawn, caching, duplicate tracks, stale Animator references, and state conflicts.

Camera systems require explicit ownership/priority and START → UPDATE → STOP → RESTORE semantics where they modify camera state. Coordinate CurrentCamera, CameraType, CameraSubject, FOV, shake/recoil/zoom/lock-on/spectating, and RenderStepped/BindToRenderStep use; do not allow competing loops to overwrite camera state.

Audio must distinguish world/player/UI/global ownership and audit positional behavior, rolloff, volume, playback speed, sound groups, looping, lifetime, cleanup, and client/server trigger ownership. Presentation-only audio should not be unnecessarily replicated.

## Build rules: Presentation call graph

For important player-facing effects trace:
PLAYER ACTION → INPUT HANDLER → CONTROLLER → SERVER REQUEST → SERVER RESULT → REPLICATION/ACK → PRESENTATION CALL → ACTUAL UI/VFX/SFX/ANIMATION/CAMERA MUTATION → CLEANUP.

A missing required link prevents a complete claim.

## Proof rules: UI proof

Verify actual ScreenGui/PlayerGui hierarchy and controller wiring. Audit explicit UI states, duplicate connections, stale callbacks, destroyed references, overlapping tweens, PlayerGui replacement, loading/error/empty/disabled states, and relevant keyboard/mouse/touch/gamepad behavior.

UI-triggered authority must follow UI → controller → validated server request → server → result → UI update. UI itself never proves server authority.

## Proof rules: VFX/audio/animation/camera proof

Verify actual runtime consumers, not configuration alone. VFX must have effect hierarchy/configuration, caller, activation, timing, owner, bounded lifetime, cleanup, and pooling when justified. Reject "Play VFX here" comments as implementation.

Audio must have actual Sound/SoundService consumers and correct ownership/cleanup. Animation must have Animator/AnimationTrack consumption, lifecycle, priority/blending/markers as relevant, and no stale/duplicate tracks. Camera systems must have OWNER/PRIORITY/START/UPDATE/STOP/RESTORE semantics and no competing overwrite loops.
