# units.dat
`units.dat` contains the settings for all the units in the game, and references to other data related to the units.

Edited by [PyDAT](/Help/Programs/PyDAT.md) on the [Units Tab](/Help/Programs/PyDAT/Units.md)

## Format
The file has 228 entries, one per unit ID. Each entry holds the units vital statistics (hit points, shields, armor), build cost and time, supply and transport space, weapons, sight and targeting ranges, sounds, graphics and dimensions, StarEdit settings, and AI behavior — see the [Units Tab](/Help/Programs/PyDAT/Units.md) for the full breakdown by category.
Like all DAT files, the file stores one array per setting (each array covering every entry), rather than one block per entry. A few settings are only stored for a range of unit IDs — the infestation reference and addon position only exist for IDs 106 to 201 (buildings), and the Ready/Yes/Annoyed sounds only for IDs 0 to 105.

## References
- Armor [Upgrade](/Help/Files/DAT/upgrades.dat.md)
- [Weapons](/Help/Files/DAT/weapons.dat.md)
- [Sounds](/Help/Files/DAT/sfxdata.dat.md)
- Graphics [Flingy](/Help/Files/DAT/flingy.dat.md)
- Construction [Image](/Help/Files/DAT/images.dat.md)
- [Portraits](/Help/Files/DAT/portdata.dat.md)
- Rank [Strings](/Help/Files/TBL.md#stat_txttbl)
- AI Action [Orders](/Help/Files/DAT/orders.dat.md)
- Subunit and Infestation [Units](/Help/Files/DAT/units.dat.md)

## Names
The unit names are not specified in a setting on the unit, they are the first 228 entries in [stat_txt.tbl](/Help/Files/TBL.md#stat_txttbl) (expanded entries would get their names from [unitnames.tbl](/Help/Files/TBL.md#unitnamestbl), see [Expanded DAT Files](/Help/Programs/PyDAT.md#expanded-dat-files) for more info).

## Expanded
An expanded `units.dat` (see [Expanded DAT Files](/Help/Programs/PyDAT.md#expanded-dat-files)) must have a multiple of 12 entries, at least 250 and at most 912, and IDs 228 to 250 are reserved. Some settings are also stored larger in expanded files, so their references can reach expanded entries in other DAT files (for example the graphics reference grows to support expanded [flingy.dat](/Help/Files/DAT/flingy.dat.md) entries).
