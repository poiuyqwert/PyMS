# Weapons Tab
The Weapons tab of [PyDAT](/Help/Programs/PyDAT.md) edits [weapons.dat](/Help/Files/DAT/weapons.dat.md), which contains the settings for all the weapons used by [Units](/Help/Programs/PyDAT/Units.md).

## Damage Properties
The weapons damage Amount and the Bonus added per level of its damage [Upgrade](/Help/Programs/PyDAT/Upgrades.md), the damage Type (Normal, Explosive, Concussive, and so on — how damage scales against unit sizes), the Explosion (what happens on impact, like splash damage or a spell effect), the damage Factor (multiplies the displayed damage, and a value of 2 makes the weapon attack twice like the Goliaths missiles), and the Cooldown between attacks (shown in ticks and in seconds on Fastest game speed).
The Unused field is a leftover technology reference — the game does not use it, it is just a hint to the related [Technology](/Help/Programs/PyDAT/Techdata.md).

## Weapon Display
The Label and Error Msg fields are `stat_txt.tbl` strings: the label names the weapon (shown in tooltips), and the error message is shown when targeting something invalid.
The Behaviour controls how the weapon travels to its target (fly, appear on target, bounce, and so on), and Remove After is how long the weapon lasts if it does not hit a target.
The Graphics field is the [Flingy](/Help/Programs/PyDAT/Flingy.md) used for the weapons projectile, and the Icon is the command card icon — pick it by ID, or click the preview or find button to browse all the icons visually.
The X/Y Offsets set where the projectile spawns relative to the attacker, the Attack Angle is the angle within which the weapon can fire without waiting for the units graphics to turn, and Launch Spin is the angle the weapons sprite spins by after it spawns.

## Weapon Range
The weapons Minimum and Maximum range (in pixels).

## Splash Radii
The Inner, Medium, and Outer splash radii (in pixels) for weapons with splash damage explosions — targets in the inner radius take full damage, with less damage in the outer radii.

## Target Flags
What the weapon is allowed to target: Air, Ground, Mechanical, Organic, Non-Building, Non-Robotic, Terrain, Org. or Mech., and Own (the players own units).

## Used By
The [Used By](/Help/Programs/PyDAT.md#used-by) panel lists the units using the weapon as their ground or air weapon, and the orders using it for targeting.

## See Also
- [PyDAT](/Help/Programs/PyDAT.md)
- [weapons.dat](/Help/Files/DAT/weapons.dat.md)
