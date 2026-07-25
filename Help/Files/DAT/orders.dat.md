# orders.dat
`orders.dat` contains the settings for the orders that units can be given, and references to other data related to the orders.

Edited by [PyDAT](/Help/Programs/PyDAT.md) on the [Orders Tab](/Help/Programs/PyDAT/Orders.md)

## Format
The file has 189 entries, one per order ID. Each entry holds the orders behavior flags (whether it uses weapon targeting, can be interrupted, can be queued, is obstructable, and so on), the weapon/technology/obscured-order references, the IScript animation, the highlight icon, and the requirements index — see the [Orders Tab](/Help/Programs/PyDAT/Orders.md) for the full breakdown.

## References
- A [Weapon](/Help/Files/DAT/weapons.dat.md) which specifies the targeting rules (if "Use Weapon Targeting" is enabled)
- A [Technology](/Help/Files/DAT/techdata.dat.md) which specifies the energy required to call the order
- The [Order](/Help/Files/DAT/orders.dat.md) to run if the unit is obscured by fog of war
- Name [String](/Help/Files/TBL.md#stat_txttbl) (Note: This is unused, it is now just a hint)
- An [IScript Animation](/Help/Files/iscript.bin.md#animations) that a unit should use while calling the order
- The [Icon](/Help/Files/GRP.md#cmdicongrp) to highlight on the units command card when executing the order (65535 means no highlight)

## Names
Order names come from the label setting, which is a string in [stat_txt.tbl](/Help/Files/TBL.md#stat_txttbl) (although the game itself does not use it).

## Expanded
An expanded `orders.dat` (see [Expanded DAT Files](/Help/Programs/PyDAT.md#expanded-dat-files)) can have at most 255 entries.
