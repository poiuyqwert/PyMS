# flingy.dat
`flingy.dat` contains the movement settings for things like [Units](/Help/Files/DAT/units.dat.md), [Weapons](/Help/Files/DAT/weapons.dat.md) and [IScripts](/Help/Files/iscript.bin.md), as well as a reference to a [Sprite](/Help/Files/DAT/sprites.dat.md). These movement settings may not all be used if the "Move Control" setting is not set to "Flingy.dat control" (for example "Iscript.bin control" means the [IScript](/Help/Files/iscript.bin.md) Entry of the [Image](/Help/Files/DAT/images.dat.md) referenced by the flingy's [Sprite](/Help/Files/DAT/sprites.dat.md) will control the movement).

Edited by [PyDAT](/Help/Programs/PyDAT.md) on the [Flingy Tab](/Help/Programs/PyDAT/Flingy.md)

## Format
The file has 209 entries, one per flingy ID. Each entry holds the sprite reference, top speed, acceleration, halt distance, turn radius, movement control, and an unused value — see the [Flingy Tab](/Help/Programs/PyDAT/Flingy.md) for the full breakdown.

## References
- [Sprite](/Help/Files/DAT/sprites.dat.md)

## Names
Flingies have no name setting — PyDAT names them after the [Image](/Help/Files/DAT/images.dat.md) displayed by their sprite.

## Expanded
An expanded `flingy.dat` (see [Expanded DAT Files](/Help/Programs/PyDAT.md#expanded-dat-files)) can have at most 65536 entries.
