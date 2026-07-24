# PyTILE
PyTILE is a tool used for editing [tilesets](/Help/Files/Tilesets/Tilesets.md), which are stored in a handful of different file types, with [.cv5](/Help/Files/Tilesets/CV5.md) being used as the "main" file. PyTILE provides editors for MegaTile Group settings, MegaTile flags, and MiniTile graphics, along with a comprehensive export and import system for the graphics and settings. If you are new to tileset editing, start with the [Editing a Tileset](/Help/Tutorials/Editing_a_Tileset.md) tutorial.
The main areas of PyTILE are covered by their own pages:

- [Tile Groups](/Help/Programs/PyTILE/Tile_Groups.md) ([.cv5](/Help/Files/Tilesets/CV5.md))
- [Doodad Groups](/Help/Programs/PyTILE/Doodad_Groups.md) ([dddata.bin](/Help/Files/Tilesets/dddata.bin.md))
- [MegaTile Editor](/Help/Programs/PyTILE/MegaTile_Editor.md) ([.vf4](/Help/Files/Tilesets/VF4.md), [.vx4](/Help/Files/Tilesets/VX4.md), [.vr4](/Help/Files/Tilesets/VR4.md))
- [Tile Palette](/Help/Programs/PyTILE/Tile_Palette.md)
- [Importing and Exporting](/Help/Programs/PyTILE/Importing_and_Exporting.md)

## Main Window
The left side of the window is a palette listing every MegaTile Group in the tileset, with each group shown as its row of 16 MegaTiles. Clicking a group selects it, and clicking a specific MegaTile in the group selects that MegaTile for editing.
The right side of the window shows the settings of the selected group, arranged into labeled panels. Which panels are shown depends on the type of the selected group — see [Tile Groups](/Help/Programs/PyTILE/Tile_Groups.md) for normal terrain groups and [Doodad Groups](/Help/Programs/PyTILE/Doodad_Groups.md) for doodad groups. Hover over any field for a tooltip explaining what it does. The **MegaTile** panel contains the embedded [MegaTile Editor](/Help/Programs/PyTILE/MegaTile_Editor.md) for the selected MegaTile.
The status bar shows a status message, an indicator for unsaved changes, and whether the tileset uses an [expanded VX4 file](#expanded-vx4-files).

## Managing Files
A tileset is made up of multiple files, and PyTILE loads and saves them together:

- **Open** (`Ctrl+O`): Opens a `.cv5` file, automatically loading the sibling [.vf4](/Help/Files/Tilesets/VF4.md), [.vx4](/Help/Files/Tilesets/VX4.md), [.vr4](/Help/Files/Tilesets/VR4.md), and `.wpe` palette files, and the `dddata.bin` inside the folder named after the tileset.
- **Save** (`Ctrl+S`) and **Save As** (`Ctrl+Alt+A`): Saves all of the tilesets component files next to the chosen `.cv5` path (creating the folder for `dddata.bin` if needed).
- **Close** (`Ctrl+W`): Closes the tileset, asking to save any unsaved changes first.
- **MegaTile Group Palette** (`Ctrl+P`): Opens the [Tile Palette](/Help/Programs/PyTILE/Tile_Palette.md) for the MegaTile Groups, where you can add groups and import/export graphics and settings.
- **Manage Settings** (`Ctrl+M`): Opens the settings dialog to manage the [MPQs](/Help/Files/MPQ.md) data files are loaded from, choose the `stat_txt.tbl` file (used for [Doodad Group names](/Help/Programs/PyTILE/Doodad_Groups.md#name)), and change the PyMS window [theme](/Help/Programs/Themes.md).
- **Set as default `*.cv5` editor** (Windows Only): Associates `.cv5` files with PyTILE, so they open in PyTILE when double clicked.

## Expanded VX4 Files
The standard `.vx4` format is limited to 32768 MiniTile graphics. The expanded format (`.vx4ex`, created by the community "VX4 Expander Plugin") raises the limit to allow far more MiniTiles. When opening a tileset PyTILE automatically prefers a `.vx4ex` file if one exists next to the `.cv5`, warns you that the tileset is expanded, and shows a **VX4 Expanded** indicator in the status bar. When a tileset runs out of MiniTiles (adding or [importing graphics](/Help/Programs/PyTILE/Importing_and_Exporting.md#graphics)), PyTILE offers to expand the VX4, and saving will then produce a `.vx4ex` file. Expanded tilesets require the plugin (or StarCraft: Remastered) to be usable in the game.

## Command Line
PyTILE has no command line compiling/decompiling; the only option opens a file with the GUI:

```
PyTILE [options]
```

- `--gui`: Opens a file with the GUI.

## See Also
- [Tile Groups](/Help/Programs/PyTILE/Tile_Groups.md)
- [Doodad Groups](/Help/Programs/PyTILE/Doodad_Groups.md)
- [MegaTile Editor](/Help/Programs/PyTILE/MegaTile_Editor.md)
- [Tile Palette](/Help/Programs/PyTILE/Tile_Palette.md)
- [Importing and Exporting](/Help/Programs/PyTILE/Importing_and_Exporting.md)
- [Tilesets](/Help/Files/Tilesets/Tilesets.md)
- [Editing a Tileset](/Help/Tutorials/Editing_a_Tileset.md)
