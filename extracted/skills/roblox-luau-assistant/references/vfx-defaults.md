# VFX defaults (budgets and feel)

## Roles
- Gameplay (damage, hits, cooldowns) = server. Visuals/audio/camera feedback = client. Replicate only an effect name, origin, direction and optionally a seed.

## Budgets
| Effect | Particles per burst | Lifetime | Extras |
|---|---|---|---|
| Hit spark | 8-15 | 0.2-0.4 s | 1 short light pulse, SFX with pitch variance +-8% |
| Aura (looping) | rate 20-40 | 0.8-1.4 s | stop emitter on cleanup |
| Projectile trail | Trail 0.3-0.5 s | - | cap one trail per projectile |
| Explosion | up to 60 | 0.4-0.9 s | ring 0.4-0.5 s, light 0.4-0.6 s, camera shake <= 0.5 s |
| Ground slam | ring + 10-14 debris parts | debris 2-3 s | debris anchored or cleaned with Debris |
- Mobile caps: at most 150 live particles per effect and 3 heavy effects at once; scale counts with the graphics quality level.

## Feel
- Anticipation 0.15-0.4 s before impact, Out easing for impacts, InOut for loops, color roles primary / accent / dark, one hero shape per effect.
- Pair every impact with SFX; keep camera shake short; hitstop only for heavy hits.

## Technical rules
- Use `ParticleEmitter:Emit(n)` for bursts, `Rate` for loops. Anchor decorative parts, set `CanCollide`, `CanQuery`, `CanTouch` to false. Clean up with `Debris:AddItem` or a Janitor. No unbounded loops.
- Textures: built-in `rbxasset://textures/particles/*.dds` unless the user supplies asset IDs (see `asset-icon-policy.md`). Never invent IDs.
- The dataset (`references/dataset/`) has tested-style element patterns; search it with `search_dataset.py` and adapt, do not paste blindly.
