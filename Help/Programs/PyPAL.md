# PyPAL
PyPAL is a tool used for editing color [palette](/Help/Files/Palettes.md) files in various formats. PyPAL provides an editor to modify the 256 colors of a palette, as well as a way to convert between the different supported palette formats. If you are new to palette editing, start with the [Editing a Palette](/Help/Tutorials/Editing_a_Palette.md) tutorial.

**Supported Palette Formats:**
- [RIFF .pal](/Help/Files/Palettes.md#riff-pal)
- [JASC .pal](/Help/Files/Palettes.md#jasc-pal)
- [StarCraft .pal](/Help/Files/Palettes.md#starcraft-pal)
- [Terrain .wpe](/Help/Files/Palettes.md#terrain-wpe)
- [Adobe Color Table .act](/Help/Files/Palettes.md#adobe-color-table-act)
- Palettes embedded in [.pcx](/Help/Files/PCX.md) files (open only)
- Palettes embedded in 8-bit [.bmp](/Help/Files/BMP.md) files (open only)

## Main Window
The window shows the palette as a 16x16 grid of its 256 colors:

- Hovering over a color shows its index, RGB values, and hex value in the status bar at the bottom.
- Clicking a color selects it, shown by a white outline, ready for [copying and pasting](#copying-and-pasting-colors).
- Double clicking a color opens a color picker to [change it](#editing-colors).

Every command is in the menubar (**File**, **Edit**, **Settings** and **Help**), and the toolbar under it has a button for each file, settings and help command, in the same order as the menus.
The status bar also shows an indicator for unsaved changes.
On Windows, **Settings > Set as Default `*.pal` and `*.wpe` Editor (Windows Only)** associates those files with PyPAL, so they open in PyPAL when double clicked.

## Managing Files
These commands are in the **File** menu:

- **New** (`Ctrl+N`): Creates a new palette with every color set to black.
- **Open...** (`Ctrl+O`): Opens a palette file in any of the supported formats — the format is detected automatically.
- **Save** (`Ctrl+S`): Saves the palette back to its file in the same format. A new palette has no format yet, so it must be saved with one of the save as commands first.
- **Save As...**: Saves the palette to a new file, keeping its current format (a new palette is saved as a StarCraft `.pal`). To change the format, see [Converting Between Formats](#converting-between-formats).
- **Close** (`Ctrl+W`): Closes the palette.
- **Check for Updates...**: Checks GitHub for a newer version of PyPAL and PyMS, and shows the result. PyPAL also checks automatically when it starts, but only shows a message when an update is available.
- **Exit**: Closes PyPAL.

Creating, opening, or closing a palette (or exiting PyPAL) asks to save any unsaved changes first.

## Editing Colors
Double click a color in the grid (or select it and use **Edit > Edit Color...**) to open the color picker and choose its new color. The palette updates as soon as the picker is accepted, and the change is written to the file when you save.

## Copying and Pasting Colors
Colors are moved around as hex values (like `#FF00FF`) with the **Edit** menu, which acts on the selected color. Right clicking a color also selects it and opens a menu with the same two commands:

- **Copy** (`Ctrl+C`): Copies the color to the clipboard as a hex value.
- **Paste** (`Ctrl+P`): Sets the color to the hex value on the clipboard. Nothing happens if the clipboard doesn't hold a valid hex color (the right click menu disables it in that case).

Since the colors travel as plain hex values, they can be exchanged with any other program that understands them, like an image editor.

## Converting Between Formats
A palette is converted by opening it and saving it in a different format with the save as commands in the **File** menu (each also has a toolbar button):

- **Save as RIFF `*.pal`...** (`Ctrl+R`)
- **Save as JASC `*.pal`...** (`Ctrl+J`)
- **Save as StarCraft `*.pal`...** (`Ctrl+Alt+P`)
- **Save as StarCraft Terrain `*.wpe`...** (`Ctrl+T`)
- **Save as Adobe Color Table `*.act`...** (`Ctrl+A`)

[.pcx](/Help/Files/PCX.md) and [.bmp](/Help/Files/BMP.md) images can be opened to extract the palette they were made with, but cannot be saved to — save the extracted palette in one of the formats above instead.

## Settings
**Settings > Manage Settings...** (`Ctrl+M`) opens the settings dialog:

- **Theme**: Changes the PyMS window [theme](/Help/Programs/Themes.md).

## Command Line
PyPAL can also be used from the command line to convert between the palette formats:

```
PyPAL [options] <inp> [out]
```

If `out` is left off, the converted palette is saved next to the input file with the new format's extension.

- `-s`, `--starcraft`: Convert to StarCraft `.pal` (the default).
- `-w`, `--wpe`: Convert to StarCraft Terrain `.wpe`.
- `-r`, `--riff`: Convert to RIFF `.pal`.
- `-j`, `--jasc`: Convert to JASC `.pal`.
- `-a`, `--act`: Convert to Adobe Color Table `.act`.
- `--gui`: Opens a file with the GUI.

## See Also
- [Editing a Palette](/Help/Tutorials/Editing_a_Palette.md)
- [Palettes](/Help/Files/Palettes.md)
- [PCX](/Help/Files/PCX.md)
- [BMP](/Help/Files/BMP.md)
- [Themes](/Help/Programs/Themes.md)
