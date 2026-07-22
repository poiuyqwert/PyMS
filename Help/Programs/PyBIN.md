# PyBIN
PyBIN is a tool used for editing UI menus/dialogs, contained in various [UI .bin](/Help/Files/UI_BIN.md) files. It shows a live preview of the dialog on a 640x480 canvas, rendered with the games own art, fonts, and videos loaded from your [MPQs](/Help/Files/MPQ.md).
A dialog is a tree of widgets (buttons, labels, images, sliders, and so on). See [Widgets](/Help/Programs/PyBIN/Widgets.md) for the widget types and how to arrange them, and the [Widget Editor](/Help/Programs/PyBIN/Widget_Editor.md) for editing a widgets properties. If you are new to PyBIN, start with the [Editing a Dialog](/Help/Tutorials/Editing_a_Dialog.md) tutorial.
PyBIN supports both legacy (pre-Remastered) and StarCraft: Remastered dialog files (see [UI BIN](/Help/Files/UI_BIN.md#legacy-and-remastered-files) for the differences). The **SC:R** indicator above the widget tree shows whether the loaded file is in the Remastered format — it is enabled automatically when you open a Remastered file or use Remastered-only widgets.

## Main Window
The left side of the window shows the widget tree — the dialogs widgets in their draw order, including any editor-only groups you have made to organize them. Each widget is listed with its text, control ID, and type. Selecting a widget in the tree also selects it on the canvas.
The toolbar under the widget tree has the widget editing actions:

- **Add Widget**: Adds a new widget (or group), chosen from a menu of the widget types. See [Adding and Removing Widgets](/Help/Programs/PyBIN/Widgets.md#adding-and-removing-widgets).
- **Remove Selected**: Removes the selected widget or group (the root Dialog can't be removed).
- **Edit Widget**: Opens the selected widget in the [Widget Editor](/Help/Programs/PyBIN/Widget_Editor.md) (also `Enter`, or double clicking the widget in the tree or on the canvas).
- **Toggle Preview Settings**: Shows/hides the [Preview Settings](#preview-settings) panel.
- **Move Widget Up** and **Move Widget Down**: Reorders the selected widget among its siblings, which also changes its draw order (see [Tree Order and Z-Order](/Help/Programs/PyBIN/Widgets.md#tree-order-and-z-order)).

The right side of the window is the canvas: a 640x480 preview of the dialog where you can select, move, and resize widgets directly (see [Editing on the Canvas](/Help/Programs/PyBIN/Widgets.md#editing-on-the-canvas)).
Below the canvas is a collapsible **Failed Assets** panel, which lists any game assets (images, fonts, videos, backgrounds) that could not be loaded from your MPQs, along with which widget uses each one. If assets are failing to load, check your MPQ list in [Manage Settings](#program-settings).
The status bar shows the general status, an indicator for unsaved changes, and the widget the mouse is over on the canvas.

## Managing Files
- **New** (`Ctrl+N`): Creates a new dialog, containing just an empty 640x480 Dialog widget.
- **Open** (`Ctrl+O`): Opens an existing `.bin` dialog file. The format (legacy or Remastered) is detected automatically.
- **Import from TXT** (`Ctrl+I`): Loads a dialog from the text format produced by **Export to TXT**.
- **Save** (`Ctrl+S`) and **Save As** (`Ctrl+Alt+A`): Saves the dialog to a `.bin` file. The file is saved in the Remastered format if it was loaded as one or uses Remastered-only features, and in the legacy format otherwise.
- **Export to TXT** (`Ctrl+E`): Saves the dialog as an editable text file listing every widget and SMK with its properties. Exporting, editing the text, and re-importing can be an easy way to make bulk changes.
- **Close** (`Ctrl+W`): Closes the loaded file.
- **Set as default .bin editor** (Windows Only): Associates `.bin` files with PyBIN, so they open in PyBIN when double clicked.

## Preview Settings
The Preview Settings panel below the widget tree controls what the canvas renders. All the settings are remembered between sessions.

- **Widget**: Toggles rendering of widget **Images**, **Text**, and **SMKs**, whether **Hidden** widgets (with their Visible flag off) are still drawn, and whether the **Dialog** widget draws its frame art. **Simple Names** simplifies the widget names shown in the tree (hiding text formatting codes).
- **SMKs**: **Animated** plays SMK videos on the canvas (at the games ~15fps), and **Hovers** also shows SMKs that are flagged to only show on mouse hover.
- **Bounds**: Draws outline boxes for **Widgets** (blue), **Groups** (grey), **Text** (white), and the **Responsive** mouse hit-box (green), so you can see widgets that have no visible art.
- **Theme**: Chooses which of the games UI themes (Main Menu, Campaign, the mission briefings, the victory/defeat screens, or General) supplies the button/checkbox/slider art, dialog frame art, and title font used by the preview. **Background** also draws that themes background image behind the dialog. Since a `.bin` file doesn't record which screen it belongs to, pick the theme matching the file you are editing (see the file list in [UI BIN](/Help/Files/UI_BIN.md#dialog-files)).

## Program Settings
**Manage Settings** (`Ctrl+M`) opens the settings dialog. It also opens automatically at startup if any of the preview files fail to load.

- **MPQ Settings**: Manages the list of MPQs that game assets are loaded from (usually your StarCraft MPQs and/or your mods MPQ).
- **Preview Settings**: Chooses the files used to render text on the canvas: the `tfontgam.pcx` text color palette and the `font10.fnt`, `font14.fnt`, `font16.fnt`, and `font16x.fnt` [fonts](/Help/Files/FNT.md). By default these load from your MPQs.
- **Theme**: Changes the PyMS window [theme](/Help/Programs/Themes.md).

## Command Line
PyBIN has no command line workflow, but you can open a file with the GUI from the command line:

```
PyBIN --gui path/to/file.bin
```

## See Also
- [Widgets](/Help/Programs/PyBIN/Widgets.md)
- [Widget Editor](/Help/Programs/PyBIN/Widget_Editor.md)
- [UI BIN](/Help/Files/UI_BIN.md)
- [Editing a Dialog](/Help/Tutorials/Editing_a_Dialog.md)
