# portdata.dat
`portdata.dat` contains the settings for the portraits (idle "fidget" videos and talking videos) used by [Units](/Help/Files/DAT/units.dat.md) and [Map triggers](/Help/Files/Maps.md#triggers), and a reference to a string in [portdata.tbl](/Help/Files/TBL.md#portdatatbl) which contains the folder and start of the file name of the [SMK](/Help/Files/SMK.md) files in the [MPQ's](/Help/Files/MPQ.md).

Edited by [PyDAT](/Help/Programs/PyDAT.md) on the [Portdata Tab](/Help/Programs/PyDAT/Portdata.md)

## Format
The file has 110 entries, one per portrait ID, stored as 6 lists one after another: the fidget (idle) SMK prefix, the talking SMK prefix, and the chances of fidget videos 0, 1, 2 and 3. PyDAT shows the fidget prefix with the fidget 0 and 2 chances as the idle portrait, and the talking prefix with the fidget 1 and 3 chances as the talking portrait — see the [Portdata Tab](/Help/Programs/PyDAT/Portdata.md) for the full breakdown.
References to portraits in [units.dat](/Help/Files/DAT/units.dat.md) use the value 65535 to mean no portrait.

## References
- References to strings in [portdata.tbl](/Help/Files/TBL.md#portdatatbl) (1-based, 0 means none), which contain the folder and start of the file name of the [SMK](/Help/Files/SMK.md) videos played by the portrait: the game plays `portrait\<string><n>.smk`, with n = 0–3 for fidgets and 0–2 for talking

## Names
Portraits have no name setting — PyDAT names them after their idle [SMK](/Help/Files/SMK.md) prefix.

## Expanded
An expanded `portdata.dat` (see [Expanded DAT Files](/Help/Programs/PyDAT.md#expanded-dat-files)) can have at most 65535 entries.
