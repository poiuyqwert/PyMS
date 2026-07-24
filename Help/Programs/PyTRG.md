# PyTRG
PyTRG is a tool used for editing the triggers in [.trg](/Help/Files/TRG.md) files, used for [maps](/Help/Files/Maps.md) and for initialization of the [game modes](/Help/Files/GOT.md). PyTRG is a text based editor: opening a `.trg` file decompiles its triggers into the [TRG Language](/Help/Programs/PyTRG/TRG_Language.md), you edit the code in the [Code Editor](/Help/Programs/PyTRG/Code_Editor.md), and saving compiles it back into the binary format. If you are new to trigger editing, start with the [Creating Your First Trigger](/Help/Tutorials/Creating_Your_First_Trigger.md) tutorial.

- [TRG Language](/Help/Programs/PyTRG/TRG_Language.md): The text language triggers are written in.
- [Code Editor](/Help/Programs/PyTRG/Code_Editor.md): The editor features (syntax highlighting, autocomplete, tooltips, and more).
- [Conditions Reference](/Help/Programs/PyTRG/Conditions_Reference.md): Every condition and its parameters.
- [Actions Reference](/Help/Programs/PyTRG/Actions_Reference.md): Every action (including mission briefing actions) and its parameters.

## Main Window
The window is a single [Code Editor](/Help/Programs/PyTRG/Code_Editor.md) with a toolbar of file actions above it. The status bar at the bottom shows a status message, an indicator for unsaved changes, and the current line, column, and selection size.
The file actions that work on the open file (Save, Save As, Export, Test Code, Close, and Find/Replace) are disabled until a TRG is created or opened.

## Managing Files
- **New** (`Ctrl+N`): Starts editing a new, empty TRG.
- **Open** (`Ctrl+O`): Opens a `.trg` file and decompiles its triggers into the editor. If the file is not a normal TRG it is retried as a [GOT compatible TRG](#got-compatible-trgs).
- **Import TRG** (`Ctrl+I`): Loads a text file of trigger code into the editor (the format produced by **Export TRG**).
- **Save** (`Ctrl+S`) and **Save As** (`Ctrl+Alt+A`): Compiles the code and saves it as a binary `.trg` file. Compile errors are shown (and highlighted in the code), and nothing is saved until the code compiles.
- **Save `*.got` Compatable `*.trg`** (`Ctrl+G`): Compiles and saves as a [GOT compatible TRG](#got-compatible-trgs).
- **Export TRG** (`Ctrl+E`): Saves the code in the editor to a text file, without compiling it.
- **Test Code** (`Ctrl+T`): Compiles the code without saving it. Errors and warnings are highlighted in the code, or you are told the code compiles cleanly.
- **Close** (`Ctrl+W`): Closes the open TRG, asking to save unsaved changes first.
- **Set as default `*.trg` editor** (Windows Only): Associates `.trg` files with PyTRG, so they open in PyTRG when double clicked.

## GOT Compatible TRGs
The triggers that initialize the [game modes](/Help/Files/GOT.md) (stored at `triggers\*.trg` in the games [MPQs](/Help/Files/MPQ.md)) use a slightly different file format than normal `.trg` files. **Save `*.got` Compatable `*.trg`** (`Ctrl+G`) saves in that format, and **Open** detects it automatically, so you can edit both kinds of file. The [PyGOT](/Help/Programs/PyGOT.md) help covers how a game template references its trigger file.

## Data Files
PyTRG uses `stat_txt.tbl` to show unit names in triggers, and `aiscript.bin`/`bwscript.bin` for the AI scripts used by the RunAIScript actions. They are loaded from your MPQs (or from files you choose) at startup.
**Manage `stat_txt.tbl` and `aiscript.bin` files** (`Ctrl+M`) opens the settings dialog, which also opens automatically at startup if any of the files fail to load:

- **MPQ Settings**: Manages the list of MPQs that data files are loaded from (usually your StarCraft MPQs and/or your mods MPQ).
- **File Settings**: Chooses the `stat_txt.tbl` (unit and AI script names), `aiscript.bin`, and `bwscript.bin` (AI script IDs) files.
- **Theme**: Changes the PyMS window [theme](/Help/Programs/Themes.md).

## Command Line
PyTRG can also be used from the command line to decompile `.trg` files to the text format and compile them back:

```
PyTRG [options] <inp> [out]
```

If `out` is not given, it defaults to the input filename with a `.txt` extension when decompiling, or a `.trg` extension when compiling.

- `-d`, `--decompile`: Decompile a TRG file (the default).
- `-c`, `--compile`: Compile a TRG file.
- `-g`, `--got`: Decompile/compile a GOT compatible TRG.
- `-s`, `--stattxt`: The `stat_txt.tbl` file to use (default: the standard file bundled with PyMS).
- `-a`, `--aiscript`: The `aiscript.bin` file to use (default: the standard file bundled with PyMS).
- `--gui`: Opens a file with the GUI.

## See Also
- [TRG Language](/Help/Programs/PyTRG/TRG_Language.md)
- [Code Editor](/Help/Programs/PyTRG/Code_Editor.md)
- [Conditions Reference](/Help/Programs/PyTRG/Conditions_Reference.md)
- [Actions Reference](/Help/Programs/PyTRG/Actions_Reference.md)
- [Creating Your First Trigger](/Help/Tutorials/Creating_Your_First_Trigger.md)
- [TRG](/Help/Files/TRG.md)
- [GOT](/Help/Files/GOT.md)
