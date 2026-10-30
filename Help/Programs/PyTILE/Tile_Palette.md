# Tile Palette
The Tile Palette browses and manages the tiles of a tileset, and opens for each of the three tile types: MegaTile Groups, MegaTiles, and MiniTiles. From the [PyTILE](/Help/Programs/PyTILE.md) main window, **MegaTile Group Palette** (`Ctrl+P`) opens the palette for the MegaTile Groups. The palettes title shows how many tiles of that type exist and the maximum the file format supports: 4096 MegaTile Groups, 65536 MegaTiles, and 32768 MiniTiles (or over 2 billion with an [expanded VX4](/Help/Programs/PyTILE.md#expanded-vx4-files)).

## Selecting Tiles
Click a tile to select it, `Shift` click to select a range, and `Ctrl` click to add/remove single tiles from the selection. The status bar lists the selected tile IDs. The selection is what the export toolbar actions operate on.

## Palette Toolbar
- **Add** (`Insert`): Adds a new blank MegaTile Group, MegaTile, or MiniTile to the end of the palette. If the tileset has run out of MiniTiles, PyTILE offers to [expand the VX4](/Help/Programs/PyTILE.md#expanded-vx4-files).
- **Select MegaTiles** / **Select MiniTiles** (`Ctrl+M`): Opens another palette containing the smaller tiles used by the current selection — the MegaTiles of the selected groups, or the MiniTiles of the selected MegaTiles. Handy for exporting or editing the tiles making up a group.
- **Edit MegaTiles** / **Edit MiniTiles** (`Return`): Opens the selected MegaTile in the [MegaTile Editor](/Help/Programs/PyTILE/MegaTile_Editor.md), or the selected MiniTile in the [MiniTile Editor](/Help/Programs/PyTILE/MegaTile_Editor.md#minitile-editor).
- **Export Graphics** (`Ctrl+E`) and **Import Graphics** (`Ctrl+I`): Exports the selected tiles graphics to a BMP, or imports graphics from BMPs — see [Importing and Exporting](/Help/Programs/PyTILE/Importing_and_Exporting.md#graphics).
- **Export Settings** (`Shift+Ctrl+E`) and **Import Settings** (`Shift+Ctrl+I`): Exports the selected MegaTile Groups or MegaTiles settings to an editable text file, or imports settings from one — see [Importing and Exporting](/Help/Programs/PyTILE/Importing_and_Exporting.md#settings). Not available for MiniTiles (their only settings are part of the MegaTiles).

## Picking Tiles
The palette also opens as a picker from the find buttons next to tile ID fields (like the MegaTile **ID** in the main window, the MiniTile **ID** in the [MegaTile Editor](/Help/Programs/PyTILE/MegaTile_Editor.md), and the cells of the [Placeability](/Help/Programs/PyTILE/Doodad_Groups.md#placeability) dialog). Double click a tile to choose it and close the palette.

## See Also
- [PyTILE](/Help/Programs/PyTILE.md)
- [MegaTile Editor](/Help/Programs/PyTILE/MegaTile_Editor.md)
- [Importing and Exporting](/Help/Programs/PyTILE/Importing_and_Exporting.md)
- [Tilesets](/Help/Files/Tilesets/Tilesets.md)
