# Portdata Tab
The Portdata tab of [PyDAT](/Help/Programs/PyDAT.md) edits [portdata.dat](/Help/Files/DAT/portdata.dat.md), which contains the settings for the unit portraits shown in the bottom center of the game screen.
Each portrait entry has two sets of [SMK](/Help/Files/SMK.md) videos — the **Idle Portrait** played normally, and the **Talking Portrait** played when the unit speaks. Each set has:

- **SMK Dir**: The folder of SMK videos, referenced by its index in `portdata.tbl` (the dropdown shows the paths).
- **SMK Change**: How often the game skips the first SMK in the folder and plays one of the others instead.
- **Unknown**: An unknown value.

## Used By
The [Used By](/Help/Programs/PyDAT.md#used-by) panel lists the units using the portrait.

## See Also
- [PyDAT](/Help/Programs/PyDAT.md)
- [portdata.dat](/Help/Files/DAT/portdata.dat.md)
- [SMK](/Help/Files/SMK.md)
