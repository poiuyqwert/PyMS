# Editing a Tileset
This tutorial walks through editing a [tileset](/Help/Files/Tilesets/Tilesets.md) with [PyTILE](/Help/Programs/PyTILE.md) — from getting the tileset files out of the game, to changing tile flags and graphics, to using the result in your mod. It uses the Jungle tileset as the example, but the steps are the same for any tileset.

## Getting the Tileset Files
A tileset is made up of [multiple files](/Help/Files/Tilesets/Tilesets.md), which live in the games [MPQs](/Help/Files/MPQ.md) under the `tileset\` folder:

1. Open your StarCraft MPQs with [PyMPQ](/Help/Programs/PyMPQ.md) (the original tilesets like Jungle are in `StarDat.mpq`, and the Brood War tilesets like Desert are in `BrooDat.mpq`).
2. Extract `tileset\jungle.cv5`, `tileset\jungle.vf4`, `tileset\jungle.vx4`, `tileset\jungle.vr4`, and `tileset\jungle.wpe` into a working folder.
3. Extract `tileset\jungle\dddata.bin` into a folder named `jungle` inside that same working folder — PyTILE expects it there.

## Opening the Tileset
1. Open PyTILE and press **Open** (`Ctrl+O`), then choose your extracted `jungle.cv5`. The other files load automatically from beside it.
2. The palette on the left fills with every MegaTile Group in the tileset. Click a group to load its [settings](/Help/Programs/PyTILE/Tile_Groups.md) into the panels on the right, and click one of its 16 MegaTiles to select that tile — the **MegaTile** panel shows it in the embedded [MegaTile Editor](/Help/Programs/PyTILE/MegaTile_Editor.md).

## Changing Tile Flags
Walkability, height, sight blocking, and ramps are controlled per MiniTile, so they are edited in the MegaTile Editor:

1. Select a MegaTile in a grassy group, and switch the MegaTile Editors mode dropdown to **Walkable** (or just press `w`). Each of the 16 MiniTiles gets a green (walkable) or red (unwalkable) border.
2. Click a MiniTile to toggle it, or click and drag to paint several. Right click to apply the same state to all 16 MiniTiles at once. Notice the unsaved changes indicator light up in the status bar.
3. Try the **Height** mode (`h`) too: pick **Low**, **Mid**, or **High** in the dropdown that appears, then paint it onto MiniTiles.
4. To give the whole group the same flags, press **Apply to Megas** and choose to apply the current modes flags (or all flags) to the rest of the groups MegaTiles.

## Changing Graphics
Custom terrain graphics come in and out of PyTILE as BMP images:

1. Press **MegaTile Group Palette** (`Ctrl+P`) to open the [Tile Palette](/Help/Programs/PyTILE/Tile_Palette.md), and select a group or two.
2. Press **Export Graphics** (`Ctrl+E`) and save the BMP. Each group is exported as a 512 pixel wide row of its 16 MegaTiles.
3. Edit the BMP in your image editor. Keep it as a 256 color (8-bit indexed) BMP using the tilesets palette, and keep the same image size.
4. Back in the palette (with the same tiles selected), press **Import Graphics** (`Ctrl+I`), **Add** your edited BMP, check **Replace palette selection**, and press **Import**. The [reuse options](/Help/Programs/PyTILE/Importing_and_Exporting.md#graphics) keep the tileset from filling up with duplicate tiles.

## Saving and Using It In the Game
1. Press **Save** (`Ctrl+S`). All of the tileset files are saved together next to your `.cv5`.
2. To use the edited tileset in the game, add the files to your mods MPQ at their original paths (`tileset\jungle.cv5` and so on, with `dddata.bin` at `tileset\jungle\dddata.bin`) using [PyMPQ](/Help/Programs/PyMPQ.md) — see [Creating a Mod MPQ](/Help/Tutorials/Creating_a_Mod_MPQ.md). Any map using the Jungle tileset will now use your edited tiles.

## See Also
- [PyTILE](/Help/Programs/PyTILE.md)
- [Tile Groups](/Help/Programs/PyTILE/Tile_Groups.md)
- [MegaTile Editor](/Help/Programs/PyTILE/MegaTile_Editor.md)
- [Importing and Exporting](/Help/Programs/PyTILE/Importing_and_Exporting.md)
- [Tilesets](/Help/Files/Tilesets/Tilesets.md)
- [Creating a Mod MPQ](/Help/Tutorials/Creating_a_Mod_MPQ.md)
