# MPQ
`.mpq` files contain almost all the data files used by the game, kind of like a `.zip` file. They can also be embedded in other files like [EXE](/Help/Files/EXE.md) files, which is how a lot of mods are packaged. The game will load a set of MPQ's, and load files from those MPQ's in a defined order. The default MPQ's are in this order:
1. [Patch_rt.mpq](#patchrtmpq)
2. [BrooDat.mpq](#broodatmpq)
3. [StarDat.mpq](#stardatmpq)

Mods will insert their own MPQ at the highest priority, so the modded files will be loaded from there rather than the default MPQ's.

Edited by [PyMPQ](/Help/Programs/PyMPQ.md)

## Patch_rt.mpq
`Patch_rt.mpq` holds the latest changes from patches to the game, which is why it has the highest priority of the default MPQ's.

## BrooDat.mpq
`BrooDat.mpq` holds the data for the BroodWar expansion.

## StarDat.mpq
`StarDat.mpq` holds the data for the base StarCraft game. Some files in this MPQ might not be compatible with PyMS tools, as PyMS is designed for modding BroodWar.
