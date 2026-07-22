# Editing a Dialog
This tutorial walks through editing one of the games menus with [PyBIN](/Help/Programs/PyBIN.md) — from setting up the game files, to changing widgets and saving your edited dialog. It uses the Main Menu (`glumain.bin`) as the example, but the steps are the same for any [UI .bin](/Help/Files/UI_BIN.md) file.

## Setting Up PyBIN
PyBIN renders its preview using the games own art and fonts, loaded from your [MPQs](/Help/Files/MPQ.md), so the first step is to point it at them:

1. Open PyBIN and press **Manage Settings** (`Ctrl+M`). This dialog also opens by itself on startup if any files failed to load.
2. In the **MPQ Settings** tab, add your StarCraft MPQs (for example `StarDat.mpq`, `BrooDat.mpq`, and `patch_rt.mpq` from your StarCraft folder), plus your mods MPQ if you have one.
3. The **Preview Settings** tab chooses the fonts and text color palette used to render text. The defaults load from the MPQs you just added, so you shouldn't need to change anything.
4. Press **Ok**. If the **Failed Assets** panel below the canvas reports missing files later on, come back here and check your MPQ list.

## Opening a Dialog
The games dialogs live in the `rez` folder of its MPQs, so you need to extract one to edit it:

1. Use [PyMPQ](/Help/Programs/PyMPQ.md) to open one of your MPQs (`glumain.bin` is in `StarDat.mpq`) and extract `rez\glumain.bin` to a working folder.
2. In PyBIN, press **Open** (`Ctrl+O`) and open the extracted file. The widget tree fills with the Main Menus widgets, and the canvas shows a preview.

You could instead start a brand new dialog with **New** (`Ctrl+N`), but editing an existing one is an easier introduction.

## Previewing It Properly
The canvas probably looks sparse at first — most menu art comes from theme assets and SMK animations that are not all shown by default:

1. Open the **Preview Settings** panel under the widget tree (the arrow button on the widgets toolbar toggles it).
2. In the **Theme** dropdown pick `Main Menu (glue\palmm\)`, and check **Background** to draw the menus background art. When editing a different file, pick the theme matching its screen (see the file list in [UI BIN](/Help/Files/UI_BIN.md#dialog-files)).
3. In the **SMKs** group check **Animated** to play the menus video animations, and **Hovers** to also show the ones that normally only appear on mouse hover.
4. Try the **Bounds** checkboxes — the colored outline boxes make it much easier to find widgets with no visible art.

## Making Changes
1. Click a widget on the canvas — say one of the menu buttons. It gets a red selection outline, and is highlighted in the widget tree. Where widgets overlap, clicking selects the deepest widget under the mouse, and holding `Ctrl` keeps targeting the selected one instead of its children.
2. Drag the widget to move it, or drag its edges to resize it. The status bar shows which widget the mouse is over.
3. Double click the widget to open the [Widget Editor](/Help/Programs/PyBIN/Widget_Editor.md). Change its **Text** and press **Update Preview** to see the result without closing the editor, then **Ok** to apply (or close the editor to discard).
4. Add something new: press **Add Widget** on the widgets toolbar and pick a type from the menu — for example a **Label (Center Align)**. The new widget appears in the middle of the dialog, ready to be moved and edited. See [Widgets](/Help/Programs/PyBIN/Widgets.md) for the widget types.
5. **Save** (`Ctrl+S`) when you are happy with your changes.

## Using It In the Game
To see your edited dialog in the game, use [PyMPQ](/Help/Programs/PyMPQ.md) to add the edited file into the MPQ your mod loads, at its original path (`rez\glumain.bin`). The next time the game loads that screen, it uses your dialog.

## See Also
- [PyBIN](/Help/Programs/PyBIN.md)
- [Widgets](/Help/Programs/PyBIN/Widgets.md)
- [Widget Editor](/Help/Programs/PyBIN/Widget_Editor.md)
- [UI BIN](/Help/Files/UI_BIN.md)
