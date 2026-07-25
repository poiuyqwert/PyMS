# upgrades.dat
`upgrades.dat` contains the settings for upgrades, like cost and availability settings, as well as references to their ([Icon](/Help/Files/GRP.md#cmdicongrp) and Name [Label](/Help/Files/TBL.md#stat_txttbl)).

Edited by [PyDAT](/Help/Programs/PyDAT.md) on the [Upgrades Tab](/Help/Programs/PyDAT/Upgrades.md)

## Format
The file has 61 entries, one per upgrade ID. Each entry holds the base and per-level factor costs (minerals, vespene, research time), the maximum number of levels, the requirements index, race, and BroodWar flag, plus the icon and label references — see the [Upgrades Tab](/Help/Programs/PyDAT/Upgrades.md) for the full breakdown.
References to upgrades in other DAT files use the value 61 (one past the last upgrade ID) to mean no upgrade.

## References
- [Icon](/Help/Files/GRP.md#cmdicongrp)
- Name [Label](/Help/Files/TBL.md#stat_txttbl)

## Names
Upgrade names come from the label setting, which is a string in [stat_txt.tbl](/Help/Files/TBL.md#stat_txttbl).

## Expanded
An expanded `upgrades.dat` (see [Expanded DAT Files](/Help/Programs/PyDAT.md#expanded-dat-files)) can have at most 256 entries.
