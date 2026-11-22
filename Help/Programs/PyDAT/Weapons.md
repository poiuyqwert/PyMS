# Weapons Tab
The Weapons tab of [PyDAT](/Help/Programs/PyDAT.md) edits [weapons.dat](/Help/Files/DAT/weapons.dat.md), which contains the settings for all the weapons used by [Units](/Help/Programs/PyDAT/Units.md).

## Damage Properties
The weapons damage Amount and the Bonus added per level of its damage [Upgrade](/Help/Programs/PyDAT/Upgrades.md), the damage Type (Normal, Explosive, Concussive, Ignore Armor and Independent — how damage scales against unit sizes, and whether armor applies), the Explosion (what happens on impact, like splash damage or a spell effect; Mind Control, Feedback and Unknown stop the game with a fatal error), the damage Factor (multiplies the displayed damage; only a value of 2 does anything in the game, firing a second bullet with each attack like the Goliaths missiles), and the Cooldown between attacks (shown in ticks and in seconds on Fastest game speed; the game keeps the slowed or sped-up value between 5 and 250 and adds a random -1 to +2).
The Unused field is a leftover technology reference — neither the game nor StarEdit uses it, it is just a hint to the related [Technology](/Help/Programs/PyDAT/Techdata.md).
Upgrade 60 is used for weapons no upgrade affects.

## Weapon Display
The Label and Error Msg fields are `stat_txt.tbl` strings: the label names the weapon (shown in tooltips), and the error message is shown when targeting something invalid.
The Behaviour controls how the weapon travels to its target (fly, appear on target, bounce, and so on), and Remove After is the bullet's lifetime in frames (a flying bullet is removed when it arrives or when this runs out; a Persist on Target Site bullet, like Psionic Storm, deals its damage every 7 frames for this long).
The Graphics field is the [Flingy](/Help/Programs/PyDAT/Flingy.md) used for the weapons projectile (0 fires no bullet, as for melee weapons), and the Icon is the weapon icon in a selected units status panel — pick it by ID, or click the preview or find button to browse all the icons visually.
The Forward and Up Offsets set how many pixels in front of and above the attacker the projectile spawns, the Attack Angle is the angle (in 256ths of a turn; 128 or more means any direction) within which the weapon can fire without waiting for the unit to turn, and Launch Spin turns the bullets starting direction by this angle, left and right in turn, which makes homing missiles curve.

## Weapon Range
The weapons Minimum and Maximum range (in pixels, measured between the edges of the attackers and targets unit dimensions). A Minimum of 0 means no minimum. Range upgrades and Bunkers add to the Maximum, depending on the unit type.

## Splash Radii
The Inner, Medium, and Outer splash radii (in pixels, from the bullet to the edge of a unit) for weapons with splash damage explosions — units in the inner radius take full damage, in the medium radius half and in the outer radius a quarter. Burrowed units are only hit in the inner radius. With Splash (Air), the target takes full damage if it is in the inner radius, otherwise one random enemy in the outer radius does, and every other unit takes half or a quarter.

## Target Flags
What the weapon is allowed to target. Air and Ground say which units it can hit at all; Mechanical, Organic, Non-Building, Non-Robotic, Org. or Mech., and Own (the players own units) are extra conditions the target must all meet. Terrain allows aiming at a spot on the ground. The flags also decide which units a splash hurts.

## Used By
The [Used By](/Help/Programs/PyDAT.md#used-by) panel lists the units using the weapon as their ground or air weapon, and the orders using it for targeting.

## See Also
- [PyDAT](/Help/Programs/PyDAT.md)
- [weapons.dat](/Help/Files/DAT/weapons.dat.md)
