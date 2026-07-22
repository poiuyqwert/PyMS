# PyFNT
PyFNT is a tool used to view and edit the games fonts, contained in [.fnt](/Help/Files/FNT.md) files. Rather than editing pixels directly, PyFNT works by exporting a font to a [.bmp](/Help/Files/BMP.md) image, which you edit in any image editor and then import back into a font. If you are new to font editing, start with the [Editing a Font](/Help/Tutorials/Editing_a_Font.md) tutorial.

## Main Window
The left side of the window is the **Characters** list, showing each letter in the font by its ASCII code and character (for example `65 (A)`). Selecting a letter shows it magnified in the **Display** area on the right. The display is a preview only — the pixels themselves are changed by [exporting and importing](#exporting-and-importing).
The status bar at the bottom shows the result of the last action and an indicator for unsaved changes.
On Windows, the **Set as default `*.fnt` editor** button associates `.fnt` files with PyFNT, so they open in PyFNT when double clicked.

## Managing Files
- **New** (`Ctrl+N`): Creates a blank font. The **FNT Specifications** dialog asks for the ASCII code of the lowest character (default 32, a space), how many letters are in the font (default 208 — together they can cover at most the 256 ASCII codes), and the max width and height of each character (defaults 8 and 11).
- **Open** (`Ctrl+O`): Opens a `.fnt` file.
- **Save** (`Ctrl+S`) and **Save As** (`Ctrl+Alt+A`): Saves the font.
- **Close** (`Ctrl+W`): Closes the font.

Creating, opening, importing, or closing a font (or exiting PyFNT) asks to save any unsaved changes first.

## Exporting and Importing
Editing letters is done outside of PyFNT, by exporting the font to a `.bmp`, editing the image, and importing it back:

- **Export Font** (`Ctrl+E`): Exports every letter into a single [.bmp](/Help/Files/BMP.md) image, laid out side by side in one row, each letter taking an equal width.
- **Import Font** (`Ctrl+I`): Imports a `.bmp` in that same layout as a new font. The **FNT Specifications** dialog asks for the lowest ASCII code and the amount of letters, and the image is sliced into that many equal width columns (the image height becomes the letter height). The imported font is unsaved, so **Save As** it when you are done.

Each letter can only use up to 8 colors, which the game maps to actual text colors through a color ramp — the exported image shows them as colors from the [special palette](#settings), with the first palette color as the transparent background.

## Settings
**Manage MPQ's and Special Palette** (`Ctrl+M`) opens the settings dialog, which also opens automatically at startup if the palette fails to load:

- **MPQ Settings**: Manages the list of [MPQs](/Help/Files/MPQ.md) that game files are loaded from (usually your StarCraft MPQs and/or your mods MPQ).
- **Palette Settings**: Chooses the `tfontgam.pcx` special palette, which holds the text colors used to display and export letters (by default it is loaded from your MPQs).
- **Theme**: Changes the PyMS window [theme](/Help/Programs/Themes.md).

## Command Line
PyFNT can also be used from the command line to decompile `.fnt` files to `.bmp` images and compile them back:

```
PyFNT [options] <inp> [out]
```

- `-d`, `--decompile`: Decompile a FNT file to a BMP (the default).
- `-c`, `--compile`: Compile a BMP into a FNT file.
- `-s`, `--specifics`: The lowest ASCII index and amount of letters, separated by a comma (for example `-s 32,208`). Required when compiling.
- `--gui`: Opens a file with the GUI.

## See Also
- [Editing a Font](/Help/Tutorials/Editing_a_Font.md)
- [FNT](/Help/Files/FNT.md)
- [BMP](/Help/Files/BMP.md)
- [Themes](/Help/Programs/Themes.md)
