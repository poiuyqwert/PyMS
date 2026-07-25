# PyDAT
PyDAT is a tool used to edit the various `.dat` files, which contain the settings for lots of aspects of the game. Its design and field explanations are based on BroodKillers DatEdit, so it should feel familiar to anyone that has used that tool. If you are new to `.dat` editing, start with the [Editing a Unit](/Help/Tutorials/Editing_a_Unit.md) tutorial.
Each `.dat` file is edited in its own tab of the main window:

- [Units](/Help/Programs/PyDAT/Units.md) ([units.dat](/Help/Files/DAT/units.dat.md))
- [Weapons](/Help/Programs/PyDAT/Weapons.md) ([weapons.dat](/Help/Files/DAT/weapons.dat.md))
- [Flingy](/Help/Programs/PyDAT/Flingy.md) ([flingy.dat](/Help/Files/DAT/flingy.dat.md))
- [Sprites](/Help/Programs/PyDAT/Sprites.md) ([sprites.dat](/Help/Files/DAT/sprites.dat.md))
- [Images](/Help/Programs/PyDAT/Images.md) ([images.dat](/Help/Files/DAT/images.dat.md))
- [Upgrades](/Help/Programs/PyDAT/Upgrades.md) ([upgrades.dat](/Help/Files/DAT/upgrades.dat.md))
- [Techdata](/Help/Programs/PyDAT/Techdata.md) ([techdata.dat](/Help/Files/DAT/techdata.dat.md))
- [Sfxdata](/Help/Programs/PyDAT/Sfxdata.md) ([sfxdata.dat](/Help/Files/DAT/sfxdata.dat.md))
- [Portdata](/Help/Programs/PyDAT/Portdata.md) ([portdata.dat](/Help/Files/DAT/portdata.dat.md))
- [Mapdata](/Help/Programs/PyDAT/Mapdata.md) ([mapdata.dat](/Help/Files/DAT/mapdata.dat.md))
- [Orders](/Help/Programs/PyDAT/Orders.md) ([orders.dat](/Help/Files/DAT/orders.dat.md))

## Main Window
The left side of the window is the entry list for the active tab, showing each entry with its ID and name. Selecting an entry loads it into the tab, and right clicking the list opens a menu with the [entry actions](#working-with-entries).
Below the entry list is a collapsible options panel:

- **Find**: Searches the entry list by name (case insensitive substring match). Press `Enter` or the **Next** button to cycle through the matches. Your search history is kept for the session.
- **ID Jump**: Jumps straight to an entry by its ID (hex values are accepted).
- **Names**: Chooses how entry names are displayed — **Basic** uses the standard names bundled with PyMS, **TBL** uses the strings from your [TBL files](#data-files), and **Combined** shows both. **Simple TBL Names** hides the extra data in TBL strings (like hotkeys and formatting codes), for the DAT types whose names come from `stat_txt.tbl`.

The right side of the window shows the settings of the selected entry, grouped into labeled sections. Hover over any field for a tooltip explaining what it does. Fields that reference an entry in another DAT file have a dropdown to pick the entry by name and a **Jump ->** button to go edit it.
The status bar shows the file path of the active tabs file, an indicator for unsaved changes, and whether the file is [expanded](#expanded-dat-files).

## Managing Files
Each tab manages its own file, and the file actions apply to the active tab (except the ones that load or save multiple files at once). Closing PyDAT (or loading over a tab) asks to save any unsaved changes first.

- **New** (`Ctrl+N`): Resets the active tab to the default file loaded from your MPQs.
- **Open** (`Ctrl+O`): Opens a `.dat` file. The DAT type is recognized by its filename (for example `units.dat`), and PyDAT switches to its tab.
- **Open Directory** (`Ctrl+D`): Scans a folder and opens every `.dat` file found in it.
- **Open MPQ** (`Ctrl+Alt+O`): Opens every `.dat` file found in the `arr` folder of an [MPQ](/Help/Files/MPQ.md) (or self-executing MPQ).
- **Save** (`Ctrl+S`) and **Save As** (`Ctrl+Alt+S`): Saves the active tabs file.
- **Export to TXT** (`Ctrl+E`): Saves the active tabs file as an editable text file listing every entry and its properties.
- **Import from TXT** (`Ctrl+I`): Loads entries from the text format produced by **Export to TXT**, asking before each entry is overwritten (Yes / Yes to All / No / Cancel). Exporting, editing the text, and re-importing can be an easy way to make bulk changes.
- **Save MPQ** (`Ctrl+Alt+M`): Saves files directly into an MPQ at their correct paths. You choose any combination of the eleven `.dat` files, the TBL files, and `cmdicons.grp`.
- **Reload data files** (`Ctrl+R`): Reloads the [data files](#data-files) (TBLs, icons, iscript, and palettes) from your MPQs, to pick up outside changes.
- **Set as default `.dat` editor** (Windows Only): Associates `.dat` files with PyDAT, so they open in PyDAT when double clicked.

Opening and saving MPQs requires MPQ support (SFmpq) to be available.

## Working with Entries
Right clicking the entry list opens a menu with actions for the selected entry:

- **Copy Entry to Clipboard** (`Shift+Ctrl+C`): Copies the entry to the clipboard in the same text format as **Export to TXT**.
- **Copy Sub-Tab to Clipboard** (`Ctrl+Y`): On the Units tab only — copies just the properties shown on the active sub-tab.
- **Paste from Clipboard** (`Shift+Ctrl+P`): Imports copied text over the selected entry. Since it is plain text you can also paste between PyDAT windows, or edit the text before pasting.
- **Reload Entry**: Resets the selected entry back to its values in the default file from your MPQs.
- **Add Entry (DatExtend)** (`Shift+Ctrl+A`) and **Set Entry Count (DatExtend)** (`Shift+Ctrl+S`): Adds [expanded entries](#expanded-dat-files).
- **Override Name** (`Shift+Ctrl+N`): Opens the [Name Overrides](#name-overrides) dialog for the selected entry.

## Name Overrides
**Name Overrides** (`Shift+Ctrl+N`) lets you rename entries in the entry list, which is especially useful for expanded entries or total conversions. Each DAT type has its own list of overrides.
Enter an ID and a name and press **Update** to set an override (an empty name removes it). Checking **Append** adds your name onto the end of the normal name instead of replacing it. Overrides only affect how entries are listed in PyDAT — they are not saved into the `.dat` file itself.
The overrides for a DAT type can be saved to and loaded from a text file with the **Save As** and **Open** buttons, with one override per line in the form `ID:Name` (or `ID+:Name` for an appended name).

## Used By
The bottom of each tab has a collapsible **Used By** panel, listing every entry (in any of the loaded DAT files) that references the current entry — for example, viewing a weapon shows which units and orders use it. Double click a listing (or press `Enter`) to jump to the referencing entry.

## Expanded DAT Files
PyDAT supports expanded DAT files, which allow you to add new entries to any of the DAT files. To use expanded DAT files in your mod, you will need a plugin like [DatExtend](https://github.com/saintofidiocy/GPTP/tree/DatExtender) to be able to handle these files.
To add expanded entries to a DAT file, you can right click on the list of entries, and choose the `Add Entry (DatExtend)` or `Set Entry Count (DatExtend)` options, or use the associated keyboard shortcuts `Shift+Ctrl+A` or `Shift+Ctrl+S` respectively. **Set Entry Count** shows the constraints for the DAT type (minimum/maximum entry counts, entry count multiples, and reserved entries) and the resulting count as you type.
The status bar shows an indicator when the active tabs file is expanded, and PyDAT warns when opening expanded files since they require a plugin. Expanded units get their names from `unitnames.tbl` (see [Data Files](#data-files)) — or you can use [Name Overrides](#name-overrides) to name any expanded entry.

## Data Files
PyDAT uses the games data files to display entry names, referenced files, icons, and graphics previews. They are loaded from your MPQs (or from files you choose) at startup.
**Manage MPQ and TBL files** (`Ctrl+M`) opens the settings dialog, which also opens automatically at startup if any of the files fail to load:

- **MPQ Settings**: Manages the list of MPQs that data files are loaded from (usually your StarCraft MPQs and/or your mods MPQ).
- **TBL Settings**: Chooses the [TBL](/Help/Files/TBL.md) files: `stat_txt.tbl` (unit, weapon, upgrade, technology, and order names), `unitnames.tbl` (unit names for expanded dat files), `images.tbl` ([GRP](/Help/Files/GRP.md) file paths), `sfxdata.tbl` (sound file paths), `portdata.tbl` (portrait file paths), and `mapdata.tbl` (campaign map paths). **Use custom labels** makes the TBL based entry names update live as you edit an entrys label, rather than using the default strings.
- **Other Settings**: Chooses `cmdicons.grp` (the icon images) and `iscript.bin` (the [IScript](/Help/Files/iscript.bin.md) entries referenced by images.dat).
- **Palette Settings**: Chooses the [palettes](/Help/Files/Palettes.md) used to render previews: `Units.pal`, `bfire.pal`, `gfire.pal`, and `ofire.pal` for graphics with those remappings, `Terrain.pal` for terrain based graphics, and `Icons.pal` for icons.
- **Theme**: Changes the PyMS window [theme](/Help/Programs/Themes.md).

## Command Line
PyDAT can also be used from the command line to decompile `.dat` files to the text format and compile them back:

```
PyDAT [options] <inp> [out]
```

- `-d`, `--decompile`: Decompile a DAT file (the default).
- `-c`, `--compile`: Compile a DAT file.
- `-u`, `--units`: Decompiling/Compiling `units.dat` (the default type).
- `-w`, `--weapons`: Decompiling/Compiling `weapons.dat`.
- `-f`, `--flingy`: Decompiling/Compiling `flingy.dat`.
- `-s`, `--sprites`: Decompiling/Compiling `sprites.dat`.
- `-i`, `--images`: Decompiling/Compiling `images.dat`.
- `-g`, `--upgrades`: Decompiling/Compiling `upgrades.dat`.
- `-t`, `--techdata`: Decompiling/Compiling `techdata.dat`.
- `-l`, `--sfxdata`: Decompiling/Compiling `sfxdata.dat`.
- `-p`, `--portdata`: Decompiling/Compiling `portdata.dat`.
- `-m`, `--mapdata`: Decompiling/Compiling `mapdata.dat`.
- `-o`, `--orders`: Decompiling/Compiling `orders.dat`.
- `-n`, `--ids`: A list of entry IDs to decompile, separated by commas (default: all).
- `-b`, `--basedat`: The base DAT file to compile on top of (default: the standard file bundled with PyMS).
- `-r`, `--reference`: Put a reference for various values when decompiling.
- `--gui`: Opens a file with the GUI.

## See Also
- [Units Tab](/Help/Programs/PyDAT/Units.md)
- [Weapons Tab](/Help/Programs/PyDAT/Weapons.md)
- [Flingy Tab](/Help/Programs/PyDAT/Flingy.md)
- [Sprites Tab](/Help/Programs/PyDAT/Sprites.md)
- [Images Tab](/Help/Programs/PyDAT/Images.md)
- [Upgrades Tab](/Help/Programs/PyDAT/Upgrades.md)
- [Techdata Tab](/Help/Programs/PyDAT/Techdata.md)
- [Sfxdata Tab](/Help/Programs/PyDAT/Sfxdata.md)
- [Portdata Tab](/Help/Programs/PyDAT/Portdata.md)
- [Mapdata Tab](/Help/Programs/PyDAT/Mapdata.md)
- [Orders Tab](/Help/Programs/PyDAT/Orders.md)
- [Editing a Unit](/Help/Tutorials/Editing_a_Unit.md)
