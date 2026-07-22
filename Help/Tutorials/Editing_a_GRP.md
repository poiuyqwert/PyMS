# Editing a GRP
This tutorial walks through editing a unit graphic with [PyGRP](/Help/Programs/PyGRP.md) — from extracting the [.grp](/Help/Files/GRP.md) file, to changing its frames and getting it into your mod. The frames are edited as [.bmp](/Help/Files/BMP.md) images, so you will also need an image editor that can work with indexed color `.bmp` files.

## Getting a GRP
1. Extract a GRP from your [MPQs](/Help/Files/MPQ.md) with [PyMPQ](/Help/Programs/PyMPQ.md) — for example the Marine's graphics at `unit\terran\marine.grp`.
2. Open the extracted file in PyGRP with **Open** (`Ctrl+O`).
3. In the **Palette** list, select the palette matching how the game draws the graphic — for unit graphics like the Marine, that is `Units.pal`.
4. Browse the **Frames** list and note the total amount of frames — you will need the count when importing later.

## Exporting the Frames
1. Leave the BMP style dropdown (in the bottom right) on **Single BMP (Framesets)** — the frames will export as one image with 17 frames per row, and must be imported back with the same style.
2. Select every frame with `Ctrl+A`, then press **Export Selected Frames** (`Ctrl+E`) and save the `.bmp` image.
3. Open the image in your image editor. The frames are laid out in a grid, in rows of 17.

## Editing the Image
Change the frames you want, keeping to these rules so the image can be imported back:

1. Do not resize the image, and keep each frame within its own spot in the grid — every frame of a GRP has the same size.
2. Keep the image in indexed color mode, and only use colors from the palette the image exported with.
3. The background color around the frames (normally palette index 0) is transparent in the game, so paint it anywhere you want transparency.
4. On unit graphics, palette indexes 8 to 15 are drawn as the player's color in the game, so use them for anything that should change color per player.

## Importing Your Changes
1. Back in PyGRP, select every frame with `Ctrl+A` and press **Remove Frames** (`Delete`) — imported frames are added to the end of the GRP, so the old frames are removed first.
2. Press **Import Frames** (`Ctrl+I`) and choose your edited `.bmp` (with the BMP style dropdown still on **Single BMP (Framesets)**).
3. Enter the amount of frames from when you [got the GRP](#getting-a-grp), and press **Ok**.
4. Select some frames to check they imported the way you expect, then press **Save As** (`Ctrl+Alt+A`) to save your `.grp`.

## Using It In the Game
To use the edited graphics in the game they need to be in the MPQ your mod loads, at their original path. Use [PyMPQ](/Help/Programs/PyMPQ.md) to add the saved file to your mods MPQ (for example at `unit\terran\marine.grp`).

## See Also
- [PyGRP](/Help/Programs/PyGRP.md)
- [GRP](/Help/Files/GRP.md)
- [BMP](/Help/Files/BMP.md)
- [MPQ](/Help/Files/MPQ.md)
- [Palettes](/Help/Files/Palettes.md)
