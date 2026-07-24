# Tile Groups
A MegaTile Group is an entry in the [.cv5](/Help/Files/Tilesets/CV5.md) file, containing 16 MegaTile slots along with the settings controlling how those tiles behave in the game. Selecting a group in the [PyTILE](/Help/Programs/PyTILE.md) main window palette loads its settings into the panels on the right side of the window. This page covers normal terrain groups — groups with **Type** 1 are doodad groups and get a different set of panels, covered by [Doodad Groups](/Help/Programs/PyTILE/Doodad_Groups.md).

## Flags
The flag panels edit the groups behavior flags:

- **Walkability**: **Walkable** and **Unwalkable**.
- **Buildability**: **Unbuildable** (no buildings can be built), **Occupied** (unbuildable until a building on this tile gets removed), and **Special** (allows Beacons and Start Locations to be placed).
- **Creep**: **Creep** (Zerg can build here when this flag is combined with the Temporary creep flag), **Receding** (receding creep), and **Temporary** (Zerg can build here when this flag is combined with the Creep flag).
- **Height**: **Mid Ground** and **High Ground** (High Ground has priority over Mid Ground).
- **Misc.**: **Has Doodad Cover** (provides cover for hit calculations), **Blocks View**, and **Cliff Edge**.
- **Unknown**: The unknown/unused flags **0002**, **0008**, and **0020**.

Flags marked with a `*` in the UI (**Walkable**, **Unwalkable**, **Mid Ground**, **High Ground**, **Blocks View**, and **Cliff Edge**) get overwritten by StarCraft based on the per-MiniTile flags of the groups MegaTiles, so to control those behaviors edit the MiniTile flags in the [MegaTile Editor](/Help/Programs/PyTILE/MegaTile_Editor.md) instead.

## Edge Types
The **Left**, **Up**, **Right**, and **Down** values define what tile types can be next to tiles in this group in each direction. It is unsure if StarEdit actually uses these, or if they are just reference/outdated values.

## Piece Types
The **Left**, **Up**, **Right**, and **Down** values pair edges with terrain pieces: a value of 0 can match any appropriate tile, otherwise the edge only pairs with a matching Terrain Piece Type value and tile index. As with Edge Types, it is unsure if StarEdit actually uses these.

## Group Type
The **Group** panel shows the groups **Type**: 0 for unused/unplaceable groups, 1 for doodads, and 2+ for basic terrain and edges. The **Doodad** checkbox indicates whether the group is a [Doodad Group](/Help/Programs/PyTILE/Doodad_Groups.md).

## MegaTiles
The **MegaTile** panel manages the currently selected MegaTile slot of the group. The **ID** entry sets which MegaTile fills the slot (with a find button to pick one visually from the [Tile Palette](/Help/Programs/PyTILE/Tile_Palette.md)), and below it is the embedded [MegaTile Editor](/Help/Programs/PyTILE/MegaTile_Editor.md) for editing the MegaTiles MiniTiles and flags, along with the **Apply to Megas** button to copy the MegaTiles flags to the rest of the group.

## Copying Group Settings
The **Copy Group Settings** panel copies settings between groups through the clipboard. Check the categories you want (**Walkability**, **Buildability**, **Creep**, **Height**, **Misc.**, **Unknown**, **Edge Types**, **Piece Types**, and **Group Type**), then press **Copy** (`Ctrl+Alt+C`) to copy those settings of the selected group, and **Paste** (`Ctrl+Alt+V`) to apply copied settings onto another selected group. The clipboard contents are plain text in the same format as [exported settings](/Help/Programs/PyTILE/Importing_and_Exporting.md#settings), so you can also edit the text before pasting, or paste between PyTILE windows.

## See Also
- [PyTILE](/Help/Programs/PyTILE.md)
- [Doodad Groups](/Help/Programs/PyTILE/Doodad_Groups.md)
- [MegaTile Editor](/Help/Programs/PyTILE/MegaTile_Editor.md)
- [Importing and Exporting](/Help/Programs/PyTILE/Importing_and_Exporting.md)
- [.cv5](/Help/Files/Tilesets/CV5.md)
