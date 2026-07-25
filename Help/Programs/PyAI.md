# PyAI
PyAI is a tool used for editing AI scripts, contained in [aiscript.bin](/Help/Files/aiscript.bin.md) and [bwscript.bin](/Help/Files/aiscript.bin.md#bwscriptbin). PyAI decompiles the `.bin` files into text source code, and compiles the text source code back into the `.bin` files.
The source code is written in the [AI Language](/Help/Programs/PyAI/AI_Language.md), and edited using the built in [Code Editor](/Help/Programs/PyAI/Code_Editor.md). If you are new to AI scripting, start with the [AI Basics](/Help/Tutorials/AI_Basics.md) and [Creating Your First AI Script](/Help/Tutorials/Creating_Your_First_AI_Script.md) tutorials.

## Main Window
The main window shows the list of AI scripts in the loaded files. Each script in the list shows:

- The scripts 4 character AI ID
- A `BW` marker if the script is stored in `bwscript.bin`
- The scripts three [flags](#script-flags) in binary form
- The scripts name, which is its string from `stat_txt.tbl` (or `String N` if the string could not be looked up)

Hovering over a script shows a tooltip with its full details. Double clicking a script opens it in the [Code Editor](/Help/Programs/PyAI/Code_Editor.md), and right clicking opens a menu with the common editing actions.
The View menu (or the sort buttons on the toolbar) controls the order the scripts are listed in: File Order, Sort by ID, Sort by BroodWar, Sort by Flags, or Sort by Strings.
The status bar shows the general status, an indicator for unsaved changes, the script count and file size of each `.bin` file, and the [plugins](#plugins) required by the loaded files (if any).
Changes to the script list (adding, removing, and editing scripts) can be undone with `Ctrl+Z` and redone with `Ctrl+Y`.

## Managing Files
- **New** (`Ctrl+N`): Creates a new, empty `aiscript.bin` and `bwscript.bin`.
- **Open** (`Ctrl+O`): Opens an existing `aiscript.bin`, then asks for the matching `bwscript.bin` (press Cancel to open only the `aiscript.bin`).
- **Open Default Scripts** (`Ctrl+D`): Opens the default StarCraft scripts bundled with PyMS.
- **Open MPQ** (`Ctrl+Alt+O`): Opens `scripts\aiscript.bin` and `scripts\bwscript.bin` directly out of an [MPQ](/Help/Files/MPQ.md).
- **Save** (`Ctrl+S`) and **Save As...** (`Ctrl+Alt+A`): Saves the `aiscript.bin`, and asks where to save the `bwscript.bin` if any scripts are stored in it.
- **Save MPQ** (`Ctrl+Alt+M`): Saves both files into an MPQ as `scripts\aiscript.bin` and `scripts\bwscript.bin`.
- **Close** (`Ctrl+W`): Closes the loaded files.
- **Set as default .bin editor** (Windows Only): Associates `.bin` files with PyAI, so they open in PyAI when double clicked.

`aiscript.bin` has a maximum file size of 65535 bytes (the reason `bwscript.bin` exists). If your scripts don't fit, PyAI will offer to "expand" the file, which raises the limit but makes the file require the AISE plugin to work in the game (see [Plugins](#plugins)).

## Data Files
PyAI uses some of the games data files to display script names, to let you use unit/upgrade/technology names in code, and to validate your scripts:

- [stat_txt.tbl](/Help/Files/TBL.md): The names of AI scripts, units, upgrades, and technologies.
- [units.dat](/Help/Files/DAT/units.dat.md): Unit data, used for checks like whether a unit is a building or can attack ground/air.
- [upgrades.dat](/Help/Files/DAT/upgrades.dat.md): Upgrade data.
- [techdata.dat](/Help/Files/DAT/techdata.dat.md): Technology data.

**Manage Settings** (`Ctrl+U`) opens the settings dialog where you can choose these files (from disk or from your MPQs), manage the MPQs to load files from, and change the theme. The settings dialog also opens automatically at startup if any of the files fail to load.
The toolbar also has **Save TBL and DAT Settings** and **Open TBL and DAT Settings** buttons, which save your data file choices to a small settings file and load them back later, so you can quickly switch between sets of data files (for example between two mods).

## Editing Scripts
- **Add Blank Script** (`Insert`): Creates a new script containing just a `stop()` command. You choose its AI ID, string, and flags.
- **Remove Scripts** (`Delete`): Removes the selected scripts.
- **Edit AI Script** (`Ctrl+E`): Opens the selected scripts in the [Code Editor](/Help/Programs/PyAI/Code_Editor.md) to edit their code.
- **Edit AI ID, String, and Extra Info.** (`Ctrl+I`): Edits the selected scripts 4 character AI ID and its `stat_txt.tbl` string. The AI ID cannot contain commas, parenthesis, or colons. The string can be chosen from a list with the Browse... button, and the dialog also has a Flags... button.
- **Edit Flags** (`Ctrl+G`): Edits the selected scripts flags.

## Script Flags
Each script has three flags, shown in the script list in binary form:

- **BroodWar Only**: The script is only available in BroodWar.
- **Invisible in StarEdit**: The script is hidden from the AI script list in StarEdit.
- **Requires a Location**: The script must be run on a location (for scripts run by the "Run AI Script at Location" trigger action).

## Finding Scripts
**Find Scripts** (`Ctrl+F`) searches the loaded scripts by any combination of AI ID, which file the script is in (`aiscript.bin`, `bwscript.bin`, or either), flags, string ID, and string text. The search terms can be matched Case Sensitive and/or as Regular Expressions (otherwise they are matched as substrings). Selecting results and pressing Select will select those scripts in the main window.

## Exporting and Importing
- **Export Scripts** (`Ctrl+Alt+E`): Decompiles the selected scripts to a text file. If a script references blocks in other scripts, the referenced scripts are exported as well.
- **Import Scripts** (`Ctrl+Alt+I`): Compiles a text file into the loaded files. Imported scripts with the same AI ID as an existing script will replace the existing script.
- **Import a List of Files** (`Ctrl+L`): Manages a list of text files to import from, which is remembered between sessions. You can import individual files from the list, or all of them at once.
- **Decompiling Format**: Chooses the code styles used when decompiling: Block (`--block--` or `:block`), Command (`wait 1` or `wait(1)`), and Comment (`# comment` or `; comment`). This only affects decompiled output; all styles are always accepted when compiling. See [AI Language](/Help/Programs/PyAI/AI_Language.md) for details on the styles.

## External Definitions
**Manage External Definition Files** (`Ctrl+X`) manages a list of external definition files, which is remembered between sessions. External definition files can define variables (to give meaningful names to values in your code) and definition directives, and are applied every time scripts are compiled or decompiled — when decompiling, values are replaced by their variable names. See [External Definitions](/Help/Programs/PyAI/AI_Language.md#external-definitions) for the file format.

## Plugins
The core AI language is the set of commands supported by the unmodded game. Plugins extend the game (and the language) with extra functionality — currently PyAI supports the **AISE** plugin (see [AISE Commands](/Help/Programs/PyAI/AISE_Commands.md)).
Using a plugin command in your code, or "expanding" a file past its normal size limit, makes the saved files require that plugin to be installed in the game. PyAI will ask for confirmation before compiling changes that add a new plugin requirement (listing the reasons), show the required plugins in the status bar, and warn when opening files that require plugins.

## Fixing Issues
`aiscript.bin` and `bwscript.bin` are a pair: every script stored in `bwscript.bin` should have a matching entry in `aiscript.bin`. If the files don't match up when opening them, PyAI shows a dialog listing each issue so you can decide how to resolve it:

- **Script exists in bwscript.bin but is not defined in aiscript.bin**: Either delete the script from `bwscript.bin`, or add a definition for it to `aiscript.bin`.
- **Script is in aiscript.bin but also exists in bwscript.bin**: Either delete the script from `bwscript.bin`, replace the script in `aiscript.bin` with the one in `bwscript.bin`, or change the ID of one of the two scripts.

Each issue can preview the affected script code from either file before you decide. Cancelling the dialog cancels opening the files.

## Command Line
PyAI can also be used from the command line to decompile and compile scripts without opening the GUI:

```
PyAI [options] <inp|aiscriptin bwscriptin> [out|aiscriptout bwscriptout]
```

- `-d`, `--decompile`: Decompile AI's from an `aiscript.bin` and/or `bwscript.bin` (the default).
- `-c`, `--compile`: Compile AI's to an `aiscript.bin` and/or `bwscript.bin`.
- `-u`, `--units`: Specify your own `units.dat` file for unit data lookups.
- `-g`, `--upgrades`: Specify your own `upgrades.dat` file for upgrade data lookups.
- `-t`, `--techdata`: Specify your own `techdata.dat` file for technology data lookups.
- `-x`, `--stattxt`: Specify the `stat_txt.tbl` file to use.
- `-s`, `--scripts`: A list of AI Script ID's to decompile, separated by commas (default: all).
- `-a`, `--aiscript`: The base `aiscript.bin` file to compile on top of.
- `-b`, `--bwscript`: The base `bwscript.bin` file to compile on top of (requires `--aiscript`).
- `-w`, `--hidewarns`: Hides any warnings produced by compiling your code.
- `-f`, `--deffile`: An External Definition file containing variables to be used when compiling/decompiling.
- `--gui`: Opens a file with the GUI.

## See Also
- [Code Editor](/Help/Programs/PyAI/Code_Editor.md)
- [AI Language](/Help/Programs/PyAI/AI_Language.md)
- [Command Reference](/Help/Programs/PyAI/Command_Reference.md)
- [AISE Commands](/Help/Programs/PyAI/AISE_Commands.md)
- [AI Basics](/Help/Tutorials/AI_Basics.md)
- [Creating Your First AI Script](/Help/Tutorials/Creating_Your_First_AI_Script.md)
