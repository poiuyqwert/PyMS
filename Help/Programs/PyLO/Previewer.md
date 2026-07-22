# Previewer
The Previewer draws the offset under the cursor in the [Code Editor](/Help/Programs/PyLO/Code_Editor.md) onto real game graphics, and lets you adjust it by dragging. Place the cursor on an offset line and the preview shows that offset on its frame; the preview is empty while the cursor is anywhere else.

## Preview Graphics
The preview composites two [GRP](/Help/Files/GRP.md) graphics, drawn with the unit palette:

- **Base GRP**: The graphic the `.lo?` file attaches to (a unit, for example), drawn at the center of the preview.
- **Overlay GRP**: The graphic positioned by the offsets (an attack flash or shield effect, for example), drawn at the offset under the cursor.

The two file fields under the preview choose the graphics, either from a file on disk or from your [MPQs](/Help/Files/MPQ.md) (manage the MPQ list with **Manage MPQ Settings** (`Ctrl+M`)). The **Use base GRP** and **Use overlay GRP** checkboxes toggle each graphic — when a graphic is off, a crosshair is drawn in its place instead (green for the base graphic's center, blue for the offset position), which can be easier to judge exact positions with.

## Frames
- **Base Frame**: Follows the cursor in the editor — the preview shows the frame of the Base GRP matching the `Frame:` block the cursor is inside.
- **Overlay Frame**: Chosen with the scrollbar under the preview, so you can line up the correct facing/animation frame of the overlay graphic.

The labels above the preview show the current and total frames of each graphic.

## Adjusting Offsets
With the cursor on an offset line, click and drag on the preview to move the overlay around. When you release the mouse button, the new `(x, y)` values are written back into that line of the code (coordinates are clamped to the valid `-128` to `127` range). The change is a single undo step, so `Ctrl+Z` reverts it.

## See Also
- [PyLO](/Help/Programs/PyLO.md)
- [Code Editor](/Help/Programs/PyLO/Code_Editor.md)
- [GRP](/Help/Files/GRP.md)
- [MPQ](/Help/Files/MPQ.md)
