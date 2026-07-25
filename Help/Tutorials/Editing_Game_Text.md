# Editing Game Text
This tutorial walks through editing the games text with [PyTBL](/Help/Programs/PyTBL.md) — from setting up the game files, to changing a button tooltip and getting it into your mod. It uses the Train Marine tooltip as the example, but the steps are the same for any string in any [TBL file](/Help/Files/TBL.md).

## Setting Up PyTBL
PyTBL previews strings using the fonts, text colors, and icons from the games files in your [MPQs](/Help/Files/MPQ.md), so the first step is to point it at them:

1. Open PyTBL and press **Manage Settings** (`Ctrl+M`). This dialog also opens by itself on startup if any files failed to load.
2. In the **MPQ Settings** tab, add your StarCraft MPQs (for example `StarDat.mpq`, `BrooDat.mpq`, and `patch_rt.mpq` from your StarCraft folder).
3. The **Preview Settings** tab chooses the font, color, and icon files used by the previewer. The defaults load from the MPQs you just added, so you shouldn't need to change anything.
4. Press **Ok**, then press **Open Default TBL** (`Ctrl+D`) to open the standard `stat_txt.tbl` bundled with PyMS.

## Finding a String
1. Press **Find Strings** (`Ctrl+F`), search for `Train`, and press **Find Next** until the string `m<1>Train <3>M<1>arine<0>` is selected (it is string 585).
2. This is a button tooltip string, so it starts with two special characters: the `m` is the button's hotkey, and the first `<1>` is the [hotkey type](/Help/Files/TBL.md#hotkey-types), which tells the game to show the Marine's mineral, gas, and supply costs in the tooltip.
3. The rest is the label, with [color codes](/Help/Files/TBL.md#color-codes) mixed in: `<3>` colors the `M` yellow to highlight the hotkey, `<1>` switches back to the normal color, and the `<0>` ends the string. The reference panel below the editor lists all of these codes.

## Making Changes
1. In the editor, click right before `arine` and type `ega M` to change the label to `Train <3>M<1>ega Marine`. Your edits apply as you type — the string list updates and the unsaved changes indicator lights up in the status bar.
2. Try recoloring the highlight: change the `<3>` to `<7>` to make the `M` green in-game. You can type special characters directly as their `<N>` escape codes.

## Previewing
1. Press **Test String** (`Ctrl+T`) to see the string rendered with the games fonts and colors.
2. Make sure **Hotkey String** is checked — the previewer reads the hotkey and type characters, and shows the mineral, gas, and supply requirement icons the way the game does. **End at Null** stops the preview at the `<0>` like the game would.

## Saving Your Changes
Press **Save As** (`Ctrl+Alt+A`) and save your `stat_txt.tbl` to a working folder, rather than overwriting the default file bundled with PyMS.

## Using It In the Game
To use the edited file in the game, it needs to be in the MPQ your mod loads, at its original path `rez\stat_txt.tbl`. Use [PyMPQ](/Help/Programs/PyMPQ.md) to add it to your mods MPQ — see the [Creating a Mod MPQ](/Help/Tutorials/Creating_a_Mod_MPQ.md) tutorial. The next game you play with your mod, the Barracks will offer to train Mega Marines.

## See Also
- [PyTBL](/Help/Programs/PyTBL.md)
- [TBL](/Help/Files/TBL.md)
- [MPQ](/Help/Files/MPQ.md)
- [Creating a Mod MPQ](/Help/Tutorials/Creating_a_Mod_MPQ.md)
