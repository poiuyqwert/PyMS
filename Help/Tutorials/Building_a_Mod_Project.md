# Building a Mod Project
This tutorial walks through setting up a mod project in [PyMOD](/Help/Programs/PyMOD.md) and building it into an [MPQ](/Help/Files/MPQ.md) the game can load. Instead of packaging your finished files by hand every time you change something — the approach in the [Creating a Mod MPQ](/Help/Tutorials/Creating_a_Mod_MPQ.md) tutorial — you lay your mod out as editable source files once, and rebuild the whole thing with one button from then on.
The key idea: **folder names decide what gets built**. A folder named `marine.grp` is not a graphic, it is the recipe for one, and the `.bmp` files inside it are the ingredients. PyMOD walks your project, recognizes those folder names, and compiles each one into the game file it is named after.

## Creating the Project
1. Open PyMOD and press **New** (`Ctrl+N`).
2. Choose the folder to create your project in.
3. Enter a name for it, for example `MyMod`, and press **Save**.

You now have an empty `MyMod` folder, and PyMOD is watching it. Everything from here on is done by creating folders and files inside it with your file manager and your usual PyMS tools — PyMOD builds your project, it doesn't edit it.

## Laying Out the MPQ
Anything you want packaged into an MPQ goes inside a folder whose name ends with `.mpq`, and the layout inside that folder becomes the layout inside the archive. The game finds files by their paths, so those paths have to match the originals.

1. Inside `MyMod`, create a folder named `MyMod.mpq`.
2. Inside `MyMod.mpq`, create the folders the game expects: `arr`, `rez`, and `unit/terran`.

If you are not sure where a file you want to override lives, press **Extract** and search for it. Finding `unit\terran\marine.grp` in the list tells you that a `marine.grp` source belongs in a `unit/terran` folder.
Extract can also pull the file straight into your project, pre-filling that folder layout for you — see [Extract](/Help/Programs/PyMOD.md#extract).

## Adding a Text Source
Start with something small — the game's unit names, which live in `stat_txt.tbl`.

1. Open [PyTBL](/Help/Programs/PyTBL.md) and open the game's `stat_txt.tbl`.
2. Inside `MyMod.mpq/rez`, create a folder named `stat_txt.tbl`.
3. Press **Export Strings** (`Ctrl+E`) and save into that folder as `stat_txt.txt` — the name matches the folder, minus the extension.
4. Edit a line in `stat_txt.txt`, for example changing `Terran Marine` to something of your own.

The folder is the source, and the `.txt` inside it is its input. See [TBL Sources](/Help/Programs/PyMOD/TBL_Sources.md) for why a TBL needs every line rather than just the ones you changed.

## Adding a Unit Source
DAT sources work differently, and in a way that is much nicer to live with: they only need the parts you changed.

1. Open [PyDAT](/Help/Programs/PyDAT.md) and make a change to a unit — say the Marine's hit points.
2. Right click the Marine in the entry list and choose **Copy Entry to Clipboard** (`Shift+Ctrl+C`), which copies just that entry in the same text format as **Export to TXT**.
3. Inside `MyMod.mpq/arr`, create a folder named `units.dat`, and paste the clipboard into a new file there called `Marine.txt`.

The file only has to contain the entry and the properties you are changing:

```
Unit(0):
	hit_points.whole 400
```

Everything else comes from the base file, which by default is the unmodified game `units.dat` bundled with PyMS. You can add as many `.txt` files to the folder as you like — one per unit, one per race, however you prefer to organize it. See [DAT Sources](/Help/Programs/PyMOD/DAT_Sources.md).

## Adding a Graphic Source
1. Open [PyGRP](/Help/Programs/PyGRP.md) and open the game's `unit\terran\marine.grp`.
2. Inside `MyMod.mpq/unit/terran`, create a folder named `marine.grp`.
3. Select all the frames (`Ctrl+A`), set the style dropdown to **One BMP per Frame**, and press **Export Selected Frames** (`Ctrl+E`). Save into that folder under the name `frame`, and PyGRP numbers the files `frame 000.bmp`, `frame 001.bmp`, and so on. Frames are ordered by filename, so leave that numbering alone.
4. Edit one of the BMPs in an image editor that preserves indexed color.

See [GRP Sources](/Help/Programs/PyMOD/GRP_Sources.md) for the single-image alternatives to one BMP per frame.

## Compiling
Your project now looks like this:

```
┬ MyMod/
├── .pymod_project.json
└─┬ MyMod.mpq/
  ├─┬ arr/units.dat/
  │ └── Marine.txt
  ├─┬ unit/terran/marine.grp/
  │ ├── frame 000.bmp
  │ ├── frame 001.bmp
  │ └── ...
  └── rez/stat_txt.tbl/stat_txt.txt
```

1. Press **Refresh** on the **Files** tab and check that PyMOD found your three sources. If a source is listed as a plain folder instead, its name doesn't match a source type — check the spelling and the extension.
2. Press **Compile**. PyMOD switches to the **Logs** tab and builds your project.
3. Read the log. Each source reports what it is doing, and the build ends with a green completion message. Orange warnings are worth reading even on a successful build.
4. Find your finished `MyMod.mpq` in the `.build/artifacts` folder inside your project.

If something failed, the log ends in a red error naming the source and the problem. Fix it and compile again — the sources that already succeeded are skipped the second time.

## Rebuilding As You Work
This is where the project pays off. Edit a BMP, or add another `.txt` to your `units.dat` folder, and press **Compile** again. Only what changed is rebuilt; everything else is skipped with a `No changes required` message.
A few things worth knowing:

- Renaming inputs counts as a change, because for a GRP the filenames are the frame order.
- If a compile fails, your previous `MyMod.mpq` is still sitting in `.build/artifacts`, untouched. Artifacts are only replaced once a whole build succeeds.
- **Clean** forces a full rebuild from scratch. You rarely need it, since a normal compile already clears out files it no longer produces.
- Adding files outside of PyMOD won't show up in the **Files** tab until you press **Refresh**, though a compile refreshes it for you anyway.

## Using It In the Game
Load the `MyMod.mpq` from `.build/artifacts` with a mod loader (such as MPQDraft), which inserts it at a higher priority than the game's own MPQs so your files are found first, and can package it into a self-executing [EXE](/Help/Files/EXE.md) to share. Since the artifact is rebuilt in place, you can point your loader at that path once and just recompile as you work.
As your mod grows, add more sources the same way: [AI scripts](/Help/Programs/PyMOD/AI_Script_Sources.md) and [iscripts](/Help/Programs/PyMOD/IScript_Sources.md) in a `scripts` folder, [PCX](/Help/Programs/PyMOD/PCX_Sources.md) menu art, sounds simply copied in as [ordinary files](/Help/Programs/PyMOD/Other_Sources.md). Then commit the project folder to version control and you have a mod anyone can rebuild from source.

## See Also
- [PyMOD](/Help/Programs/PyMOD.md)
- [Building](/Help/Programs/PyMOD/Building.md)
- [MPQ Packages](/Help/Programs/PyMOD/MPQ_Packages.md)
- [Creating a Mod MPQ](/Help/Tutorials/Creating_a_Mod_MPQ.md)
- [Editing a Unit](/Help/Tutorials/Editing_a_Unit.md)
- [Editing a GRP](/Help/Tutorials/Editing_a_GRP.md)
- [Editing Game Text](/Help/Tutorials/Editing_Game_Text.md)
- [MPQ](/Help/Files/MPQ.md)
