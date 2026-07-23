# PySPK
PySPK is a tool used for editing parallax [.spk](/Help/Files/SPK.md) files, which contain the scrolling star background displayed behind the terrain on the Space Platform [tileset](/Help/Files/Tilesets/Tilesets.md). A parallax is made up of layers of stars that each scroll at a different speed as the screen moves, creating an illusion of depth. If you are new to parallax editing, start with the [Editing a Parallax](/Help/Tutorials/Editing_a_Parallax.md) tutorial.
The main parts of the editor each have their own page:

- [Layers](/Help/Programs/PySPK/Layers.md): The parallax layers and the Layers panel
- [Palette Tab](/Help/Programs/PySPK/Palette_Tab.md): The library of star images that can be placed
- [Stars Tab](/Help/Programs/PySPK/Stars_Tab.md): The list of stars placed on the layers

## Main Window
The toolbar at the top holds the file actions and settings. Below it, the left side of the window has the [Layers](/Help/Programs/PySPK/Layers.md) panel and the [Palette](/Help/Programs/PySPK/Palette_Tab.md) and [Stars](/Help/Programs/PySPK/Stars_Tab.md) tabs, and the rest of the window is the canvas where you place and edit stars.
The canvas shows a single 648x488 tile of the parallax — in the game each layer repeats to cover the whole map, which you can see in the [Preview](#preview).
The status bar shows status messages, an indicator for unsaved changes, and how many stars are selected.

## Managing Files
- **New** (`Ctrl+N`): Creates a new, empty parallax. It starts with no layers, so [add a layer](/Help/Programs/PySPK/Layers.md) before drawing.
- **Open** (`Ctrl+O`): Opens a `.spk` file. The first layer and first star image are selected automatically.
- **Import from BMP** (`Ctrl+I`): Builds a whole parallax from an 8-bit [.bmp](/Help/Files/BMP.md) file. You are asked how many layers the BMP contains — the image is cut into that many equal height horizontal bands, top to bottom, one band per layer, so the image height must divide evenly by the layer count. Each connected group of non-black pixels in a band becomes a star, and identical shapes automatically share a single star image.
- **Save** (`Ctrl+S`) and **Save As** (`Ctrl+Alt+A`): Saves the parallax to a `.spk` file.
- **Export to BMP** (`Ctrl+E`): Saves the parallax as an 8-bit BMP with the layers stacked vertically — the same arrangement **Import from BMP** expects, so you can export a parallax, edit the image in a paint program, and import it back.
- **Close** (`Ctrl+W`): Closes the parallax.
- **Set as default `.spk` editor** (Windows Only): Associates `.spk` files with PySPK, so they open in PySPK when double clicked.

PySPK asks to save unsaved changes before they would be lost (when creating, opening, or importing over the open file, closing it, or exiting).

## Editing Stars
Stars are edited on the canvas using three tools, switched with the buttons on the [Palette](/Help/Programs/PySPK/Palette_Tab.md) and [Stars](/Help/Programs/PySPK/Stars_Tab.md) tabs or their shortcut keys:

- **Select** (`M`): Click a star, or drag a box around stars, to select them. A plain click replaces the selection, while holding `Ctrl` or `Shift` adds to it. Stars on locked [layers](/Help/Programs/PySPK/Layers.md) can not be selected.
- **Move** (`V`): Drag to move the selected stars.
- **Draw** (`P`): Click to place the star image chosen on the [Palette Tab](/Help/Programs/PySPK/Palette_Tab.md) onto the active layer, centered on the cursor (a preview of the star follows the cursor). If the active layer is hidden, drawing on it makes it visible again, and if it is locked nothing is drawn.

With any tool, the arrow keys nudge the selected stars 1 pixel at a time, and `Delete` or `Backspace` deletes them (after confirming).

## Preview
**Preview** (`Ctrl+L`) opens the Parallax Preview window, which shows the parallax the way the game displays it: a 640x480 view that scrolls around a full size (256x256 tile) map, with every layer repeating and scrolling at its own speed. Scroll with the scrollbars, the arrow keys, or the mouse wheel (hold `Shift` to scroll horizontally with the wheel) and watch the layers drift apart to check the depth effect.

## Settings
**Manage Settings** (`Ctrl+M`) opens the settings dialog, which also opens by itself at startup if the palette fails to load:

- **MPQ Settings**: Manages the list of [MPQs](/Help/Files/MPQ.md) that game data is loaded from (usually your StarCraft MPQs and/or your mods MPQ).
- **Preview Settings**: Chooses the `platform.wpe` [palette](/Help/Files/Palettes.md) used to display the stars in color. By default it is loaded from `tileset\platform.wpe` in your MPQs.
- **Theme**: Changes the PyMS window [theme](/Help/Programs/Themes.md).

## See Also
- [Layers](/Help/Programs/PySPK/Layers.md)
- [Palette Tab](/Help/Programs/PySPK/Palette_Tab.md)
- [Stars Tab](/Help/Programs/PySPK/Stars_Tab.md)
- [Editing a Parallax](/Help/Tutorials/Editing_a_Parallax.md)
- [SPK](/Help/Files/SPK.md)
- [BMP](/Help/Files/BMP.md)
