# Doodad Groups
Doodads are decorations (trees, rocks, ruins, etc.) that map makers can place on top of the terrain. A doodad group is a MegaTile Group with **Type** 1 — when one is selected in the [PyTILE](/Help/Programs/PyTILE.md) main window, the settings panels switch to the doodad layout described on this page (see [Tile Groups](/Help/Programs/PyTILE/Tile_Groups.md) for the normal layout). A whole doodad is a grid of MegaTiles: each row of the doodad is one MegaTile Group, and all of its groups are contiguous in the tileset and share the same Doodad ID.

## Doodad
- **ID**: The Doodad ID. Each doodad must have a unique ID, and all MegaTile Groups in the doodad must have the same ID. It is also the index into the [dddata.bin](/Help/Files/Tilesets/dddata.bin.md) [placeability](#placeability) data.
- **Width** and **Height**: The total size of the doodad in MegaTiles.

## Overlay
A doodad can have a sprite or unit overlay placed on top of it:

- **ID**: The overlay ID, referencing either `sprites.dat` or `units.dat` depending on the selected flag.
- **None**, **Sprites.dat**, or **Units.dat**: What the overlay ID references.
- **Flipped**: The overlay is flipped (unused by the game).

The overlay flags share bits with some creep/misc flags of normal groups: **Sprites.dat** overlaps with the Receding creep flag, **Flipped** overlaps with the Temporary creep flag, and **Units.dat** overlaps with the Cliff Edge flag. Those overlapping flags are shown as non-editable in the doodad panels.

## Behavior Flags
The **Walkability**, **Buildability**, **Creep**, **Height**, and **Misc.** panels are the same as for [Tile Groups](/Help/Programs/PyTILE/Tile_Groups.md#flags), except **Receding**, **Temporary**, and **Cliff Edge** are not editable since their bits are used by the [Overlay](#overlay) flags. The **Unknown** panel additionally has the **Unknown 4** and **Unknown 8** entries, which are unknown/unused values (used as Edge/Piece Type values by normal groups).

## SC:R
The **SC:R** checkbox marks doodads that were added in StarCraft: Remastered, with a **Raw** entry to edit the underlying value directly (1 = added in SC:R).

## Name
The name of the doodad shown to map makers. The **String** dropdown picks a string from `stat_txt.tbl` (choose which TBL file to load with **Manage Settings** `Ctrl+M`), and the **Raw** entry edits the string ID directly.

## Placeability
The **Placeability** button opens the Doodad Placeability dialog, which edits which MegaTile Groups the doodad must be placed on ([dddata.bin](/Help/Files/Tilesets/dddata.bin.md)). The dialog shows the doodads full grid of MegaTiles, with an entry under each tile for the required MegaTile Group ID at that position (0 = no requirement). Double click a tile to pick the group visually from the [Tile Palette](/Help/Programs/PyTILE/Tile_Palette.md). Press **Ok** to apply the changes.

## Apply All
The **Apply All** button applies the selected groups settings to all the other MegaTile Groups with the same Doodad ID, so you can set up one row of the doodad and copy the settings to the rest.

## Copying Doodad Settings
The **Copy Group Settings** panel works the same as for [Tile Groups](/Help/Programs/PyTILE/Tile_Groups.md#copying-group-settings), with doodad categories: **Doodad**, **Overlay**, **Walkability**, **Buildability**, **Creep**, **Height**, **Misc.**, **Unknown**, **SC:R**, and **Name**. Press **Copy** (`Ctrl+Alt+C`) to copy the checked settings to the clipboard as text, and **Paste** (`Ctrl+Alt+V`) to apply copied settings onto the selected group.

## See Also
- [PyTILE](/Help/Programs/PyTILE.md)
- [Tile Groups](/Help/Programs/PyTILE/Tile_Groups.md)
- [Importing and Exporting](/Help/Programs/PyTILE/Importing_and_Exporting.md)
- [dddata.bin](/Help/Files/Tilesets/dddata.bin.md)
- [.cv5](/Help/Files/Tilesets/CV5.md)
