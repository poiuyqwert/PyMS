# sprites.dat
`sprites.dat` contains some display settings, like selection circle and health bar settings, for the sprites used by [Flingys](/Help/Files/DAT/flingy.dat.md) and [IScripts](/Help/Files/iscript.bin.md), as well as a reference to an [Image](/Help/Files/DAT/images.dat.md).

Edited by [PyDAT](/Help/Programs/PyDAT.md) on the [Sprites Tab](/Help/Programs/PyDAT/Sprites.md)

## Format
The file has 517 entries, one per sprite ID. Each entry holds the image reference, a visibility flag, and an unused flag. The health bar size, selection circle image, and selection circle offset are only stored for sprite IDs 130 to 516 (the sprites used by selectable units) — see the [Sprites Tab](/Help/Programs/PyDAT/Sprites.md) for the full breakdown.

## References
- [Image](/Help/Files/DAT/images.dat.md)
- Selection circle [Image](/Help/Files/DAT/images.dat.md) (stored as an offset from image ID 561, where the selection circle images start)

## Names
Sprites have no name setting — PyDAT names them after their [Image](/Help/Files/DAT/images.dat.md).

## Expanded
An expanded `sprites.dat` (see [Expanded DAT Files](/Help/Programs/PyDAT.md#expanded-dat-files)) can have at most 65536 entries.
