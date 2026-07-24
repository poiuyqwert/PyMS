# MegaTile Editor
The MegaTile Editor edits a MegaTile as its 4x4 grid of MiniTiles — both which MiniTile graphics it uses ([.vx4](/Help/Files/Tilesets/VX4.md)) and the per-MiniTile flags ([.vf4](/Help/Files/Tilesets/VF4.md)) that control walkability, height, sight blocking, and ramps. It is embedded in the **MegaTile** panel of the [PyTILE](/Help/Programs/PyTILE.md) main window for the selected MegaTile, and also opens as its own dialog when editing MegaTiles from the [Tile Palette](/Help/Programs/PyTILE/Tile_Palette.md).

## Edit Modes
The dropdown above the MegaTile picks what clicking a MiniTile does, and each mode has a keyboard shortcut:

- **Minitile** (`m`): Selects a MiniTile. The **ID** entry sets which MiniTile graphic is used in the selected spot, with a find button to pick one visually from the MiniTile [Tile Palette](/Help/Programs/PyTILE/Tile_Palette.md), and an edit button to open the [MiniTile Editor](#minitile-editor).
- **Flip** (`f`): Toggles the MiniTiles horizontal flip.
- **Height** (`h`): Paints the height selected in the dropdown below the MegaTile — **Low (Red)**, **Mid (Orange)**, or **High (Yellow)**. Each MiniTiles current height is shown as a border in its color.
- **Walkable** (`w`): Toggles the walkable flag (green = walkable, red = unwalkable).
- **Block view** (`b`): Toggles the blocks sight flag (red = blocks sight, green = doesn't).
- **Ramp?** (`r`): Toggles the ramp flag (green = set, red = not). The exact use of this flag is uncertain.

In the flag modes, clicking a MiniTile toggles it, dragging paints the same state across MiniTiles, and right clicking applies the clicked state to all 16 MiniTiles at once.
The corresponding group flags marked with `*` on the [Tile Groups](/Help/Programs/PyTILE/Tile_Groups.md#flags) page get overwritten by StarCraft based on these per-MiniTile flags, so this editor is where those behaviors are really controlled.

## Apply to Megas
In the main window, the **Apply to Megas** button (shown in the flag edit modes) copies the selected MegaTiles flags to all the other MegaTiles in the group:

- Apply only the current modes flags: `Shift+Ctrl+H` (Height), `Shift+Ctrl+W` (Walkability), `Shift+Ctrl+B` (Blocks View), or `Shift+Ctrl+R` (Ramp).
- Apply all flags: `Shift+Ctrl+A`.
- **Exclude Null Tiles** (`Shift+Ctrl+N`): When checked, MegaTile 0 (the null tile) is skipped when applying.

## Copying MegaTile Flags
The **Copy MegaTile Flags** panel in the main window copies flags between MegaTiles through the clipboard. Check the flag types you want (**Height**, **Walkable**, **Blocks Sight**, and **Ramp**), then press **Copy** (`Shift+Ctrl+C`) to copy them from the selected MegaTile, and **Paste** (`Shift+Ctrl+V`) to apply them to another selected MegaTile. The clipboard contents are plain text in the same format as [exported MegaTile settings](/Help/Programs/PyTILE/Importing_and_Exporting.md#settings), so you can also edit the text before pasting, or paste between PyTILE windows.

## MiniTile Editor
The MiniTile Editor is a pixel editor for the 8x8 MiniTile graphics stored in the [.vr4](/Help/Files/Tilesets/VR4.md) file. It opens from the edit button in **Minitile** mode, or when editing MiniTiles from the [Tile Palette](/Help/Programs/PyTILE/Tile_Palette.md).
The left side shows the MiniTile enlarged (with an actual size preview below it), and the right side shows the tilesets 256 color `.wpe` palette. Left clicking a pixel paints with the foreground color and right clicking paints with the background color; drag to paint multiple pixels. Click a palette swatch with the left or right mouse button to set the foreground or background color, or click the eyedropper and then a pixel to pick that pixels color instead. Press **Ok** to apply — since MiniTile graphics are shared, every MegaTile using the MiniTile is affected.

## See Also
- [PyTILE](/Help/Programs/PyTILE.md)
- [Tile Groups](/Help/Programs/PyTILE/Tile_Groups.md)
- [Tile Palette](/Help/Programs/PyTILE/Tile_Palette.md)
- [.vf4](/Help/Files/Tilesets/VF4.md)
- [.vx4](/Help/Files/Tilesets/VX4.md)
- [.vr4](/Help/Files/Tilesets/VR4.md)
