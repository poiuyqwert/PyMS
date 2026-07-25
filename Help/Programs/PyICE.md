# PyICE
PyICE is a tool used for editing animation scripts (IScripts), contained in [iscript.bin](/Help/Files/iscript.bin.md). PyICE decompiles the `.bin` file into text source code, and compiles the text source code back into the `.bin` file.
The source code is written in the [IScript Language](/Help/Programs/PyICE/IScript_Language.md), and edited using the built in [IScript Editor](/Help/Programs/PyICE/Code_Editor.md). If you are new to IScript editing, start with the [Editing an IScript](/Help/Tutorials/Editing_an_IScript.md) tutorial.

## Main Window
The main window is used to select which IScript entries to edit or export. It shows five lists:

- **IScript Entries**: Every IScript entry in the loaded file, shown as its ID and name.
- **Images**: Every [images.dat](/Help/Files/DAT/images.dat.md) entry, which each reference an IScript entry directly.
- **Sprites**: Every [sprites.dat](/Help/Files/DAT/sprites.dat.md) entry, which each reference an Image.
- **Flingy's**: Every [flingy.dat](/Help/Files/DAT/flingy.dat.md) entry, which each reference a Sprite.
- **Units**: Every [units.dat](/Help/Files/DAT/units.dat.md) entry, which each reference a Flingy.

Selecting an entry in any list selects an IScript entry — the Images, Sprites, Flingy's, and Units lists resolve through their references down to the IScript entry of the resulting Image (each entry shows the resolved IScript ID in square brackets). This lets you find an IScript by the unit/flingy/sprite/image that uses it, without knowing its ID.
Multiple entries can be selected in each list, in any combination of lists. Each list has an **Unselect All** button, `Ctrl+A` selects all IScript entries, and the status bar shows the combined list of selected IScript IDs.

## Managing Files
- **New** (`Ctrl+N`): Creates a new, empty `iscript.bin`.
- **Open** (`Ctrl+O`): Opens an existing `iscript.bin`.
- **Open Default Scripts** (`Ctrl+D`): Opens the default StarCraft `iscript.bin` bundled with PyMS.
- **Save** (`Ctrl+S`) and **Save As...** (`Ctrl+Alt+A`): Saves the `iscript.bin`.
- **Close** (`Ctrl+W`): Closes the loaded file.
- **Set as default .bin editor** (Windows Only): Associates `.bin` files with PyICE, so they open in PyICE when double clicked.

`iscript.bin` has a maximum file size of 65535 bytes. PyICE checks the size when compiling changes, and will show an error instead of letting the file grow past the limit.

## Data Files
PyICE uses some of the games data files to display entry names in the lists, to add helpful name comments to decompiled code, to validate the IDs used in your code, and to power the [Previewers](/Help/Programs/PyICE/Previewers.md):

- [stat_txt.tbl](/Help/Files/TBL.md) and `unitnames.tbl`: Unit names.
- `images.tbl`: The [GRP](/Help/Files/GRP.md) file paths of images.
- `sfxdata.tbl`: The sound file paths.
- [units.dat](/Help/Files/DAT/units.dat.md), [flingy.dat](/Help/Files/DAT/flingy.dat.md), [sprites.dat](/Help/Files/DAT/sprites.dat.md), and [images.dat](/Help/Files/DAT/images.dat.md): The entries of the Main Window lists and their references down to IScript entries.
- [weapons.dat](/Help/Files/DAT/weapons.dat.md): Weapon names, for commands like `useweapon`.
- [sfxdata.dat](/Help/Files/DAT/sfxdata.dat.md): Sound names, for commands like `playsnd`.

**Manage TBL and DAT files** (`Ctrl+M`) opens the settings dialog where you can choose these files (from disk or from your [MPQs](/Help/Files/MPQ.md)), manage the MPQs to load files from, choose the [palettes](/Help/Files/Palettes.md) used by the graphics previewer, and change the [theme](/Help/Programs/Themes.md). The settings dialog also opens automatically at startup if any of the files fail to load.

## Editing Entries
**Edit IScript entries** (`Ctrl+E`) opens the [IScript Editor](/Help/Programs/PyICE/Code_Editor.md) with the selected entries decompiled into it (or empty if no entries are selected, for writing new entries from scratch). Saving in the editor compiles the code back into the loaded file — entries with the same ID as an existing entry replace the existing entry.

## Finding Entries
**Find Entries** (`Ctrl+F`) searches all five lists by name. The search can be matched Case Sensitive and/or as a Regular Expression (otherwise it is matched as a substring), and **Include ID's in Search** also matches against the ID numbers in the lists. The results are grouped by list; selecting results and pressing **Select** (or **Add Selection**, to keep the existing selection) selects those entries in the main window.

## Exporting and Importing
- **Export Entries** (`Ctrl+Alt+E`): Decompiles the selected entries to a text file.
- **Import Entries** (`Ctrl+Alt+I`): Compiles one or more text files into the loaded file. Imported entries with the same ID as an existing entry will replace the existing entry.
- **Import a List of Files** (`Ctrl+L`): Manages a list of text files to import from. You can import individual files from the list, or all of them at once.

## Command Line
PyICE can also be used from the command line to decompile and compile scripts without opening the GUI:

```
PyICE [options] <inp|iscriptin> [out|iscriptout]
```

- `-d`, `--decompile`: Decompile IScript entries from an `iscript.bin` (the default).
- `-c`, `--compile`: Compile IScript entries to an `iscript.bin`.
- `-a`, `--weapons`: Specify your own `weapons.dat` file for weapon data lookups.
- `-l`, `--flingy`: Specify your own `flingy.dat` file for flingy data lookups.
- `-i`, `--images`: Specify your own `images.dat` file for image data lookups.
- `-p`, `--sprites`: Specify your own `sprites.dat` file for sprite data lookups.
- `-f`, `--sfxdata`: Specify your own `sfxdata.dat` file for sound data lookups.
- `-x`, `--stattxt`: Specify the `stat_txt.tbl` file to use.
- `-m`, `--imagestbl`: Specify the `images.tbl` file to use.
- `-t`, `--sfxdatatbl`: Specify the `sfxdata.tbl` file to use.
- `-s`, `--scripts`: A list of IScript ID's to decompile, separated by commas (default: all).
- `-b`, `--iscript`: The base `iscript.bin` file to compile on top of.
- `-w`, `--hidewarns`: Hides any warnings produced by compiling your code.
- `--gui`: Opens a file with the GUI.

## See Also
- [IScript Editor](/Help/Programs/PyICE/Code_Editor.md)
- [IScript Language](/Help/Programs/PyICE/IScript_Language.md)
- [Command Reference](/Help/Programs/PyICE/Command_Reference.md)
- [Code Generator](/Help/Programs/PyICE/Code_Generator.md)
- [Previewers](/Help/Programs/PyICE/Previewers.md)
- [Editing an IScript](/Help/Tutorials/Editing_an_IScript.md)
