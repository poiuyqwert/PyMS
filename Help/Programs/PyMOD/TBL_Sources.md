# TBL Sources
A folder whose name ends with `.tbl` is compiled by [PyMOD](/Help/Programs/PyMOD.md) into a [.tbl](/Help/Files/TBL.md) string table of the same name. The folder contains a single `.txt` file with the same base name as the folder, so a `stat_txt.tbl/` folder is compiled from `stat_txt.tbl/stat_txt.txt`.
The `.txt` file is the format [PyTBL](/Help/Programs/PyTBL.md) exports: one string per line, with the special characters written as `<0>` style escapes.

```
Terran Marine<0>*<0>Ground Units<0>
Terran Ghost<0>*<0>Ground Units<0>
```

Because a TBL is a plain list, a string's position in the file is its ID, and the game looks strings up by ID. That means you can not leave lines out of the file the way you can leave entries out of a [DAT source](/Help/Programs/PyMOD/DAT_Sources.md) — the `.txt` has to contain every string, in order. Export the game's TBL with PyTBL, then edit the lines you want to change.
In a mod `stat_txt.tbl` belongs in the `rez` folder of your MPQ, so the source is usually `MyMod.mpq/rez/stat_txt.tbl/`. There are no settings for TBL sources.

## See Also
- [PyMOD](/Help/Programs/PyMOD.md)
- [MPQ Packages](/Help/Programs/PyMOD/MPQ_Packages.md)
- [PyTBL](/Help/Programs/PyTBL.md)
- [TBL](/Help/Files/TBL.md)
- [Editing Game Text](/Help/Tutorials/Editing_Game_Text.md)
