# IScript Sources
A folder named `iscript.bin` is compiled by [PyMOD](/Help/Programs/PyMOD.md) into [iscript.bin](/Help/Files/iscript.bin.md). Like [AI scripts](/Help/Programs/PyMOD/AI_Script_Sources.md), all of the `.txt` files in the folder are compiled together into one file, because a mod's iscripts live in a single shared file.
In a mod this belongs in the `scripts` folder of your MPQ, so the source is usually `MyMod.mpq/scripts/iscript.bin/`. There are no settings for iscript sources.

## Scripts
Every `.txt` file in the folder is iscript source in the language [PyICE](/Help/Programs/PyICE.md) uses (see [IScript Language](/Help/Programs/PyICE/IScript_Language.md)). A file can hold any number of scripts and they are compiled in alphabetical order, so you can split them up however suits your mod — one file per unit, or one file per group of related graphics.
If two of your scripts use the same script ID, the compile log warns and the later one wins. A folder with no scripts at all is skipped with a warning, and no `iscript.bin` is produced.
Adding a script that doesn't fit fails the build with a message naming the script, the current size, the maximum, and what the size would have become. Unlike AI scripts, `iscript.bin` has no expanded form — the limit is part of the format.

## Names From Your Own Data
Iscripts refer to images, sprites, flingies, sounds, and weapons, and can use names rather than raw IDs. To resolve those names PyMOD looks for the game data of the MPQ this source is inside, using the versions your own project compiled: `arr/images.tbl`, `arr/sfxdata.tbl`, `rez/stat_txt.tbl`, `arr/images.dat`, `arr/sprites.dat`, `arr/flingy.dat`, `arr/sfxdata.dat`, and `arr/weapons.dat`.
Each one is optional, and the compile log says whether it was found. This is why iscripts are compiled after the DAT and TBL sources — so a new image or sound you added in your own `.dat` files can be referred to by name. If a file is missing you can still use raw IDs.

## Base File
By default the compile starts from an empty file containing only your scripts. Since `iscript.bin` drives the animations of every graphic in the game, that is almost never what you want — an iscript.bin holding only your scripts leaves every other graphic in the game without animations.
To build on top of an existing file instead, put a base `iscript.bin` in the folder named the same as the folder itself — `iscript.bin/iscript.bin`. Your scripts are added on top of the base scripts, replacing any base script with the same ID, so a mod usually starts from the game's `iscript.bin` and only ships the scripts it changes.

## See Also
- [PyMOD](/Help/Programs/PyMOD.md)
- [AI Script Sources](/Help/Programs/PyMOD/AI_Script_Sources.md)
- [DAT Sources](/Help/Programs/PyMOD/DAT_Sources.md)
- [Building](/Help/Programs/PyMOD/Building.md)
- [PyICE](/Help/Programs/PyICE.md)
- [IScript Language](/Help/Programs/PyICE/IScript_Language.md)
- [iscript.bin](/Help/Files/iscript.bin.md)
- [Editing an IScript](/Help/Tutorials/Editing_an_IScript.md)
