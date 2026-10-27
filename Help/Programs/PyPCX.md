# PyPCX
PyPCX is a tool for viewing and converting Picture Exchange [.pcx](/Help/Files/PCX.md) image files, and working with their [palettes](/Help/Files/Palettes.md). The image itself is edited outside of PyPCX, by exporting it to a [.bmp](/Help/Files/BMP.md) file, editing it in any image editor that supports indexed color, and importing it back. If you are new to PCX editing, start with the [Converting an Image to PCX](/Help/Tutorials/Converting_an_Image_to_PCX.md) tutorial.

## Main Window
The window shows a preview of the open image at its actual size.
The status bar at the bottom shows the result of the last action and an indicator for unsaved changes.

Every command is in the menubar, and most also have a toolbar button:

- **File**: Open, Save, Save As, Import BMP, Export BMP, Close, Check for Updates, and Exit. The toolbar's first group has the same buttons in the same order (Check for Updates is next to the Donate button, and Exit is the last toolbar button). Check for Updates checks GitHub for a newer version of PyPCX and PyMS, and shows the result. PyPCX also checks automatically when it starts, but only shows a message when an update is available.
- **Palette**: Import Palette, and the **Save Palette As** submenu with one item per palette format. The toolbar's second group has the same buttons.
- **Settings**: Manage Settings, and **Set as Default `*.pcx` Editor (Windows Only)**, which associates `.pcx` files with PyPCX on Windows so they open in PyPCX when double clicked.
- **Help**: View Help (`F1`), Donate, and About PyPCX.

## Managing Files
These are in the **File** menu:

- **Open** (`Ctrl+O`): Opens a `.pcx` file.
- **Save** (`Ctrl+S`) and **Save As** (`Ctrl+Alt+A`): Saves the PCX.
- **Close** (`Ctrl+W`): Closes the PCX.

Opening or importing over a file, closing it, or exiting PyPCX asks to save any unsaved changes first.

## Converting to and from BMP
These are in the **File** menu:

- **Import BMP** (`Ctrl+I`): Imports a `.bmp` file as the image, replacing the current image and its palette. Importing also works with no file open, creating a new PCX ready to **Save As**.
- **Export BMP** (`Ctrl+E`): Exports the image to a `.bmp` file.

Imported BMPs must be 256 color (8 bit indexed), with RLE compression or no compression at all.

## Palettes
A PCX contains its own 256 color palette, and PyPCX can replace it or save it out to any of the [palette formats](/Help/Files/Palettes.md). These are in the **Palette** menu (the save items are under its **Save Palette As** submenu):

- **Import Palette** (`Ctrl+Alt+I`): Replaces the image's palette, recoloring the image. Palettes can be loaded from `.pal`, `.wpe`, `.act`, `.pcx`, and `.bmp` files, with the format detected automatically.
- **Save Palette as RIFF `*.pal`** (`Ctrl+R`)
- **Save Palette as JASC `*.pal`** (`Ctrl+J`)
- **Save Palette as StarCraft `*.pal`** (`Ctrl+P`)
- **Save Palette as StarCraft Terrain `*.wpe`** (`Ctrl+T`)
- **Save Palette as Adobe Color Table `*.act`** (`Ctrl+A`)

To edit the palette colors themselves, use [PyPAL](/Help/Programs/PyPAL.md).

## Settings
**Settings > Manage Settings** (`Ctrl+M`) opens the settings dialog:

- **Theme**: Changes the PyMS window [theme](/Help/Programs/Themes.md).

## Command Line
PyPCX can also be used from the command line to convert between `.pcx` and `.bmp` files:

```
PyPCX [options] <inp> [out]
```

- `-p`, `--pcx`: Convert a PCX to a BMP (the default).
- `-b`, `--bmp`: Convert a BMP to a PCX.
- `--gui`: Opens a file with the GUI.

When no output file is given, the converted file is saved next to the input file with the extension swapped.

## See Also
- [Converting an Image to PCX](/Help/Tutorials/Converting_an_Image_to_PCX.md)
- [PCX](/Help/Files/PCX.md)
- [BMP](/Help/Files/BMP.md)
- [Palettes](/Help/Files/Palettes.md)
- [PyPAL](/Help/Programs/PyPAL.md)
- [Themes](/Help/Programs/Themes.md)
