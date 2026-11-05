# PyGRAFT
PyGRAFT is a tool used for editing the `.graft` files of the GPTP Graft Hook, a replacement for FireGraft. The Graft Hook loads six files from the `datreq` folder of your mod's MPQ: the requirements for training or building units (`Units.graft`), researching upgrades (`Upgrades.graft`), researching technologies (`Research.graft`), using technologies (`Tech.graft`), and using orders (`Orders.graft`), along with the command card buttons (`Buttons.graft`).

PyGRAFT is in early development: the tabs don't edit their entries yet. To make changes, use **Export to TXT**, edit the text, then **Import from TXT**.

## Main Window
The menubar holds every command, in the **File**, **Settings**, and **Help** menus, and the toolbar under it has buttons for the file actions and settings (hover over a button to see its name and shortcut).

The right side of the window has a tab for each part of the Graft files:

- **Button Sets**: The sets of buttons that button cards use, from `Buttons.graft`.
- **Button Cards**: The button card of each unit, followed by the special button cards, from `Buttons.graft`.
- **Unit Stat Info**: The functions that show each unit's stats, from `Buttons.graft`.
- **Unit Training Reqs.**: The requirements for training or building units, from `Units.graft`.
- **Upgrade Research Reqs.**: The requirements for researching upgrades, from `Upgrades.graft`.
- **Tech Research Reqs.**: The requirements for researching technologies, from `Research.graft`.
- **Tech Usage Reqs.**: The requirements for using technologies, from `Tech.graft`.
- **Order Reqs.**: The requirements for using orders, from `Orders.graft`.

The **Button Sets**, **Button Cards**, and **Unit Stat Info** tabs all edit the same `Buttons.graft` file.

The list on the left shows the entries of the active tab, and selecting an entry in the list selects it in the tab. Each tab remembers its selected entry when you switch between tabs.

The status bar shows the path of the active tab's file, an indicator for unsaved changes, and how many entries the active tab has.

## Managing Files
These commands are in the **File** menu and on the toolbar. Unless noted otherwise, they act on the file of the active tab:

- **New** (`Ctrl+N`): Resets the file to the vanilla StarCraft requirements or buttons.
- **Open...** (`Ctrl+O`): Opens a `.graft` file. Files named like one of the Graft files (such as `Units.graft`) open into that file's tab (`Buttons.graft` opens into **Button Sets**), and any other file opens into the active tab's file.
- **Open Directory...** (`Ctrl+D`): Opens every Graft file found in a folder.
- **Open MPQ...** (`Ctrl+Alt+O`): Opens every Graft file found in the `datreq` folder of an MPQ.
- **Save** (`Ctrl+S`) and **Save As...** (`Ctrl+Alt+S`): Saves the file.
- **Save MPQ...** (`Ctrl+Alt+M`): Saves all six Graft files into the `datreq` folder of an MPQ.
- **Import from TXT...** (`Ctrl+I`): Replaces the file's contents with code from a text file.
- **Export to TXT...** (`Ctrl+E`): Saves the file's contents as code in a text file.
- **Import FireGraft Project...** (`Ctrl+Shift+I`): Lays the requirements and buttons of a FireGraft `.fgp` project over all of the open Graft files.
- **Check for Updates...**: Checks GitHub for a newer version of PyGRAFT and PyMS, and shows the result.
- **Set as Default `*.graft` Editor** (Windows Only, in the **Settings** menu and on the toolbar): Associates `.graft` files with PyGRAFT, so they open in PyGRAFT when double clicked.

PyGRAFT asks to save unsaved changes before they would be lost (when creating or opening over an edited file, or exiting).

## Settings
**Manage Settings...** (`Ctrl+M`, in the **Settings** menu) sets the MPQs to load files from, the theme, and the `stat_txt.tbl`, `unitnames.tbl`, `units.dat`, `upgrades.dat`, `techdata.dat`, and `orders.dat` files used to name the entries. `unitnames.tbl` is optional: it holds the unit names of mods with expanded units, and when it isn't found the unit names come from `stat_txt.tbl`. **Reload Data Files** reloads those files after you change them.

## Command Line
PyGRAFT can convert Graft files to and from text without opening the window:

    PyGRAFT.pyw [options] <input> [output]

- `-d` / `--decompile`: Converts a `.graft` file to text (the default).
- `-c` / `--compile`: Converts text to a `.graft` file.
- `-u` / `--units`, `-g` / `--upgrades`, `-r` / `--research`, `-t` / `--tech`, `-o` / `--orders`, `-b` / `--buttons`: Which Graft file is being converted (`--units` is the default).
- `--gui <file>`: Opens the file in the window instead.

When no output is given, it is the input path with a `.txt` (decompiling) or `.graft` (compiling) extension. Names in the code use the vanilla StarCraft data files.
