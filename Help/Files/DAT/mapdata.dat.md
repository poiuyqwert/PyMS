# mapdata.dat
`mapdata.dat` contains the list of single player campaign maps, as references to a string in [mapdata.tbl](/Help/Files/TBL.md#mapdatatbl) which contains the path to the [CHK](/Help/Files/Maps.md#scenariochk) file in the [MPQ's](/Help/Files/MPQ.md).

Edited by [PyDAT](/Help/Programs/PyDAT.md) on the [Mapdata Tab](/Help/Programs/PyDAT/Mapdata.md)

## Format
The file has 65 entries, one per campaign mission, and each entry is just the mission folder reference. It is the only DAT file that does not support [expansion](/Help/Programs/PyDAT.md#expanded-dat-files).

## References
- A reference to a string in [mapdata.tbl](/Help/Files/TBL.md#mapdatatbl), which contains the path in the [MPQ's](/Help/Files/MPQ.md) for the missions folder (holding its `staredit\scenario.chk` [map](/Help/Files/Maps.md#scenariochk) and [WAV](/Help/Files/WAV.md) files)

## Names
Missions have no name setting — PyDAT names them after their folder path.
