# techdata.dat
`techdata.dat` contains the settings for researchable technologies, like cost and availability settings, as well as references to their ([Icon](/Help/Files/GRP.md#cmdicongrp) and Name [String](/Help/Files/TBL.md#stat_txttbl)).

Edited by [PyDAT](/Help/Programs/PyDAT.md) on the [Techdata Tab](/Help/Programs/PyDAT/Techdata.md)

## Format
The file has 44 entries, one per technology ID. Each entry holds the research costs (minerals, vespene, time), the energy cost of using the ability, the research and use requirement indexes, race, an unused flag, and the BroodWar flag, plus the icon and label references — see the [Techdata Tab](/Help/Programs/PyDAT/Techdata.md) for the full breakdown.
References to technologies in other DAT files use the value 44 (one past the last technology ID) to mean no technology.

## References
- [Icon](/Help/Files/GRP.md#cmdicongrp)
- Name [String](/Help/Files/TBL.md#stat_txttbl)

## Names
Technology names come from the label setting, which is a string in [stat_txt.tbl](/Help/Files/TBL.md#stat_txttbl).

## Expanded
An expanded `techdata.dat` (see [Expanded DAT Files](/Help/Programs/PyDAT.md#expanded-dat-files)) can have at most 255 entries.
