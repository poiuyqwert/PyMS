# Widgets
A dialog is made up of widgets: the root Dialog widget, plus a widget for each control on the screen. In [PyBIN](/Help/Programs/PyBIN.md) the widgets are shown in the widget tree on the left of the main window, and rendered on the canvas on the right. Double clicking a widget (in the tree or on the canvas) opens it in the [Widget Editor](/Help/Programs/PyBIN/Widget_Editor.md).

## Widget Types
- **Dialog**: The root widget. Every file has exactly one, it can't be removed, and every other widget is (directly or indirectly) inside it. When the **Dialog** preview setting is on it draws the standard dialog frame art.
- **Default Button**, **Button**, and **Highlight Button**: Clickable buttons. A Default Button is activated by `Enter` in the game, and Highlight Buttons are the type normally used with [SMK animations](/Help/Programs/PyBIN/Widget_Editor.md#smk-animations) for animated menu art.
- **Option Button** and **CheckBox**: A radio button and a checkbox.
- **Image**: Displays a [PCX](/Help/Files/PCX.md) image — the widgets string is the images file path inside the MPQs.
- **Slider**: A draggable slider bar.
- **TextBox**: A text entry field.
- **Label (Left Align)**, **Label (Center Align)**, and **Label (Right Align)**: Plain text labels.
- **ListBox** and **ComboBox**: A scrollable list and a dropdown list.
- **Unknown**: An unidentified widget type found in some of the games files.
- **HTML**: Displays web content. This type only exists in StarCraft: Remastered — adding one turns the file into a Remastered file (see [UI BIN](/Help/Files/UI_BIN.md#legacy-and-remastered-files)).
- **Group**: Not a real widget — an editor-only folder for organizing widgets in the tree. Moving a group on the canvas moves all the widgets inside it. Groups are not saved into the `.bin` file, so they are lost when the file is closed.

## Adding and Removing Widgets
**Add Widget** on the widgets toolbar opens a menu of the types above. The new widget is created in the middle of the selected group (or next to the selected widget), and can then be positioned and edited. Adding an HTML widget enables SC:R mode for the file.
**Remove Selected** removes the selected widget or group (move any widgets you want to keep out of a group before removing it). The root Dialog can't be removed.

## Tree Order and Z-Order
Widgets are drawn in the order they appear in the tree, so widgets lower in the tree are drawn on top of the ones above them. Use **Move Widget Up** and **Move Widget Down** on the widgets toolbar to reorder the selected widget among its siblings.
You can also drag and drop widgets in the tree: drop a widget onto a group to move it into that group, or drop it between siblings to reorder it. The root Dialog can't be dragged, and a group can't be dropped into itself.

## Editing on the Canvas
- **Select**: Click a widget to select it (shown with a red outline, and highlighted in the tree). Clicking overlapping widgets selects the deepest one under the mouse; hold `Ctrl` to keep targeting the currently selected widget or group instead of its children.
- **Move**: Drag a selected widget to move it. Moving a group or the Dialog moves everything inside it. Movement is kept within the 640x480 window.
- **Resize**: Drag a widgets edge or corner to resize it (the mouse cursor changes when over an edge). The widgets responsive hit-box is adjusted to stay within the new size.
- **Edit**: Double click a widget to open it in the [Widget Editor](/Help/Programs/PyBIN/Widget_Editor.md). `Ctrl` double click prefers the currently selected widget, like with selecting.

The **Bounds** preview settings draw outline boxes around widgets, groups, text, and responsive hit-boxes, which makes widgets with no visible art (like unloaded images) much easier to find and manipulate.

## See Also
- [PyBIN](/Help/Programs/PyBIN.md)
- [Widget Editor](/Help/Programs/PyBIN/Widget_Editor.md)
- [UI BIN](/Help/Files/UI_BIN.md)
