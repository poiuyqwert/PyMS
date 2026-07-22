# Editing Offsets
This tutorial walks through editing overlay offsets with [PyLO](/Help/Programs/PyLO.md) — from extracting a [.lo?](/Help/Files/LO.md) file, to adjusting its offsets and getting it into your mod. The example edits the Siege Tank turret's attack overlay, which positions where its shots come from.

## Getting a LO File
1. Extract a `.lo?` file from your [MPQs](/Help/Files/MPQ.md) with [PyMPQ](/Help/Programs/PyMPQ.md) — for example the siege mode turret's attack overlay at `unit\terran\stankt.loa`.
2. Open the extracted file in PyLO with **Open** (`Ctrl+O`) — the offsets are decompiled into the editor as text source code (see [LO Source Syntax](/Help/Programs/PyLO/Code_Editor.md#lo-source-syntax)). Each `Frame:` block holds the offsets for one frame of the unit's graphics.

## Setting Up the Previewer
1. Check **Use base GRP**, and set the **Base GRP** field (under the preview) to the [GRP](/Help/Files/GRP.md) the offsets attach to — for this example, the siege mode turret at `unit\terran\stankt.grp`. The file can be picked directly out of your MPQs.
2. Check **Use overlay GRP** and choose a graphic to draw at the offset. For judging exact positions it can be easier to leave this unchecked — a blue crosshair is drawn at the offset instead.

## Adjusting the Offsets
1. Click on an offset line in the editor. The [Previewer](/Help/Programs/PyLO/Previewer.md) shows the matching frame of the base graphic, with the overlay (or crosshair) drawn at that offset.
2. Drag the overlay around the preview to move it — releasing the mouse writes the new `(x, y)` values back into the code. You can also simply type new values.
3. Repeat for the other frames — `Alt+Up` and `Alt+Down` jump between the `Frame:` blocks, and the base graphic follows along in the preview.

## Testing and Saving
1. Press **Test Code** (`Ctrl+T`) to check the code compiles — any problem lines are highlighted in the editor.
2. Save your `.lo?` file with **Save** (`Ctrl+S`) or **Save As** (`Ctrl+Alt+A`).

## Using It In the Game
To use the edited offsets in the game they need to be in the MPQ your mod loads, at their original path. Use [PyMPQ](/Help/Programs/PyMPQ.md) to add the saved file to your mods MPQ (for example at `unit\terran\stankt.loa`).

## See Also
- [PyLO](/Help/Programs/PyLO.md)
- [LO?](/Help/Files/LO.md)
- [PyMPQ](/Help/Programs/PyMPQ.md)
- [MPQ](/Help/Files/MPQ.md)
