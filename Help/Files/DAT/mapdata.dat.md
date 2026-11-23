# mapdata.dat
`mapdata.dat` contains the folder of each single player campaign mission, as references to a string in [mapdata.tbl](/Help/Files/TBL.md#mapdatatbl) which contains the folder of the mission's [CHK](/Help/Files/Maps.md#scenariochk) file in the [MPQ's](/Help/Files/MPQ.md).

Edited by [PyDAT](/Help/Programs/PyDAT.md) on the [Mapdata Tab](/Help/Programs/PyDAT/Mapdata.md)

## Format
The file has 65 entries, one per campaign mission number (0 is no mission, 1 is the Terran tutorial, 64 the last Brood War Zerg mission), and each entry is just the mission folder reference. Which missions make up each campaign, and in what order, is fixed in the game, not set here. It is the only DAT file that does not support [expansion](/Help/Programs/PyDAT.md#expanded-dat-files).

## References
- A reference to a string in [mapdata.tbl](/Help/Files/TBL.md#mapdatatbl) (1-based, 0 means none), which contains the path in the [MPQ's](/Help/Files/MPQ.md) for the missions folder (holding its `staredit\scenario.chk` [map](/Help/Files/Maps.md#scenariochk) and [WAV](/Help/Files/WAV.md) files)

## Names
Missions have no name setting — PyDAT names them after their folder path.
