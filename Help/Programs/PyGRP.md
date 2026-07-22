# PyGRP
PyGRP is a tool for editing various graphics in [.grp](/Help/Files/GRP.md) files, which are used by things like [unit](/Help/Files/DAT/units.dat.md)/[sprite](/Help/Files/DAT/sprites.dat.md) [images](/Help/Files/DAT/images.dat.md), [cmdicons](/Help/Files/GRP.md#cmdicongrp), and much more. PyGRP provides a way to convert `.grp` files to and from [.bmp](/Help/Files/BMP.md) files (in multiple configurations), as well as a way to preview the graphics. If you are new to GRP editing, start with the [Editing a GRP](/Help/Tutorials/Editing_a_GRP.md) tutorial.

## Main Window
The left side of the window holds the **Frames** list and the **Palette** list, and the right side holds the preview:

- **Frames**: Every frame in the GRP. Selecting a frame [previews](#previewing-frames) it, and multiple frames can be selected for [exporting](#exporting-and-importing-frames) or [editing](#editing-frames) (`Ctrl+A` selects them all). The **Hex** checkbox switches the frame numbers between decimal and hexadecimal, and every other [frameset](/Help/Files/GRP.md#framesets) (group of 17 frames) is indented to make the groups easier to tell apart.
- **Palette**: The palettes found in the `Palettes` folder, used to color the previewed and exported frames. Use the palette matching how the game draws the graphic (for example `Units.pal` for unit graphics) — see [Palettes](/Help/Files/Palettes.md).

The status bar at the bottom shows the result of the last action and an indicator for unsaved changes.
On Windows, the **Set as default `*.grp` editor** button associates `.grp` files with PyGRP, so they open in PyGRP when double clicked.

## Managing Files
- **New** (`Ctrl+N`): Creates an empty GRP, which takes its dimensions from the first frames you [import](#exporting-and-importing-frames).
- **Open** (`Ctrl+O`): Opens a `.grp` file. Opening an [uncompressed](/Help/Files/GRP.md#compression) GRP shows a reminder to turn on **Save Uncompressed** before saving.
- **Save** (`Ctrl+S`) and **Save As** (`Ctrl+Alt+A`): Saves the GRP, without compression if the **Save Uncompressed** checkbox is checked.
- **Close** (`Ctrl+W`): Closes the GRP.

Creating, opening, or closing a GRP (or exiting PyGRP) asks to save any unsaved changes first.

## Previewing Frames
Selecting a frame in the **Frames** list shows it on the preview canvas, colored by the selected **Palette**. Double clicking the canvas lets you pick a different background color.
The buttons under the canvas play and step through the frames: jump to the first or last frame, jump 1 frame or a whole [frameset](/Help/Files/GRP.md#framesets) (17 frames) up or down, play every frame or every 17th frame in either direction, and stop. Playing every 17th frame advances the animation while keeping the same facing direction.
The options below the playback buttons control the preview:

- **Preview Speed**: The delay between animation frames, in milliseconds (1 to 5000).
- **Preview Between**: The range of frames the play buttons cycle through.
- **Show Preview**: Turns the preview on or off.
- **Loop Preview**: Wraps around to the other end when playing or jumping past the first or last frame.
- **GRP Outline (Green)**: Outlines the full canvas of the GRP in green.
- **Frame Outline (Red)**: Outlines the visible bounds of the selected frame in red.

## Exporting and Importing Frames
The frame graphics themselves are edited outside of PyGRP, by exporting frames to [.bmp](/Help/Files/BMP.md) images, editing them in any image editor that supports indexed color, and importing them back:

- **Export Selected Frames** (`Ctrl+E`): Exports the frames selected in the **Frames** list (`Ctrl+A` to select them all), colored by the selected **Palette**.
- **Import Frames** (`Ctrl+I`): Imports `.bmp` files as new frames, added to the end of the GRP. When importing a single image containing multiple frames, PyGRP asks how many frames it contains.

The dropdown in the bottom right controls the style of BMP being exported and imported — BMPs must be imported with the same style they were exported as:

- **One BMP per Frame**: Each frame is its own image. Exporting asks for one file name and numbers the files from it (`Name 000.bmp`, `Name 001.bmp`, and so on), and importing lets you select multiple files to import in order.
- **Single BMP (Framesets)**: All the frames in one image, laid out in rows of 17 frames (any unused spots in the last row are filled with the transparent color).
- **Single BMP (Vertical/SFGrpConv)**: All the frames in one image, stacked vertically in one column (the layout used by the SFGrpConv tool).

Every frame in a GRP has the same size, at most 256x256 pixels: imported frames must all match each other (and any frames already in the GRP), and an empty GRP takes its dimensions from the imported frames.
The **Transparent Index** option sets which palette index is treated as transparent (normally 0), used when opening a GRP and when importing frames.

## Editing Frames
- **Remove Frames** (`Delete`): Removes the selected frames.
- **Move Frames Up** (`Ctrl+U`) and **Move Frames Down** (`Ctrl+D`): Move the selected frames one position up or down the frame list.

Since importing adds frames to the end of the GRP, you can replace all the frames by selecting them all (`Ctrl+A`), removing them, and then importing.

## Settings
**Manage Settings** (`Ctrl+M`) opens the settings dialog:

- **Theme**: Changes the PyMS window [theme](/Help/Programs/Themes.md).

## Command Line
PyGRP can also be used from the command line to convert between `.grp` and `.bmp` files:

```
PyGRP [options] <inp> [out]
```

- `-g`, `--grptobmps`: Convert a GRP to BMPs (the default).
- `-b`, `--bmpstogrp`: Convert BMPs to a GRP.
- `-p`, `--palette`: The palette from the `Palettes` folder to color the BMPs with (default `Units.pal`).
- `-u`, `--uncompressed`: The GRP is (or should be saved) uncompressed.
- `-o`, `--onebmp`: Convert the GRP to a single BMP with the frames stacked vertically, instead of one BMP per frame.
- `-f`, `--frames`: The input is a single BMP in the framesets style containing this many frames. Without this option, BMP to GRP conversion starts from the given file and collects the files numbered like `Name 000.bmp`.
- `--gui`: Opens a file with the GUI.

## See Also
- [Editing a GRP](/Help/Tutorials/Editing_a_GRP.md)
- [GRP](/Help/Files/GRP.md)
- [BMP](/Help/Files/BMP.md)
- [Palettes](/Help/Files/Palettes.md)
- [Themes](/Help/Programs/Themes.md)
