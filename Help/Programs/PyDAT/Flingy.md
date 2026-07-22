# Flingy Tab
The Flingy tab of [PyDAT](/Help/Programs/PyDAT.md) edits [flingy.dat](/Help/Files/DAT/flingy.dat.md), which controls the movement of the games graphical objects — every [Unit](/Help/Programs/PyDAT/Units.md) and [Weapon](/Help/Programs/PyDAT/Weapons.md) projectile has a flingy.

## Flingy Properties
- **Sprite**: The [Sprite](/Help/Programs/PyDAT/Sprites.md) the flingy displays.
- **Top Speed**: The maximum movement speed, shown as the raw value and converted to pixels per frame.
- **Acceleration**: How quickly the flingy reaches its top speed.
- **Halt Distance**: How far the flingy keeps moving while stopping, shown as the raw value and converted to pixels.
- **Turn Radius**: How quickly the flingy can turn.
- **Move Control**: How movement is controlled — by the flingy.dat values, by the [IScript](/Help/Files/iscript.bin.md), or partially controlled.
- **IScript Mask**: Unused by the game.

Top Speed, Acceleration, Halt Distance, and Turn Radius only apply when the Move Control uses the flingy.dat values.

## Used By
The [Used By](/Help/Programs/PyDAT.md#used-by) panel lists the units and weapons using the flingy as their graphics.

## See Also
- [PyDAT](/Help/Programs/PyDAT.md)
- [flingy.dat](/Help/Files/DAT/flingy.dat.md)
