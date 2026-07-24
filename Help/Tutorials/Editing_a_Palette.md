# Editing a Palette
This tutorial walks through recoloring a tileset's terrain with [PyPAL](/Help/Programs/PyPAL.md), by editing the [tileset](/Help/Files/Tilesets/Tilesets.md)'s [.wpe](/Help/Files/Palettes.md#terrain-wpe) palette. The terrain is drawn using the 256 colors of the palette, so changing the colors changes the look of the whole tileset — for example turning the Jungle World's greens into an alien purple.

## Getting the Palette
1. Extract a tileset's `.wpe` from your [MPQs](/Help/Files/MPQ.md) with [PyMPQ](/Help/Programs/PyMPQ.md) — for example the Jungle World palette at `tileset\jungle.wpe`.
2. Open the extracted file in PyPAL with **Open** (`Ctrl+O`).

## Changing the Colors
1. Find the colors you want to change — hovering over a color in the grid shows its index, RGB values, and hex value in the status bar. Related colors tend to sit together in the grid as runs of shades, so recoloring a feature of the terrain usually means changing a whole run the same way.
2. Double click a color to open the color picker, choose its new color, and accept.
3. Repeat for the rest of the colors you want to change. To keep the terrain's shading intact, keep each run of shades going in the same direction — dark shades stay dark, light shades stay light.

## Saving Your Changes
Press **Save** (`Ctrl+S`) to save the palette back to your `.wpe` file. If you started from a palette in a different format, use **Save as StarCraft Terrain `*.wpe`** (`Ctrl+T`) instead — the game expects the terrain palette in the `.wpe` format.

## Using It In the Game
To use the edited palette in the game it needs to be in the MPQ your mod loads, at its original path (for example `tileset\jungle.wpe`). Use [PyMPQ](/Help/Programs/PyMPQ.md) to add the saved file to your mods MPQ — see [Creating a Mod MPQ](/Help/Tutorials/Creating_a_Mod_MPQ.md).

## See Also
- [PyPAL](/Help/Programs/PyPAL.md)
- [PyMPQ](/Help/Programs/PyMPQ.md)
- [Palettes](/Help/Files/Palettes.md)
- [Tilesets](/Help/Files/Tilesets/Tilesets.md)
- [MPQ](/Help/Files/MPQ.md)
- [Creating a Mod MPQ](/Help/Tutorials/Creating_a_Mod_MPQ.md)
