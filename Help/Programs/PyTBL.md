# PyTBL
PyTBL is a tool used for editing the text stored in [.tbl](/Help/Files/TBL.md) files, such as `stat_txt.tbl` which contains most of the text in the game — unit names, button tooltips, error messages, and more. If you are new to editing the games text, start with the [Editing Game Text](/Help/Tutorials/Editing_Game_Text.md) tutorial.

## Main Window
The left side of the window is the string list, showing every string in the file with special characters displayed as [escape codes](/Help/Files/TBL.md#string-format) like `<0>`. Selecting a string loads it into the editor, and right clicking the list opens a menu with the [string actions](#working-with-strings).
The top right of the window is the text editor for the selected string. Edits apply as you type — the string list updates live and the unsaved changes indicator lights up in the status bar. Newlines (`<10>`) are shown as real line breaks, and other special characters are typed and shown as their `<N>` escape codes. The editor supports undo (`Ctrl+Z`) and select all (`Ctrl+A`).
The bottom right of the window is an always-visible reference listing the [color codes](/Help/Files/TBL.md#color-codes) and other special characters, so you don't need to memorize them.
The status bar shows the result of the last action, an indicator for unsaved changes, and the index of the selected string along with the total string count.

## Managing Files
- **New** (`Ctrl+N`): Creates a new, empty TBL.
- **Open** (`Ctrl+O`): Opens a `.tbl` file.
- **Open Default TBL** (`Ctrl+D`): Opens the standard `stat_txt.tbl` bundled with PyMS.
- **Import Strings** (`Ctrl+I`): Loads strings from a `.txt` file in the format created by **Export Strings**, replacing the current strings. Each line is one string (with special characters written as `<N>` escape codes), and `#` starts a comment.
- **Save** (`Ctrl+S`) and **Save As** (`Ctrl+Alt+A`): Saves the `.tbl` file.
- **Export Strings** (`Ctrl+E`): Saves the strings to an editable `.txt` file, one string per line. Exporting, editing the text, and re-importing can be an easy way to make bulk changes.
- **Close** (`Ctrl+W`): Closes the file.
- **Set as default `.tbl` editor** (Windows only): Associates `.tbl` files with PyTBL, so they open in PyTBL when double clicked.

Closing PyTBL (or loading another file over unsaved changes) asks to save first.

## Working with Strings
- **Add String** (`Insert`): Adds a new empty string to the end of the file.
- **Insert String** (`Shift+Insert`): Inserts a new empty string before the selected string.
- **Remove String** (`Delete` in the string list, `Shift+Delete` in the editor): Deletes the selected string.
- **Move String Up** (`Shift+Up`) and **Move String Down** (`Shift+Down`): Swaps the selected string with the one above or below it.

These actions are also available by right clicking the string list. Keep in mind that the game and other files (like the `.dat` files) refer to TBL strings by their index, so inserting, removing, or moving a string changes the index of every string after it.

## Finding Strings
- **Find Strings** (`Ctrl+F`): Searches the string list for text. **Case Sensitive** matches the exact casing, **Regular Expression** treats the search text as a regular expression, and **Wrap** continues the search from the other end of the list when it reaches the end. **Direction** chooses whether to search up or down from the selected string. Press **Find Next** (`F3`, or `Enter` in the dialog) to jump to the next match. Your search history is kept for the session.
- **Go to** (`Ctrl+G`): Jumps straight to a string by its index (hex values are accepted).

## Text Previewer
**Test String** (`Ctrl+T`) opens the Text Previewer, which renders the selected string the way it looks in the game, using the fonts, text colors, and icons from your [settings](#settings):

- **Hotkey String**: Treats the string as a command button tooltip — the leading hotkey and [hotkey type](/Help/Files/TBL.md#hotkey-types) characters are read, and example requirements (like mineral and gas costs) are displayed based on the type.
- **End at Null**: Stops the preview at the first `<0>`, like the game does.

## Settings
**Manage Settings** (`Ctrl+M`) opens the settings dialog, which also opens automatically at startup if any of the preview files fail to load:

- **MPQ Settings**: Manages the list of MPQs that the preview files are loaded from (usually your StarCraft MPQs and/or your mods MPQ).
- **Preview Settings**: Chooses the files used by the [Text Previewer](#text-previewer): `tfontgam.pcx` (the text colors), `font8.fnt` and `font10.fnt` (the [fonts](/Help/Files/FNT.md) used for hotkey and normal strings), `icons.grp` (the requirement icons), and the [palette](/Help/Files/Palettes.md) used to display the icons.
- **Theme**: Changes the PyMS window [theme](/Help/Programs/Themes.md).

## Command Line
PyTBL can also be used from the command line to decompile `.tbl` files to editable text files and compile them back:

```
PyTBL [options] <inp> [out]
```

- `-d`, `--decompile`: Decompile a TBL file to a `.txt` file (the default).
- `-c`, `--compile`: Compile a `.txt` file to a TBL file.
- `-r`, `--reference`: Put a reference for colors and other special characters at the top of the decompiled file.
- `--gui`: Opens a file with the GUI.

## See Also
- [TBL](/Help/Files/TBL.md)
- [Color Codes](/Help/Files/TBL.md#color-codes)
- [Hotkey Types](/Help/Files/TBL.md#hotkey-types)
- [Editing Game Text](/Help/Tutorials/Editing_Game_Text.md)
- [MPQ](/Help/Files/MPQ.md)
