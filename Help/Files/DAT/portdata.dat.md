# portdata.dat
`portdata.dat` contains the settings for the idle and talking portraits used by [Units](/Help/Files/DAT/units.dat.md) and [Map triggers](/Help/Files/Maps.md#triggers), and a reference to a string in [portdata.tbl](/Help/Files/TBL.md#portdatatbl) which contains the path to the [SMK](/Help/Files/SMK.md) file in the [MPQ's](/Help/Files/MPQ.md).

Edited by [PyDAT](/Help/Programs/PyDAT.md) on the [Portdata Tab](/Help/Programs/PyDAT/Portdata.md)

## Format
The file has 110 entries, one per portrait ID, stored as 6 lists one after another: the fidget (idle) SMK prefix, the talking SMK prefix, and the chances of fidget videos 0, 1, 2 and 3. PyDAT shows the fidget prefix with the four chances as the idle portrait, and the talking prefix as the talking portrait. Its export format still groups them the old way: `idle` holds the fidget prefix with the fidget 0 (`smk_change`) and 2 (`unknown`) chances, and `talking` holds the talking prefix with the fidget 1 and 3 chances — see the [Portdata Tab](/Help/Programs/PyDAT/Portdata.md) for the full breakdown.
References to portraits in [units.dat](/Help/Files/DAT/units.dat.md) use the value 65535 to mean no portrait.

## References
- References to strings in [portdata.tbl](/Help/Files/TBL.md#portdatatbl), which contain the paths in the [MPQ's](/Help/Files/MPQ.md) for the folders of [SMK](/Help/Files/SMK.md) videos played by the portrait

## Names
Portraits have no name setting — PyDAT names them after their idle [SMK](/Help/Files/SMK.md) folder path.

## Expanded
An expanded `portdata.dat` (see [Expanded DAT Files](/Help/Programs/PyDAT.md#expanded-dat-files)) can have at most 65535 entries.
