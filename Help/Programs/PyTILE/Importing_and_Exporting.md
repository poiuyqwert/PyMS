# Importing and Exporting
PyTILE can export tile graphics to BMP files and tile settings to editable text files, and import both back — the basis for creating custom terrain. All of the import/export actions are on the [Tile Palette](/Help/Programs/PyTILE/Tile_Palette.md) toolbar and operate on the palettes selected tiles.

## Graphics
**Export Graphics** (`Ctrl+E`) saves the selected tiles as a 256 color BMP using the tilesets `.wpe` palette. The BMP layout depends on the tile type:

- MegaTile Groups: each group is one row of its 16 MegaTiles, so the image is 512 pixels wide and 32 pixels tall per group.
- MegaTiles: a grid of 32x32 pixel tiles.
- MiniTiles: a grid of 8x8 pixel tiles.

**Import Graphics** (`Ctrl+I`) opens the import dialog, where you build a list of BMPs (**Set**, **Add**, and **Remove** buttons, with up/down buttons to reorder — the images are imported in list order). The images must match the export layout: width 512 and height a multiple of 32 for groups, and width/height multiples of 32 for MegaTiles or 8 for MiniTiles. The import is controlled by the settings below the list:

- **Reuse MegaTiles** / **Reuse MiniTiles**: To keep the tileset small, imported tiles can reuse existing tiles instead of always creating new ones. **Duplicates (Old)** reuses tiles already in the tileset that match the imported graphics, **Duplicates (New)** reuses matching tiles from earlier in the same import, and **Null** always reuses the given tile ID for matching tiles even when the duplicate options are off (with a find button to pick the null tile visually). MiniTile matching also detects horizontally flipped duplicates.
- **Replace palette selection**: Imports over the tiles selected in the palette instead of adding new tiles to the end.
- **Auto-close**: Closes the dialog after a successful import.
- **Reset to recommended settings**: Restores the recommended options — reuse duplicates on for MiniTiles, and off for MegaTiles.

If an import needs more MiniTiles than the tileset has room for, PyTILE offers to [expand the VX4](/Help/Programs/PyTILE.md#expanded-vx4-files).

## Settings
**Export Settings** (`Shift+Ctrl+E`) saves the settings of the selected MegaTile Groups or MegaTiles as an editable text file. Group settings export directly; for MegaTiles a dialog first chooses which flag types to include (**Height**, **Walkability**, **Block Sight**, and **Ramp**). Exporting, editing the text, and re-importing can be an easy way to make bulk changes.
The text format has one block per tile, with named fields. MegaTile blocks contain a 4x4 grid of 0/1 values per flag type (matching the MiniTile layout), for example:

```
# Export of MegaTile 42
MegaTile:
	walkable:
		1111
		1111
		0000
		0000
	ramp:
		0000
		0000
		1111
		0000
```

MegaTile Groups export as a `TileGroup` block with `type`, named `flags`, and `edge`/`piece` values, while doodad groups export as a `DoodadGroup` block with their named `flags` plus the `overlay_id`, `scr`, `string_id`, `dddata_id`, `width`, `height`, and unknown values.
**Import Settings** (`Shift+Ctrl+I`) applies a settings file onto the selected tiles, in order. Group types must match — a `TileGroup` can't be imported onto a doodad group or vice versa. The dialog has two options:

- **Extra Tiles**: What to do when more tiles are selected than the file has entries: **Ignore** leaves the extra tiles unchanged, **Repeat All Settings** loops through the files entries again, and **Repeat Last Setting** applies the final entry to all the extra tiles.
- **Auto-close**: Closes the dialog after a successful import.

The **Copy** and **Paste** buttons in the main window ([group settings](/Help/Programs/PyTILE/Tile_Groups.md#copying-group-settings) and [MegaTile flags](/Help/Programs/PyTILE/MegaTile_Editor.md#copying-megatile-flags)) use this same text format through the clipboard.

## See Also
- [PyTILE](/Help/Programs/PyTILE.md)
- [Tile Palette](/Help/Programs/PyTILE/Tile_Palette.md)
- [Tile Groups](/Help/Programs/PyTILE/Tile_Groups.md)
- [MegaTile Editor](/Help/Programs/PyTILE/MegaTile_Editor.md)
- [Editing a Tileset](/Help/Tutorials/Editing_a_Tileset.md)
