# Flingy Tab
The Flingy tab of [PyDAT](/Help/Programs/PyDAT.md) edits [flingy.dat](/Help/Files/DAT/flingy.dat.md), which controls the movement of the games graphical objects — every [Unit](/Help/Programs/PyDAT/Units.md) and [Weapon](/Help/Programs/PyDAT/Weapons.md) projectile has a flingy.

## Flingy Properties
- **Sprite**: The [Sprite](/Help/Programs/PyDAT/Sprites.md) the flingy displays.
- **Top Speed**: The maximum movement speed in 1/256 pixels per frame, shown as the raw value and converted to pixels per frame.
- **Acceleration**: How much the speed changes each frame when speeding up or braking, in 1/256 pixels per frame.
- **Halt Distance**: The distance from the target, in 1/256 pixels, at which the flingy starts braking, shown as the raw value and converted to pixels. It is only a stored shortcut for speed² ÷ (2 × acceleration), used while the flingy moves at exactly its Top Speed and Acceleration.
- **Turn Rate**: How far the flingy can turn each frame, in 1/256 of a full turn. Keep it between 1 and 127.
- **Move Control**: How movement is controlled — by the flingy.dat values, by the flingy.dat values without braking (bullets, and some units), or by the [IScript](/Help/Files/iscript.bin.md).
- **Unused**: Never read by the game.

Acceleration and Halt Distance are not used under Iscript.bin control, and Halt Distance is only used by "Flingy.dat Control". Under Iscript.bin control Top Speed is only a starting value (the game replaces it from the unit's walking animation), but the Turn Rate is still used.

## Used By
The [Used By](/Help/Programs/PyDAT.md#used-by) panel lists the units and weapons using the flingy as their graphics.

## See Also
- [PyDAT](/Help/Programs/PyDAT.md)
- [flingy.dat](/Help/Files/DAT/flingy.dat.md)
