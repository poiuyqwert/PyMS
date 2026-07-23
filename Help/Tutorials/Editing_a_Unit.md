# Editing a Unit
This tutorial walks through editing a unit with [PyDAT](/Help/Programs/PyDAT.md) — from setting up the game files, to changing some unit settings and getting them into your mod. It uses the Marine as the example, but the steps are the same for any entry in any of the [DAT files](/Help/Programs/PyDAT.md).

## Setting Up PyDAT
PyDAT loads the default `.dat` files, entry names, icons, and graphics from the games files in your [MPQs](/Help/Files/MPQ.md), so the first step is to point it at them:

1. Open PyDAT and press **Manage MPQ and TBL files** (`Ctrl+M`). This dialog also opens by itself on startup if any files failed to load.
2. In the **MPQ Settings** tab, add your StarCraft MPQs (for example `StarDat.mpq`, `BrooDat.mpq`, and `patch_rt.mpq` from your StarCraft folder), plus your mods MPQ if you have one.
3. The other tabs choose the [TBL, icon, iscript, and palette files](/Help/Programs/PyDAT.md#data-files) used to display names and previews. The defaults load from the MPQs you just added, so you shouldn't need to change anything.
4. Press **Ok**. Every tab now shows the games default data, ready to edit.

## Finding the Marine
1. Make sure the **Units** tab is selected.
2. Find the Marine in the entry list: type "marine" into the **Find** box and press `Enter`, or type `0` into **ID Jump** and press **Go** (the Marine is unit ID 0).
3. The [Units tab](/Help/Programs/PyDAT/Units.md) fills with the Marines settings, split across six sub-tabs. Hover over any field for an explanation of what it does.

## Making Changes
1. On the **Basic** sub-tab, change **Hit Points** from 40 to 80. Notice the unsaved changes indicator light up in the status bar.
2. The Marines weapon is a reference to another DAT file: next to **Ground** in the Weapons group, press **Jump ->** to open Gauss Rifle on the [Weapons tab](/Help/Programs/PyDAT/Weapons.md).
3. Change the damage **Amount** from 6 to 10. The **Used By** panel at the bottom shows every unit and order using this weapon — handy for checking what else your change affects.
4. Weapons don't store their own upgrade bonus damage — that comes from the **Upgrade** reference. You can follow **Jump ->** again to see U-238 Shells on the [Upgrades tab](/Help/Programs/PyDAT/Upgrades.md).

## Saving Your Changes
Each tab saves its own file, so save both files you changed:

1. On the **Weapons** tab, press **Save** (`Ctrl+S`) and save your `weapons.dat` to a working folder.
2. Switch to the **Units** tab and do the same for `units.dat`.

Alternatively, **Save MPQ** (`Ctrl+Alt+M`) saves any combination of your changed files directly into an MPQ at their correct paths (`arr\units.dat` and `arr\weapons.dat`).

## Using It In the Game
To use the edited files in the game, they need to be in the MPQ your mod loads, at their original `arr\` paths. **Save MPQ** can write them there directly, or use [PyMPQ](/Help/Programs/PyMPQ.md) to add the saved files to your mods MPQ. The next game you play with your mod, Marines will have 80 hit points and stronger rifles.

## See Also
- [PyDAT](/Help/Programs/PyDAT.md)
- [Units Tab](/Help/Programs/PyDAT/Units.md)
- [Weapons Tab](/Help/Programs/PyDAT/Weapons.md)
- [units.dat](/Help/Files/DAT/units.dat.md)
- [MPQ](/Help/Files/MPQ.md)
- [Creating a Mod MPQ](/Help/Tutorials/Creating_a_Mod_MPQ.md)
