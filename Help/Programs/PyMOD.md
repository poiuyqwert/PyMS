# PyMOD
PyMOD is a tool for building complete mod projects. It walks your project folder, detects source types by folder naming conventions, compiles each source into a game file, and can package the results into [.mpq](/Help/Files/MPQ.md) archives ready to load into the game. Builds are incremental: files are hashed so only sources that changed since the last compile are rebuilt. If you are new to PyMOD, start with the [Building a Mod Project](/Help/Tutorials/Building_a_Mod_Project.md) tutorial.
Each kind of source has its own folder convention and settings, described on its own page:

- [MPQ Packages](/Help/Programs/PyMOD/MPQ_Packages.md) ([.mpq](/Help/Files/MPQ.md))
- [DAT Sources](/Help/Programs/PyMOD/DAT_Sources.md) ([units.dat](/Help/Files/DAT/units.dat.md) and the other `.dat` files)
- [GRP Sources](/Help/Programs/PyMOD/GRP_Sources.md) ([.grp](/Help/Files/GRP.md))
- [TBL Sources](/Help/Programs/PyMOD/TBL_Sources.md) ([.tbl](/Help/Files/TBL.md))
- [LO Sources](/Help/Programs/PyMOD/LO_Sources.md) ([.lo?](/Help/Files/LO.md))
- [PCX Sources](/Help/Programs/PyMOD/PCX_Sources.md) ([.pcx](/Help/Files/PCX.md))
- [SPK Sources](/Help/Programs/PyMOD/SPK_Sources.md) ([.spk](/Help/Files/SPK.md))
- [AI Script Sources](/Help/Programs/PyMOD/AI_Script_Sources.md) ([aiscript.bin](/Help/Files/aiscript.bin.md))
- [IScript Sources](/Help/Programs/PyMOD/IScript_Sources.md) ([iscript.bin](/Help/Files/iscript.bin.md))
- [Other Sources](/Help/Programs/PyMOD/Other_Sources.md) (plain folders and copied files)

The [Building](/Help/Programs/PyMOD/Building.md) page describes what a compile actually does, step by step.

## Main Window
PyMOD has no menu bar — everything is on the toolbar and the button row under the tabs. The window has two tabs:

- **Files**: A tree of every source PyMOD found in your project. Folders can be expanded, and each source is shown by the name of the file it produces (an `aiscript.bin` folder is listed as `aiscript.bin/bwscript.bin`, since it can produce both). The **Refresh** button below the tree re-scans the project, which is useful after adding or renaming files outside of PyMOD. The tree is also refreshed automatically whenever you open a project or start a compile.
- **Logs**: The read-only compile log. PyMOD switches to this tab automatically when you compile or clean. Errors, warnings, and the final success message are colored, so you can pick problems out of a long build (the exact colors come from your [theme](/Help/Programs/Themes.md)).

The buttons under the tabs act on the open project:

- **Extract**: Opens the [Extract](#extract) dialog.
- **Compile**: [Builds](#building) the project.
- **Clean**: Deletes the intermediates folder, forcing the next compile to rebuild everything.
- **Cancel**: Stops a running compile.

**Extract**, **Compile**, and **Clean** are only enabled while a project is open and no compile is running; **Cancel** is only enabled while a compile is running. During a compile the toolbar is disabled too, so you can not open or close a project out from under the build.
The status bar shows what PyMOD is doing or the result of the last action, and the title bar shows the path of the open project.

## Managing Projects
Only one project is open at a time, and opening a project closes the previous one.

- **New** (`Ctrl+N`): Creates a new project. First choose the folder to create it in, then enter a name in the **Project Name** dialog. The name can not be empty and can not contain a path separator, and PyMOD will not overwrite an existing folder.
- **Open** (`Ctrl+O`): Opens an existing project folder. If the folder is not a PyMOD project yet, PyMOD asks whether to initialize it as one — answering yes just adds the marker file, leaving everything already in the folder alone, so you can turn a folder of files you already have into a project.
- **Close** (`Ctrl+W`): Closes the open project. Nothing is deleted; PyMOD has no unsaved state of its own, since your sources are ordinary files you edit with other tools.
- **Manage Settings** (`Ctrl+M`): Opens the [settings](#settings) dialog.
- **Help** (`F1`): Opens this help.
- **About PyMOD**: Shows the version and credits.
- **Exit**: Closes PyMOD. If a compile is running you are asked whether to cancel it and exit.

## Projects
A project is just a folder containing your mod's sources, marked as a PyMOD project by a hidden `.pymod_project.json` file. Use `New` to create a project (the marker is created for you), or `Open` on an existing folder (you will be offered to initialize it as a project if it isn't one yet).

The layout of the folder determines what gets built. Everything you want packaged into an MPQ goes inside a folder whose name ends with `.mpq`:

```
┬ MyMod/
├── .pymod_project.json
└─┬ MyMod.mpq/
  ├── config.json
  ├─┬ arr/units.dat/
  │ ├── config.json
  │ ├── units.dat
  │ ├── Race1.txt
  │ └── Race2.txt
  ├─┬ rez/stat_txt.tbl/
  │ └── stat_txt.txt
  ├─┬ scripts/aiscript.bin/
  │ ├── unitdef.txt
  │ ├── Ter3.txt
  │ ├── PB1A.txt
  │ └── ...
  ├─┬ unit/terran/marine.grp/
  │ ├── frame 000.bmp
  │ ├── frame 001.bmp
  │ └── ...
  ├─┬ unit/protoss/dragoon.grp/
  │ ├── config.json
  │ └── frames.bmp
  └── sound/zerg/advisor/zadupd00.wav
```

Folder chains are collapsed in that diagram to keep it narrow, so `arr/units.dat/` means a `units.dat` folder inside an `arr` folder. The last entry is an ordinary file that is simply copied into the archive at that path.
An MPQ is not required, though. Sources outside of any `*.mpq` folder are compiled all the same, and their compiled files are published as loose files in `.build/artifacts/`, mirroring your project layout — so you can simply compile your game files and do whatever you want with them (load them with a launcher that supports loose files, package them yourself, copy them into another project, etc.).
Everything PyMOD generates lives in a `.build` folder inside your project, which you never need to edit by hand:

- `.build/intermediates/`: Every compiled game file, in a copy of your project's folder layout. This is where the incremental build keeps its work between compiles.
- `.build/artifacts/`: The finished output of your last successful compile — the packaged `.mpq` archives, plus every compiled file that is not inside an MPQ folder.
- `.build/staging/`: Where artifacts are assembled during a compile, before being published.
- `.build/artifacts.old`: Your previous artifacts, held onto briefly while the new ones are published so they can be restored if that fails.
- `.build/meta.json`: The hashes that make builds incremental.

## Source types
Source types are detected by **folder** name, not by file name. A folder named `marine.grp` is a GRP source, and the `.bmp` files inside it are its input frames; a folder named `units.dat` is a DAT source, and the `.txt` files inside it are the entries to import. This is why a source's own name ends in the extension of the file it produces.
Folders are matched against every source type and the best match wins, falling back to a plain folder when nothing matches. See the pages listed at the [top of this page](#pymod) for each type's conventions.
A few rules apply to the whole project:

- Source folders that produce a file own everything inside them. PyMOD does not look for further sources inside a `marine.grp` or `aiscript.bin` folder, so you can put whatever supporting files you like in there.
- Folders and files whose names start with `.` are ignored entirely, which is how `.pymod_project.json` and `.build` stay out of your mod.
- `config.json` and `*.config.json` files are configuration, so they are never treated as sources or copied into your mod. Changing one still triggers a rebuild of the source it configures.
- Folders and files are always processed in sorted order, so the order of your compiled output does not depend on the order your filesystem happens to list things in.

Sources are configured with a `config.json` file inside their folder. Every setting has a default, so a `config.json` is only needed when you want to change something, and it only needs to contain the settings you are changing. A `config.json` that can not be read fails the build rather than quietly falling back to the defaults.

## Building
**Compile** builds the project. Sources are compiled into `.build/intermediates/`, and the finished artifacts are written to `.build/artifacts/`. Artifacts are assembled in a staging folder and only replace the previous artifacts once the whole build succeeds, so a failed compile never leaves you without your last good build.
Hashes of every input and output are stored in `.build/meta.json`, so a source whose inputs have not changed is skipped with a `No changes required` message on the next compile. Adding, removing, or renaming an input counts as a change, as does editing the source's `config.json`.
Progress is written to the **Logs** tab as the build runs, ending in either a green completion message or a red error. The first error stops the build. **Cancel** aborts a running compile at the next step boundary; both an abort and an error keep the hash bookkeeping from the steps that already finished, so a later compile can pick up where it left off.
**Clean** deletes `.build/intermediates`, which forces the next compile to rebuild every source from scratch. It leaves `.build/artifacts` and `.build/meta.json` alone, so your last build's output is still there. You rarely need it — a normal compile already removes intermediates it no longer uses.
See [Building](/Help/Programs/PyMOD/Building.md) for the full pipeline, including the order steps run in and how the artifact swap works.

## Extract
**Extract** opens a browser for the files in the MPQs configured in the [settings](#settings), together with the game files bundled with PyMS. Use it to find the path of a file you want to override in your mod — for example to learn that the marine's graphics live at `unit\terran\marine.grp`, which is the folder layout your source would need.
Type in the box below the list to filter it. **Wildcard** matches with `?` and `*`, and **Regex** matches with a regular expression (the box turns red while an incomplete or invalid expression is typed). **Done** closes the dialog.
**Extract** pulls the selected file into your project. Which options you get depends on the file — a file PyMOD knows how to turn into an editable source offers the settings for that, and anything else is copied out as it is — but every file offers the same two sections:

- **Destination**: The folder in your project to extract into and the path inside it. **Folder** lists the [MPQ folders](/Help/Programs/PyMOD/MPQ_Packages.md) in your project, plus the project root as a fallback, and **Path** is pre-filled from the path inside the archive, so `unit\terran\marine.grp` becomes `unit/terran/marine.grp` — the layout the packager turns back into that same archive path. Both are editable, and the full path is shown underneath. You are asked before an existing file is overwritten.
- **MPQ Config**: The [compression](/Help/Programs/PyMOD/MPQ_Packages.md#compression) the file is packaged with. Leave **Override compression** off and the file uses the containing MPQ's `autocompression` settings; turn it on and the type and level you choose are written to the source's `config.json` for you.

The **Files** tab refreshes when you close the dialog, so anything you extracted is there. To pull files out of an MPQ without a project, use [PyMPQ](/Help/Programs/PyMPQ.md).

## Settings
**Manage Settings** (`Ctrl+M`) opens the settings dialog:

- **MPQ Settings**: Manages the list of MPQs used by the [Extract](#extract) dialog. Files are read from the highest priority MPQ that contains them, and the higher an MPQ is in the list the higher its priority.
- **Theme**: Changes the PyMS window [theme](/Help/Programs/Themes.md). The theme also sets the colors of the compile log.

There are no settings for how your project is built — that is all configured per source with `config.json` files inside the project itself, so a project builds the same way for everyone who has it.

## Command line
Running PyMOD with a project path compiles it without opening the GUI, printing the build log to the console:

```
PyMOD [options] <project_path>
```

The path must already be a PyMOD project; the command line will not initialize one for you. The exit code is `0` if the compile succeeded and `1` if it failed, so PyMOD can be used as a build step in a script.

- `--gui`: Opens a project with the GUI instead of compiling it.

## See Also
- [MPQ Packages](/Help/Programs/PyMOD/MPQ_Packages.md)
- [DAT Sources](/Help/Programs/PyMOD/DAT_Sources.md)
- [GRP Sources](/Help/Programs/PyMOD/GRP_Sources.md)
- [TBL Sources](/Help/Programs/PyMOD/TBL_Sources.md)
- [LO Sources](/Help/Programs/PyMOD/LO_Sources.md)
- [PCX Sources](/Help/Programs/PyMOD/PCX_Sources.md)
- [SPK Sources](/Help/Programs/PyMOD/SPK_Sources.md)
- [AI Script Sources](/Help/Programs/PyMOD/AI_Script_Sources.md)
- [IScript Sources](/Help/Programs/PyMOD/IScript_Sources.md)
- [Other Sources](/Help/Programs/PyMOD/Other_Sources.md)
- [Building](/Help/Programs/PyMOD/Building.md)
- [Building a Mod Project](/Help/Tutorials/Building_a_Mod_Project.md)
- [MPQ](/Help/Files/MPQ.md)
- [PyMPQ](/Help/Programs/PyMPQ.md)
- [Themes](/Help/Programs/Themes.md)
