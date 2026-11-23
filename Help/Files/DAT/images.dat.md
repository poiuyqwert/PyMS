# images.dat
`images.dat` contains the graphics settings for the images used by [Sprites](/Help/Files/DAT/sprites.dat.md) and [IScripts](/Help/Files/iscript.bin.md), and references to other data related to the image.

Edited by [PyDAT](/Help/Programs/PyDAT.md) on the [Images Tab](/Help/Programs/PyDAT/Images.md)

## Format
The file has 999 entries, one per image ID. Each entry holds the GRP and IScript references, drawing flags (graphics turns, clickable, use full iscript, draw if cloaked), the drawing function and color remapping, and the overlay references — see the [Images Tab](/Help/Programs/PyDAT/Images.md) for the full breakdown.

## References
- A reference to a string in [images.tbl](/Help/Files/TBL.md#imagestbl), which contains the path (under `unit\`) in the [MPQ's](/Help/Files/MPQ.md) for the [GRP](/Help/Files/GRP.md) used by the image. The reference counts from 1, and 0 means no file
- Which [IScript](/Help/Files/iscript.bin.md) entry controls the image (an ID from the iscript.bin header, not a position)
- The [overlays](/Help/Files/LO.md) used (the attack, damage, special, landing dust, lift-off dust, and shield overlays, each also a reference to a path string in [images.tbl](/Help/Files/TBL.md#imagestbl), counting from 1 with 0 for none)

The game loads the GRP and overlay files once, when it starts. Outside Brood War it only loads them for images 0 to 754, so the higher images have no graphics there.

## Names
Images have no name setting — PyDAT names them after their [GRP](/Help/Files/GRP.md) file path.

## Expanded
An expanded `images.dat` (see [Expanded DAT Files](/Help/Programs/PyDAT.md#expanded-dat-files)) can have at most 65536 entries.
