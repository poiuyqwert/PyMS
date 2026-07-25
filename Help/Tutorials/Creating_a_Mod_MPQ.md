# Creating a Mod MPQ
This tutorial walks through packaging the files of a mod into an [MPQ](/Help/Files/MPQ.md) with [PyMPQ](/Help/Programs/PyMPQ.md), so the game will load them. It assumes you have some edited files ready to go — for example a `units.dat` from the [Editing a Unit](/Help/Tutorials/Editing_a_Unit.md) tutorial, or a `marine.grp` from the [Editing a GRP](/Help/Tutorials/Editing_a_GRP.md) tutorial.
The key idea: the game finds files by their paths inside the MPQs, so every file in your MPQ must be at the same path as the original file it replaces (for example `arr\units.dat` or `unit\terran\marine.grp`).

## Creating the Archive
1. Open PyMPQ and press **New** (`Ctrl+N`).
2. Choose where to save the archive and name it after your mod, for example `mymod.mpq`. The new empty archive opens immediately, ready for files to be added.

## Adding Your Files
1. Press **Add Files** (`Ctrl+I`) and pick your edited file — for example your `units.dat`.
2. In the folder prompt, type the folder part of the path the game expects, ending with a `\` — for `units.dat` that is `arr\`, so the file is added as `arr\units.dat`.
3. Repeat for your other files with their own paths — for example `marine.grp` is added with the prefix `unit\terran\`. If you are not sure of a path, open one of the games own MPQs in PyMPQ and find the original file to see where it lives.
4. Check the file list to confirm every file ended up at the right path. If a path is wrong, **Rename** (`Ctrl+R`) lets you fix it in place.

If you keep your mods files in folders matching their MPQ paths (an `arr` folder, a `unit\terran` folder, and so on), you can instead add everything in one step with **Add Directory** (`Ctrl+D`) — the folder structure becomes the file paths, and you can leave the prefix prompt empty.

## Choosing Compression
The default **Auto-Select** [compression](/Help/Programs/PyMPQ.md#compression-and-encryption) is a good choice for mods: regular files get Standard compression, `.wav` sounds get Audio compression, and already compressed files like `.smk` videos are stored as-is. You can simply leave it alone. If you want a specific file stored differently (for example a sound at a higher quality), pick a compression from the **Manage Settings** menu before adding that file, and switch back after.

## Updating Files Later
As you keep working on your mod, you can update the archive without re-doing the steps above:

1. Open your MPQ in PyMPQ and double click a file to open it in its editor — for example a `.dat` file in PyDAT. When you save, PyMPQ offers to update the archive with the changed file automatically.
2. To replace a file with a new version from disk, just add it again at the same path — the old version is replaced.
3. After a lot of replacing and deleting, press **Compact Archive** (`Ctrl+P`) to shrink the archive back down.

## Using It In the Game
The game loads its MPQs in a defined order, and a mod works by inserting its MPQ at a higher priority than the default MPQs, so the modded files are found first (see [MPQ](/Help/Files/MPQ.md)). To do this, load your `mymod.mpq` with a mod loader (such as MPQDraft), which can also package the MPQ into a self-executing [EXE](/Help/Files/EXE.md) to share your mod.

## See Also
- [PyMPQ](/Help/Programs/PyMPQ.md)
- [MPQ](/Help/Files/MPQ.md)
- [Editing a Unit](/Help/Tutorials/Editing_a_Unit.md)
- [Editing a GRP](/Help/Tutorials/Editing_a_GRP.md)
- [Creating a Game Template](/Help/Tutorials/Creating_a_Game_Template.md)
