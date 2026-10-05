# UI defaults (design tokens and layout rules)

Reference viewports for every layout: phone landscape 844x390, tablet 1180x820, desktop 1920x1080. Check each one mentally (or with the Studio device emulator) before delivering.

## Size (default is COMPACT)
- Panel width: phone min(88% of viewport, 560px); tablet/desktop min(62% of viewport, 720px). Panel height at most 78% of viewport height. Never more than 80% of either dimension at default size.
- Enforce with `UISizeConstraint` (MaxSize) on the panel; put `UIScale` on the root and drive it from ONE config module: `UIConfig = { Scale = 0.9, Padding = 12, CornerRadius = 12 }`.
- "Make the UI smaller/larger" means changing `UIConfig.Scale` (steps of 0.1), nothing else. Record the user's choice as a standing preference.

## Safe area (Roblox top bar and device cut-outs)
- Do not use `IgnoreGuiInset = true` for panels or HUD; it lets the UI sit under the Roblox menu/chat buttons. Use `ScreenGui.ScreenInsets = Enum.ScreenInsets.TopbarSafeInsets` (verify the enum member in the official docs: API_UNVERIFIED until checked).
- Full-screen backgrounds/overlays (vignette, flash) may ignore insets; interactive UI must not.
- Keep a 12px margin from the edges.

## Text
- Explicit TextSize tokens: title 22-26, body 14-16, caption 12-13. Minimum 12. Add `UITextSizeConstraint` when using TextScaled.
- Every dynamic label: `TextTruncate = Enum.TextTruncate.AtEnd`, fixed row height, wrapped in a layout.
- Never put two text elements on the same line without a layout. A count badge lives in its own corner region (top-right, with padding) and the name label reserves that width, so they cannot overlap.
- Body text contrast at least 4.5:1; do not use faint grey for primary information.

## Layout
- Use `UIListLayout` / `UIGridLayout` / `UIPadding`; compute `CellSize` from the container; `ScrollingFrame` with `AutomaticCanvasSize = Y`; `ClipsDescendants = true` on panels.
- Spacing scale 4 / 8 / 12 / 16 / 24. Corner radius 8-14. Stroke 1-2.
- Touch targets at least 44x44 px; hover effects only when not `UserInputService.TouchEnabled`.

## State machine (prevents "Loading..." on top of content)
- Every screen has Loading / Ready / Empty / Error; exactly one is visible. The loading overlay is hidden or destroyed before Ready is shown, and no placeholder text stays in the tree after init.
- If data is not ready within 5 s: show Error with a Retry button.
- Initialization is idempotent and cleans connections on close.

## Motion
- Open: scale 0.95 to 1 plus fade, 0.18 s, Quad Out. Hover: 0.12 s. Tween cleanup on close. Nothing animates every frame.

## Output hygiene
- ASCII-only log messages: no emoji in `print`/`warn`/`error` (they render as empty boxes in the output window). Prefix logs with `[ModuleName]`.

## Pre-delivery UI checklist
1. Panel fits at 844x390, 1180x820, 1920x1080 and is at most 80% of both dimensions.
2. Nothing sits under the top bar; no overlapping text.
3. Icons come from `IconProvider` (asset or drawn badge), never raw emoji.
4. One visible state at a time; loading cannot stay visible.
5. All dimensions come from `UIConfig`.
6. Run `python scripts/ui_lint.py <files>` if code execution is available.
