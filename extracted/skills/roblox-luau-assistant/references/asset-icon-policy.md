# Asset and icon policy

## Truth about assets
This plugin cannot browse or verify the Creator Store. Any numeric asset ID it writes by itself is unverified. Therefore:
- Never write an asset ID that the user did not supply. Never reuse one ID for several different items.
- Allowed sources: (a) IDs the user filled into `AssetManifest`, (b) built-in `rbxasset://` textures (for example the default particle textures), (c) UI drawn with Frames, `UICorner`, `UIStroke`, `UIGradient` and text.
- End every asset-dependent answer with a NEEDS ASSETS table: slot name, size, style, where it is used. The user fills the IDs.

## Emoji are not icons
Emoji that Roblox's font does not support render as empty boxes (visible as hollow squares in the UI and in the output window). Never use emoji as item icons, titles or log text. Use `IconProvider`.

## IconProvider pattern
```lua
-- AssetManifest.lua
return {
    Item_GoldenFish = {id = nil, note = "128x128 gold fish icon"},   -- fill with a real image asset ID
}
-- IconProvider.Get(itemId, parent): ImageLabel when an id exists and loads, otherwise a drawn badge
-- (rounded square in the rarity color + first letter of the item name).
```
- Validate at runtime: create the ImageLabel, `ContentProvider:PreloadAsync({imageLabel})`, then check `imageLabel.IsLoaded`; on failure swap in the drawn badge and `warn` once with the slot name (ASCII only).
- Keep all IDs in the manifest module, never inline in UI code.

## Getting real IDs (user steps)
1. Creator Store / Toolbox, Images (or upload your own to the experience). 2. Copy the asset ID from the page URL. 3. Paste it into the manifest slot. Verify the asset is an image and available to the experience; moderated or unavailable assets fail to load. (API_UNVERIFIED: confirm decal-versus-image behaviour in the docs.)
