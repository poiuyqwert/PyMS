# Editing a Parallax
This tutorial walks through editing the star background with [PySPK](/Help/Programs/PySPK.md) — from setting up the game files, to extracting and changing the games parallax and getting it into your mod. The star background is a parallax [.spk](/Help/Files/SPK.md) file, and is only displayed on the Space Platform [tileset](/Help/Files/Tilesets/Tilesets.md).

## Setting Up PySPK
PySPK loads the palette used to display the stars from the games files in your [MPQs](/Help/Files/MPQ.md), so the first step is to point it at them:

1. Open PySPK and press **Manage Settings** (`Ctrl+M`). This dialog also opens by itself on startup if the palette failed to load.
2. In the **MPQ Settings** tab, add your StarCraft MPQs (for example `StarDat.mpq`, `BrooDat.mpq`, and `patch_rt.mpq` from your StarCraft folder).
3. The **Preview Settings** tab chooses the `platform.wpe` [palette](/Help/Files/Palettes.md). The default loads it from the MPQs you just added, so you shouldn't need to change anything.
4. Press **Ok**.

## Getting the Parallax
The games star background is the file `parallax\star.spk` inside `StarDat.mpq`. To start from it rather than from scratch:

1. Open `StarDat.mpq` with [PyMPQ](/Help/Programs/PyMPQ.md) (open a copy if you are worried about accidental changes).
2. Type `*.spk` into the **Filter** box and press `Enter` to find it quickly.
3. Select `parallax\star.spk` and press **Extract Files** (`Ctrl+E`) to extract it to a working folder.

## Editing the Stars
1. In PySPK, press **Open** (`Ctrl+O`) and open the extracted `star.spk`. The [Layers](/Help/Programs/PySPK/Layers.md) panel fills with its 5 layers, and the canvas shows one 648x488 tile of the star field.
2. Click a row in the Layers panel to pick the layer to work on — Layer 1 scrolls the slowest (the deepest stars), Layer 5 the fastest (the closest). With **Auto-lock** on (the default) the other layers are locked, so you can not accidentally change them.
3. Choose the **Draw** tool (`P`), pick a star image on the [Palette tab](/Help/Programs/PySPK/Palette_Tab.md), and click on the canvas to place some stars.
4. To make your own star, create a small 8-bit [.bmp](/Help/Files/BMP.md) (black background, star drawn in colors from `platform.wpe`), press **Import Star** on the Palette tab, and place it like any other image.
5. To adjust existing stars, switch to the **Select** tool (`M`) and click a star or drag a box around several — the [Stars tab](/Help/Programs/PySPK/Stars_Tab.md) shows and selects them by position too. Drag them with the **Move** tool (`V`) or nudge them with the arrow keys, or press `Delete` to remove them.

## Previewing the Parallax
1. Press **Preview** (`Ctrl+L`) to open the Parallax Preview, which repeats and scrolls the layers just like the game.
2. Scroll around with the arrow keys or the mouse wheel (hold `Shift` to scroll horizontally with the wheel) and watch the layers drift at their different speeds to check the depth effect.

## Using It In the Game
1. Press **Save** (`Ctrl+S`) to save your `star.spk`.
2. Use [PyMPQ](/Help/Programs/PyMPQ.md) to add it to your mods MPQ at its original path — when adding, enter `parallax\` in the folder prompt so the file is stored as `parallax\star.spk`. See the [Creating a Mod MPQ](/Help/Tutorials/Creating_a_Mod_MPQ.md) tutorial for packaging a mod.
3. Play a game on a Space Platform map with your mod, and enjoy your new night sky.

## See Also
- [PySPK](/Help/Programs/PySPK.md)
- [SPK](/Help/Files/SPK.md)
- [PyMPQ](/Help/Programs/PyMPQ.md)
- [Creating a Mod MPQ](/Help/Tutorials/Creating_a_Mod_MPQ.md)
