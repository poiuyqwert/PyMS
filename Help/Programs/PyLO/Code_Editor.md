# Code Editor
The Code Editor is where you write and edit the offset source code that [PyLO](/Help/Programs/PyLO.md) decompiles from (and compiles back into) [.lo?](/Help/Files/LO.md) files.

## LO Source Syntax
The source code is a list of frames, written in order. Each frame starts with a `Frame:` header, followed by one `(x, y)` offset per overlay:

```
Frame:
    (0, 0)
    (-5, 12)

Frame:
    (2, -1)
    (7, 3)
```

- Each frame in the code matches one frame of the [GRP](/Help/Files/GRP.md) graphic the file attaches to, and each of its offsets positions one overlay for that frame.
- Offsets are measured in pixels from the center of the graphic, and each coordinate must be in the range `-128` to `127`.
- Every frame must have the same amount of offsets.
- A `#` starts a comment, which runs to the end of the line.

## Editor Features
- **Syntax highlighting**: Comments, `Frame:` headers, numbers, and operators each have their own configurable style — customize them with **Color Settings** (`Ctrl+Alt+C`).
- **Autocomplete**: Press `Tab` to complete the word being typed (`Frame` is the only keyword).
- **Offset tooltip**: Selecting an offset and hovering over the selection shows a small diagram of the offset — a green crosshair marks the center of the graphic, and a blue crosshair marks the offset position.
- **Comment toggle** (`Ctrl+/`): Comments/uncomments the current line or selected lines.
- **Indent** (`Ctrl+]`) and **Dedent** (`Ctrl+[` or `Shift+Tab`): Adjusts the indentation of the current line or selected lines.
- **Jump to frame** (`Alt+Up`/`Alt+Down`): Moves the cursor to the previous/next `Frame:` header.
- **Jump to error** (`Alt+Left`/`Alt+Right`): Moves the cursor to the previous/next highlighted error or warning.

## Test Code
**Test Code** (`Ctrl+T`) compiles the source code without saving it. If there is a problem the editor scrolls to and highlights the offending line (along with any warning lines), otherwise you are told the code compiles cleanly.

## Find and Replace
**Find/Replace** (`Ctrl+F`) opens the Find/Replace dialog to search (and optionally replace) text in the code. `F3` repeats the last find.

## See Also
- [PyLO](/Help/Programs/PyLO.md)
- [Previewer](/Help/Programs/PyLO/Previewer.md)
- [LO?](/Help/Files/LO.md)
