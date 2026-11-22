# upgrades.dat
`upgrades.dat` contains the settings for upgrades, like cost and availability settings, as well as references to their ([Icon](/Help/Files/GRP.md#cmdicongrp) and Name [Label](/Help/Files/TBL.md#stat_txttbl)).

Edited by [PyDAT](/Help/Programs/PyDAT.md) on the [Upgrades Tab](/Help/Programs/PyDAT/Upgrades.md)

## Format
The file has 61 entries, one per upgrade ID. Each entry holds the base and per-level factor costs (minerals, vespene, research time), the maximum number of levels, the requirements index, the race and BroodWar flag (only read by StarEdit), plus the icon and label references — see the [Upgrades Tab](/Help/Programs/PyDAT/Upgrades.md) for the full breakdown.
References to upgrades in other DAT files ([units.dat](/Help/Files/DAT/units.dat.md) armor upgrade, weapons.dat damage upgrade) use upgrade 60, which no one can research, to mean no upgrade; the game has no special value for it.
A map's upgrade settings can replace the six costs.

## References
- [Icon](/Help/Files/GRP.md#cmdicongrp)
- Name [Label](/Help/Files/TBL.md#stat_txttbl)

## Names
Upgrade names come from the label setting, which is a string in [stat_txt.tbl](/Help/Files/TBL.md#stat_txttbl).

## Expanded
An expanded `upgrades.dat` (see [Expanded DAT Files](/Help/Programs/PyDAT.md#expanded-dat-files)) can have at most 256 entries.
