# PyLO
PyLO is a tool used for editing the offset data contained in the various [.lo?](/Help/Files/LO.md) files, which the game uses to position things relative to a unit's graphics — like where overlay graphics are drawn, or where projectiles spawn. PyLO decompiles the `.lo?` files into text source code, and compiles the text source code back into a `.lo?` file.
The source code is written using the built in [Code Editor](/Help/Programs/PyLO/Code_Editor.md), with a live [Previewer](/Help/Programs/PyLO/Previewer.md) to visualize and adjust the offsets on real graphics. If you are new to offset editing, start with the [Editing Offsets](/Help/Tutorials/Editing_Offsets.md) tutorial.

## Main Window
The main window shows the [Code Editor](/Help/Programs/PyLO/Code_Editor.md) on the left and the [Previewer](/Help/Programs/PyLO/Previewer.md) on the right. The toolbar at the top holds the file, editing, and settings actions, and the status bar at the bottom shows the result of the last action along with an indicator for unsaved changes.

## Managing Files
- **New** (`Ctrl+N`): Creates new source code, with a single frame containing a single `(0, 0)` offset.
- **Open** (`Ctrl+O`): Opens a `.lo?` file, decompiling it into the editor.
- **Save** (`Ctrl+S`) and **Save As** (`Ctrl+Alt+A`): Compiles the source code and saves it as a `.lo?` file. Compile errors are shown, and nothing is saved until the code compiles.
- **Import LO?** (`Ctrl+I`): Loads source code from a text file into the editor. The file must compile to be imported.
- **Export LO?** (`Ctrl+E`): Saves the source code in the editor to a text file.
- **Close** (`Ctrl+W`): Closes the loaded file.
- **Set as default .lo? editor** (Windows Only): Associates the `.lo?` file extensions with PyLO, so they open in PyLO when double clicked.

Closing a file (or exiting PyLO) with unsaved changes will ask if you want to save them first.

## Settings
- **Manage MPQ Settings** (`Ctrl+M`): Opens the settings dialog, where you manage the [MPQs](/Help/Files/MPQ.md) that the [Previewer](/Help/Programs/PyLO/Previewer.md) can load its [GRP](/Help/Files/GRP.md) files from, and change the [theme](/Help/Programs/Themes.md).
- **Color Settings** (`Ctrl+Alt+C`): Customizes the syntax highlighting styles of the [Code Editor](/Help/Programs/PyLO/Code_Editor.md).

## Command Line
PyLO can also be used from the command line to decompile and compile `.lo?` files without opening the GUI:

```
PyLO [options] <inp> [out]
```

- `-d`, `--decompile`: Decompile a `.lo?` file to text source code (the default).
- `-c`, `--compile`: Compile text source code to a `.lo?` file.
- `--gui`: Opens a file with the GUI.

If no output file is given, the output is named after the input file, with the extension swapped to `.txt` when decompiling or `.lox` when compiling.

## See Also
- [Code Editor](/Help/Programs/PyLO/Code_Editor.md)
- [Previewer](/Help/Programs/PyLO/Previewer.md)
- [LO?](/Help/Files/LO.md)
- [Editing Offsets](/Help/Tutorials/Editing_Offsets.md)
