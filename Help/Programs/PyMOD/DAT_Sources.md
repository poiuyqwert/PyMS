# DAT Sources
A folder named exactly like one of the game's `.dat` files is compiled by [PyMOD](/Help/Programs/PyMOD.md) into that DAT file. All eleven are supported: [units.dat](/Help/Files/DAT/units.dat.md), [weapons.dat](/Help/Files/DAT/weapons.dat.md), [flingy.dat](/Help/Files/DAT/flingy.dat.md), [sprites.dat](/Help/Files/DAT/sprites.dat.md), [images.dat](/Help/Files/DAT/images.dat.md), [upgrades.dat](/Help/Files/DAT/upgrades.dat.md), [techdata.dat](/Help/Files/DAT/techdata.dat.md), [sfxdata.dat](/Help/Files/DAT/sfxdata.dat.md), [portdata.dat](/Help/Files/DAT/portdata.dat.md), [mapdata.dat](/Help/Files/DAT/mapdata.dat.md), and [orders.dat](/Help/Files/DAT/orders.dat.md).
In a mod these belong in the `arr` folder of your MPQ, so a units.dat source is usually `MyMod.mpq/arr/units.dat/`.

## Entry Files
The folder contains any number of `.txt` files in the text format [PyDAT](/Help/Programs/PyDAT.md) exports with **Export to TXT**. Each file can hold any selection of entries, and any selection of properties within an entry, so a file only needs to contain what you are actually changing:

```
Unit(0):
	hit_points.whole 400
	ground_weapon 0
```

That means you can organize your changes however suits you — one file per race, one file per feature, or one big file. The files are imported in alphabetical order, so if two files set the same property of the same entry, the later filename wins.
A folder with no `.txt` files produces no DAT file at all. The compile log records this as a warning and moves on, so a folder holding only a base `.dat` is not a way to copy that file into your mod unchanged — use a plain copied file for that.

## Base File
The entries are imported on top of a base file. By default that is the unmodified game DAT bundled with PyMS, which is why your `.txt` files only need your changes.
To build on top of a different DAT instead, put it in the folder named the same as the folder itself — `units.dat/units.dat`. This is what you want when your mod continues from an existing mod's DAT, or when you keep a hand-tuned DAT and only script the last few changes on top of it.

## Expanded DAT Files
A DAT can be expanded past the game's normal entry count, so you can add new units, weapons, and so on:

- `entry_count`: Expands the DAT to this total number of entries. The value may be rounded up to satisfy the format's constraints, and asking for more entries than the format allows fails the build. Expanding only ever adds entries, so a value that is not larger than the current entry count does nothing.

`entry_count` is not needed if your base file is already expanded — the extra entries come along with it.
Whenever the compiled DAT ends up expanded, by either route, the compile log prints a warning as a reminder that the game needs a plugin like [DatExtend](https://github.com/saintofidiocy/GPTP/tree/DatExtender) to load expanded DAT files.

## See Also
- [PyMOD](/Help/Programs/PyMOD.md)
- [MPQ Packages](/Help/Programs/PyMOD/MPQ_Packages.md)
- [Building](/Help/Programs/PyMOD/Building.md)
- [PyDAT](/Help/Programs/PyDAT.md)
- [units.dat](/Help/Files/DAT/units.dat.md)
- [Editing a Unit](/Help/Tutorials/Editing_a_Unit.md)
