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
A tileset is made up of multiple files, and PyTILE loads and saves them together. These commands are in the **File** menu and on the toolbar:

- **Open** (`Ctrl+O`): Opens a `.cv5` file, automatically loading the sibling [.vf4](/Help/Files/Tilesets/VF4.md), [.vx4](/Help/Files/Tilesets/VX4.md), [.vr4](/Help/Files/Tilesets/VR4.md), and `.wpe` palette files, and the `dddata.bin` inside the folder named after the tileset.
- **Save** (`Ctrl+S`) and **Save As** (`Ctrl+Alt+A`): Saves all of the tilesets component files next to the chosen `.cv5` path (creating the folder for `dddata.bin` if needed).
- **Close** (`Ctrl+W`): Closes the tileset, asking to save any unsaved changes first.
- **Check for Updates...**: Checks GitHub for a newer version of PyTILE and PyMS, and shows the result. PyTILE also checks automatically when it starts, but only shows a message when an update is available.

The rest of the toolbar mirrors the other menus:

- **MegaTile Group Palette** (`Ctrl+P`, **View** menu): Opens the [Tile Palette](/Help/Programs/PyTILE/Tile_Palette.md) for the MegaTile Groups, where you can add groups and import/export graphics and settings.
- **Manage Settings** (`Ctrl+M`, **Settings** menu): Opens the settings dialog to manage the [MPQs](/Help/Files/MPQ.md) data files are loaded from, choose the `stat_txt.tbl` file (used for [Doodad Group names](/Help/Programs/PyTILE/Doodad_Groups.md#name)), and change the PyMS window [theme](/Help/Programs/Themes.md).
- **Set as Default `*.cv5` Editor** (Windows Only, **Settings** menu): Associates `.cv5` files with PyTILE, so they open in PyTILE when double clicked.
- **View Help** (`F1`), **About PyTILE**, and **Donate** (**Help** menu).

## Menus
Besides the commands above, the menubar gives every editing shortcut of the main window a menu item:

- **View**: **Scroll Group Palette Up** (`Page Up`) and **Scroll Group Palette Down** (`Page Down`) scroll the group palette on the left of the window by a page.
- **Group**: **Copy Group Settings** (`Ctrl+Alt+C`) and **Paste Group Settings** (`Ctrl+Alt+V`) copy and paste the selected groups settings through the clipboard, using the categories checked in the **Copy Group Settings** panel (see [Tile Groups](/Help/Programs/PyTILE/Tile_Groups.md#copying-group-settings) and [Doodad Groups](/Help/Programs/PyTILE/Doodad_Groups.md#copying-doodad-settings)). Copy is disabled while no category is checked.
- **MegaTile**: **Copy MegaTile Flags** (`Shift+Ctrl+C`) and **Paste MegaTile Flags** (`Shift+Ctrl+V`) work the same for the selected MegaTiles flags (see [Copying MegaTile Flags](/Help/Programs/PyTILE/MegaTile_Editor.md#copying-megatile-flags)). The **Apply ... Flags to Group** items and **Exclude Null Tiles** (`Shift+Ctrl+N`) are the [Apply to Megas](/Help/Programs/PyTILE/MegaTile_Editor.md#apply-to-megas) actions.

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
