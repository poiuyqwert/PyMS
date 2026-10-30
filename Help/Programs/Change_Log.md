# Change Log

# October 30, 2026

## PyMS v2.3.10
- Fixed issue with expanding/collapsing groups in a tree list.

## PyAI v2.9.9
- Added `autosave` AISE command.

# October 29, 2026

## Highlights
- **Support PyMS development.** Every program has a new **Donate** button. PyMS is free and maintained in my spare time, so even a "buy me a coffee" donation helps. [More below](#support-pyms-development).
- **Built-in help, rewritten.** Every program, file format and common task now has its own help page. You can read them in the programs (F1) or online on GitHub, and contributions are welcome.
- **PyMS now runs on Python 3.** Most of PyMS has been rewritten on modern Python 3. It is more reliable, and you no longer need to install the outdated Python 2.7.
- **Official AISE support in PyAI.** You can now edit AISE scripts in the main PyAI, without a separate fork, so you get every other PyMS update too.

## PyMS v2.3.9

### Support PyMS development
Every program now has a **Donate** button (the money icon in the toolbar). It explains a bit about PyMS: it has been built and maintained since 2007, for free and as open source, and it is still actively improved and supported. The button links to my [GitHub Sponsors page](https://github.com/sponsors/poiuyqwert).

If PyMS has saved you time on a mod or map, please consider chipping in. A one-time "buy me a coffee" or "buy me a beer" donation is a nice way to say thanks. A small monthly sponsorship helps keep work like this release going. Any amount is appreciated. If you can't donate, reporting bugs, sharing PyMS and helping other users all help too.

### Help documentation
The help system has been rewritten from the ground up:
- **Every program** has a full help page covering its features, menus and shortcuts. Bigger programs (PyAI, PyBIN, PyDAT, PyICE, PyLO, PySPK, PyTILE, PyTRG) also have sub-pages for their editors and dialogs.
- **File format pages** explain what each StarCraft file is and how it's structured: DAT files, GRP, PCX, palettes, tilesets, TBL, TRG, aiscript.bin, iscript.bin, UI dialog BINs, MPQs and more.
- **Step-by-step tutorials** for common tasks: your first AI script, your first trigger, editing a unit, a GRP, a tileset, a dialog, a font, a palette, game text and more.
- **Reference material**, such as the full PyAI command reference.

Read it in any program with the Help button (F1), or online in the [Help folder on GitHub](https://github.com/poiuyqwert/PyMS/tree/master/Help). It's the same content in both places, and pages link to each other.

**Help wanted:** StarCraft modding knowledge is scattered across old forum posts, wikis and Discord messages. The goal is for PyMS's help to become a reliable single source of truth. If you spot something missing, wrong or unclear, or have knowledge or tutorials to share, please open an issue or pull request on GitHub, or get in touch.

### Python 3
PyMS has moved from Python 2.7, which stopped receiving updates in 2020, to **Python 3** (3.11–3.13 supported; newer versions run with a warning).
- **Much of PyMS has been rewritten.** The file format code, the shared UI and settings, and most programs were reworked with modern, cleaner and more consistent code. Thorough automated tests now cover file loading, saving and round-tripping. The result should be fewer bugs and faster fixes.
- **Easier to install.** You no longer need the old Python 2.7 alongside a modern Python. Just install a current Python 3 and run `python -m pip install -r requirements.txt`.
- **More platforms.** MPQ support now works on Apple Silicon Macs and Linux, and with file paths that contain non-English characters.
- Python 2 is no longer supported. SEMPQ creation has been removed.

### Other PyMS improvements
- **Reworked settings** in every program, including updated settings dialogs.
- **Menus in every program.** Every program now has a menubar listing all its commands and shortcuts, with the same File, Edit, View, Settings and Help layout everywhere.
- **Check for updates any time.** Every program now has a **Check for Updates** toolbar button and **File** menu item, which always shows the result, even when you're up to date or the check fails. Programs still check automatically on launch, like previous versions did.
- **See what's new.** When an update is available, the update message has a **Change Log** button that shows what changed in each new version, without leaving the program.
- **Consistent toolbars.** Toolbar buttons are grouped and ordered the same way in every program, and use the same names as the menus.
- **Unified code editors.** PyAI, PyLO, PyTRG and PyICE now share one syntax highlighting system with customizable colours, and the same Find/Replace dialog, which now closes with Escape.
- **Importing now counts as editing the open file.** Previously, importing a text file could change where Save wrote. In PyLO, PyTRG, PyBIN and PyTBL, saving even overwrote the imported text file with binary data. Now Save keeps targeting the file you opened, and closing after an import asks you to save.
- **Window positions on multiple monitors.** Windows saved on a second monitor (or one left of or above the main monitor) used to be pushed back onto the main screen. Now they reopen where you left them. Positions on monitors that are no longer connected are moved back on-screen.
- **No more window flashing on open.** Windows no longer briefly appear at the wrong size or position.
- **Faster opening of large MPQs and folders.**
- **More detailed error reports.**

## PyAI v2.9.8

### AISE support
[AISE](https://github.com/neivv/aise) is a popular game plugin that extends StarCraft's AI scripting with many new commands and options. Until now, editing AISE scripts meant using a separate fork of PyAI that fell behind the rest of PyMS. **AISE is now officially supported in PyAI**, so you can use one up-to-date PyMS for everything.
- **All AISE commands** are supported, including complex ones like `idle_orders`, with full syntax highlighting, tooltips and help pages.
- **Expanded files.** aiscript.bin is normally limited to 64KB. AISE allows larger "expanded" files, and PyAI can now load and save them. aiscript.bin and bwscript.bin are expanded separately, and only when a file doesn't fit in 64KB, so files stay in the standard format whenever possible.
- **No surprises.** PyAI warns you when you open an AISE file, and before a change would make a file require AISE.
- **New help:** an AISE command reference with every command and its parameters.

### Other PyAI improvements
- **New script compiler and decompiler, with an updated script language**:
  - directives to control compiling
  - unit, upgrade and tech names can be used instead of IDs
  - configurable decompile formatting
  - automatic conversion of scripts written for old PyAI and ASC3
  - clearer compile errors
- **Fix Issues dialog.** It opens when a loaded file has problems, such as broken references or invalid IDs. It suggests fixes and shows a preview of the affected code.
- **Shared code and file size.** Code shared between aiscript.bin and bwscript.bin is detected. Adding a script checks there is room in the file, and offers to expand it if it's full.
- **New tools:** Find Script and string search dialogs, a button in the code editor to insert string IDs, and an improved command line and list import.
- **New help pages:** a full command reference and a "first AI script" tutorial.
- **Go to block.** In the code editor, Ctrl+Click (⌘+Click on macOS) a block name to jump to where it's defined.
- **String highlighting.** The code editor highlights quoted strings, and TBL codes like `<44>` inside them.

## PyBIN v1.0.0
- **Load failures panel.** Images, SMK videos or fonts that fail to load are listed in a panel under the preview, instead of opening one error popup each.
- The widget tree shows each widget's ID, and has a "Simple Names" option that hides formatting characters in names.
- The Widget Editor has a button to browse MPQs for an image.
- **New text export format.** It keeps every flag when you export and re-import a dialog.
- **Fixes:**
  - SMK videos set not to repeat no longer loop forever in the preview.
  - An SMK can no longer be set as an overlay of itself, directly or through a chain of overlays.
  - "Remove Selected" on a group now also removes the widgets inside it. Before, they disappeared from the tree but were still saved.
  - Editing a widget's Top or Height in simple mode calculated Bottom from the wrong values.
  - Resizing a widget by dragging calculated its height incorrectly.
  - Cancelling the widget or SMK editor now throws away your changes instead of keeping them.

## PyDAT v3.0.5
- **Reworked settings dialog**, with Palette, TBL and Other tabs.
- **Fixes:**
  - The icon picker didn't always redraw or highlight the selected icon.
  - An entry list didn't refresh after another DAT it points to changed.
  - Entries pointing to ID 0 were missing from "used by" lookups.
  - You couldn't jump to the last entry.
  - Playing the "None" sound played a different sound.
  - A divide-by-zero crash when calculating AI force values.
  - Entry names ending in "0", "<" or ">" lost those characters.
  - Importing entries accepted negative IDs.
  - Crashes from flingy or icon data with out-of-range IDs, from actions with nothing selected, and from errors during TXT import.
  - MPQ save failures now show the error for each file.

## PyFNT v1.4.0
- The font size prompt asked for "max width" twice. It now asks for width and height.
- After importing a font, Save asks where to save instead of overwriting the previously open file.
- Export showed "exported successfully" even when it failed.

## PyGOT v1.5.0
- Saving after importing a text template asks for a .got location, instead of overwriting the text file.
- New documents no longer start marked as unsaved.
- Fixed a "compatible" typo.

## PyGRP v4.1.4
- **Fixes:**
  - Some BMPs imported with an extra row of pixels (#155).
  - BMP filenames with spaces were treated as part of a frame series.
  - After removing frames, the selection could point at frames that no longer exist.
  - Exporting frames as a single sheet ignored the filename you chose.

## PyICE v2.1.3
- **Go to block.** In the code editor, Ctrl+Click (⌘+Click on macOS) a block name to jump to where it's defined.
- **Fixes:**
  - The previewer's "Overwrite" insertion crashed on lines with nothing after the value.
  - Previewer palettes didn't reload after you changed them in settings.
  - Cached GRP frames were thrown away, which slowed down the preview.
  - Code generators could create invalid or clashing variable names.
  - Math expressions accepted commas.
  - The Enter key wasn't detected on some platforms.

## PyLO v1.9.0
- Imported text is now checked, with an error shown if it's invalid. Before, it was silently treated as an empty file.
- Export now writes the text currently in the editor, including unsaved edits.
- A failed save no longer changes the file you have open.

## PyMPQ v1.2.2
- **Fixes:**
  - The Encrypt setting was ignored when adding files.
  - The selected locale was ignored when saving edited files back into the MPQ.
  - Extracting a file that failed to read wrote stale or empty data.
  - Opening files with Windows-style paths (`\`) failed on macOS and Linux.
  - The "Default" compression setting wasn't applied.
  - Creating or opening an MPQ didn't close the previous one, and closing an MPQ could error.
  - Invalid compression settings could be saved, and the listfile list kept duplicates and reversed its order.
  - The background check for edited files could conflict with cleanup on close.

## PyPAL v1.7.0
- Ctrl+P was bound to both Paste and "Save as StarCraft .pal". Ctrl+P is now Paste, and Save as .pal is Ctrl+Alt+P.
- Converting palettes from the command line works again.

## PyPCX v1.2.1
- Importing a BMP now marks the file as unsaved, so closing asks you to save.
- The preview stacked a new image on every redraw instead of replacing the old one.

## PySPK v1.0.0
- "Move Stars Down" moved stars up.
- Holding Shift while placing a star is now respected, as the preview already showed.
- Importing a BMP now marks the file as unsaved.
- The preview works without StarCraft MPQs configured, because PySPK now bundles the platform palette.

## PyTBL v1.9.0
- **Fixes:**
  - The preview crashed on strings that are a single character, and on some resource icon rows.
  - Find used your regex wrapped in extra wildcards. It now uses the regex exactly as typed.
  - Go To errored on an empty file.

## PyTILE v2.4.1
- **Reworked megatile settings import/export.**
- MPQ and stat_txt choices are now in Settings.
- **Fixes:**
  - "VX4 Expanded" stayed in the status bar after loading a non-expanded tileset.
  - Malformed doodad data shows a clear error instead of crashing.

## PyTRG v2.8.1
- Unit and AI names now come from the stat_txt and aiscript files you configured, instead of always the built-in defaults.
- MPQ settings added.
- Export now shows an error when the file can't be written, instead of crashing.
