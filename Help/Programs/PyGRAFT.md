# PyGRAFT
PyGRAFT is a tool used for editing the `.graft` files of the GPTP Graft Hook, a replacement for FireGraft. The Graft Hook loads six files from the `datreq` folder of your mod's MPQ: the requirements for training or building units (`Units.graft`), researching upgrades (`Upgrades.graft`), researching technologies (`Research.graft`), using technologies (`Tech.graft`), and using orders (`Orders.graft`), along with the command card buttons (`Buttons.graft`).

PyGRAFT is in early development: only the **Button Cards**, **Unit Stat Info**, and requirement tabs edit their entries so far. To change button sets, use **Export to TXT**, edit the text, then **Import from TXT**.

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

The list on the left shows the entries of the active tab, and selecting an entry in the list selects it in the tab. The requirement tabs list every entry of their `.dat` file, and entries without a requirements script are greyed out. Each tab remembers its selected entry when you switch between tabs.

The status bar shows the path of the active tab's file, an indicator for unsaved changes, and how many entries the active tab has.

## Button Cards
Each button card picks what the command card shows for its unit (or, for the cards after the units, for groups, builder pages, replays, and so on):

- **Button Set**: The button set the card shows, or **None** for no buttons.
- **Connected Unit**: When units with this card are selected together with the connected unit, the group uses the connected unit's button card instead of the generic group card (such as Kerrigan connected to the Ghost), or **None**. Choose a unit from the dropdown, or type a unit ID in the entry (anything that isn't a unit, or `65535` for **None**, is undone). A card connected to a unit ID past the units that are loaded keeps it, shown as **Unit** followed by its ID.

## Unit Stat Info
Each unit's stat info picks the functions the game uses for that unit's stat panel when it's the only unit selected:

- **Status Func.**: Checks whether what the stat panel shows has changed, so it gets redrawn.
- **Display Func.**: Draws the stat panel.
- **Presets**: Shows a menu of the function pairs most units use (such as **Building**, **Normal Unit**, or **Transport**). Choosing one sets both functions.
- **Unit ID** (under **Debug**): A debug unit ID that the game doesn't use (it defaults to the unit itself). Choose a unit from the dropdown, or type any number in the entry (numbers that aren't a unit show as **Unknown**).

## Requirements
The **Unit Training Reqs.**, **Upgrade Research Reqs.**, **Tech Research Reqs.**, **Tech Usage Reqs.**, and **Order Reqs.** tabs share one editor for the selected entry's requirements script. Every tab has the same editor, but only the commands of its file can be used (for example, `upgrade_level_1` is only for upgrades, and `does_not_have_exit` is only for orders). The editor has two modes, chosen by the tabs at its top: **Builder** (not available yet) and **Script**.

### Script
The **Script** mode edits the selected entry's script as code. The code is only the script's commands, without the `Unit 0:` style header used in exported text, since the script is always for the selected entry. Entries without a script start empty. Hover over a command to see its description, and press `Tab` to complete a command name.

The toolbar above the code has these buttons, whose shortcuts work while editing the code:

- **Apply Changes** (`Ctrl+Return`): Compiles the code into the file's script for the entry, which makes the file edited (save the file to keep the changes). If the code has an error, its line is highlighted and nothing is changed. Applying code without any commands asks whether to remove the entry's script (**Yes**) or keep an empty script (**No**).
- **Revert Changes**: Discards the changes to the code since it was loaded or last applied.
- **Test Code** (`Ctrl+T`): Checks the code for errors without applying it.
- **Find/Replace** (`Ctrl+F`): Finds or replaces text in the code (`F3` finds the next match).
- **Color Settings** (`Ctrl+Alt+C`): Changes the colors of the code, which all of the requirement tabs share, and imports/exports them to share with the other programs (see [Color Settings](/Help/Programs/Syntax_Highlighting.md#color-settings)).

After applying, the code is reloaded from the file, so comments and formatting aren't kept.

Changes to the code must be applied or discarded before leaving them. Selecting another entry, switching tabs or modes, or anything else that would reload the code (such as **New**, **Open...**, **Import from TXT...**, **Reload Data Files**, or exiting) asks whether to apply the changes first: **Yes** applies them (and stays if they have an error), **No** discards them, and **Cancel** stays. Saving (**Save**, **Save As...**, **Save MPQ...**, or **Export to TXT...**) also asks whether to apply the changes first, where **No** saves the file without them and keeps them in the editor.

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
