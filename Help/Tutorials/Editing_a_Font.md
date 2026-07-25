# Editing a Font
This tutorial walks through editing a font with [PyFNT](/Help/Programs/PyFNT.md) — from setting up the game files, to changing some letters and getting the font into your mod. Since the letters of a [.fnt](/Help/Files/FNT.md) file are edited as an image, you will also need an image editor that can work with indexed color [.bmp](/Help/Files/BMP.md) files.

## Setting Up PyFNT
PyFNT displays and exports letters using the games text palette, loaded from your [MPQs](/Help/Files/MPQ.md), so the first step is to point it at them:

1. Open PyFNT and press **Manage MPQ's and Special Palette** (`Ctrl+M`). This dialog also opens by itself on startup if the palette failed to load.
2. In the **MPQ Settings** tab, add your StarCraft MPQs (for example `StarDat.mpq`, `BrooDat.mpq`, and `patch_rt.mpq` from your StarCraft folder), plus your mods MPQ if you have one.
3. The **Palette Settings** tab chooses the `tfontgam.pcx` special palette. The default loads from the MPQs you just added, so you shouldn't need to change it.
4. Press **Ok**.

## Getting a Font
1. Extract a font from your MPQs with [PyMPQ](/Help/Programs/PyMPQ.md) — the games fonts are in the `font` folder, for example `font\font10.fnt`.
2. Open the extracted file in PyFNT with **Open** (`Ctrl+O`).
3. Browse the **Characters** list to see the letters in the font, and note the ASCII code of the first entry and the total amount of letters — you will need them when importing later.

## Exporting the Font
1. Press **Export Font** (`Ctrl+E`) and save the `.bmp` image.
2. Open the image in your image editor. Every letter is laid out side by side in one row, each taking an equal width.

## Editing the Image
Change the letters you want, keeping to these rules so the image can be imported back:

1. Do not resize the image — the image height is the letter height, and the width determines the width of each letter.
2. Keep each letter within its own equal width column.
3. Keep the image in indexed color mode, and only use colors the exported image already contains — each letter can only use up to 8 colors, and the background color is transparent in the game.

## Importing Your Changes
1. Back in PyFNT, press **Import Font** (`Ctrl+I`) and choose your edited `.bmp`.
2. In the **FNT Specifications** dialog, enter the ASCII code of the lowest character and the amount of letters from when you [got the font](#getting-a-font), and press **Ok**.
3. Select some letters in the **Characters** list to check they imported the way you expect, then press **Save As** (`Ctrl+Alt+A`) to save your `.fnt`.

## Using It In the Game
To use the edited font in the game it needs to be in the MPQ your mod loads, at its original path. Use [PyMPQ](/Help/Programs/PyMPQ.md) to add the saved file to your mods MPQ (for example at `font\font10.fnt`).

## See Also
- [PyFNT](/Help/Programs/PyFNT.md)
- [FNT](/Help/Files/FNT.md)
- [BMP](/Help/Files/BMP.md)
- [MPQ](/Help/Files/MPQ.md)
- [Creating a Mod MPQ](/Help/Tutorials/Creating_a_Mod_MPQ.md)
