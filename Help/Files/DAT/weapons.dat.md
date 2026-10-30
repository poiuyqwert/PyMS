# weapons.dat
`weapons.dat` contains the settings for all the weapons in the game used by [Units](/Help/Files/DAT/units.dat.md) and [IScripts](/Help/Files/iscript.bin.md), and references to other data related to the weapons.

Edited by [PyDAT](/Help/Programs/PyDAT.md) on the [Weapons Tab](/Help/Programs/PyDAT/Weapons.md)

## Format
The file has 130 entries, one per weapon ID. Each entry holds the weapons damage settings (amount, bonus per upgrade level, type, explosion, factor, cooldown), targeting settings (min/max range, target flags, error message), splash radii, projectile settings (behaviour, offsets, attack angle, launch spin), and display settings (label, icon) — see the [Weapons Tab](/Help/Programs/PyDAT/Weapons.md) for the full breakdown.
References to weapons in other DAT files use the value 130 (one past the last weapon ID) to mean no weapon.

## References
- Damage [Upgrade](/Help/Files/DAT/upgrades.dat.md)
- Related [Technology](/Help/Files/DAT/techdata.dat.md) (Note: This is unused, it is now just a hint to the related technology)
- Name and Targeting Error [Strings](/Help/Files/TBL.md#stat_txttbl)
- Graphics [Flingy](/Help/Files/DAT/flingy.dat.md)
- [Icon](/Help/Files/GRP.md#cmdicongrp)

## Names
Weapon names come from the label setting, which is a string in [stat_txt.tbl](/Help/Files/TBL.md#stat_txttbl).

## Expanded
An expanded `weapons.dat` (see [Expanded DAT Files](/Help/Programs/PyDAT.md#expanded-dat-files)) can have at most 255 entries.
