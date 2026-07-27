# AI Script Sources
A folder named `aiscript.bin` is compiled by [PyMOD](/Help/Programs/PyMOD.md) into [aiscript.bin](/Help/Files/aiscript.bin.md), and into [bwscript.bin](/Help/Files/aiscript.bin.md#bwscriptbin) when any of your scripts needs it. Unlike most sources, all of the `.txt` files in the folder are compiled together into one file, because the AI scripts of a mod live in a single shared file.
In a mod these belong in the `scripts` folder of your MPQ, so the source is usually `MyMod.mpq/scripts/aiscript.bin/`. The files tree lists this source as `aiscript.bin/bwscript.bin` as a reminder that it can produce both.

## Scripts and External Definitions
Every `.txt` file in the folder is an AI script source in the language [PyAI](/Help/Programs/PyAI.md) uses (see [AI Language](/Help/Programs/PyAI/AI_Language.md)). A file can hold any number of scripts, so you can organize them however you like; they are compiled in alphabetical order.
Files ending in `def.txt` are treated as [external definitions](/Help/Programs/PyAI/AI_Language.md#external-definitions) instead, and are loaded before any script is compiled. That makes the names they define available to all of your scripts, which is the point of keeping them in a separate file. `unitdef.txt` is the usual name.
If two of your scripts use the same script ID, the compile log warns and the later one wins. A folder with no scripts at all is skipped with a warning, and no `aiscript.bin` is produced.

## Names From Your Own Data
AI scripts can refer to units, upgrades, and technologies by name rather than by raw ID. To resolve those names PyMOD looks for the game data of the MPQ this source is inside, using the versions your own project compiled: `rez/stat_txt.tbl`, `rez/unitnames.tbl`, `arr/units.dat`, `arr/upgrades.dat`, and `arr/techdata.dat`.
Each one is optional, and the compile log says whether it was found. This is why AI scripts are compiled after the DAT and TBL sources — the names your scripts use come from your mod's own data, so a unit you renamed in your `stat_txt.tbl` can be referred to by its new name. If a file is missing you can still use raw IDs.

## Base Files
By default the compile starts from empty files containing only your scripts. To build on top of existing files instead, put a base `aiscript.bin` in the folder named the same as the folder itself — `aiscript.bin/aiscript.bin` — and optionally a base `bwscript.bin` beside it.
Your scripts are added on top of the base scripts, replacing any base script with the same ID. A base `bwscript.bin` can only be used together with a base `aiscript.bin` and fails the build on its own, since it can't be interpreted without the `aiscript.bin` that references its scripts. Scripts in a base `bwscript.bin` that the base `aiscript.bin` doesn't reference, or that it already defines itself, are reported in the compile log and left out.

## About bwscript.bin
`bwscript.bin` is only written when your scripts actually require it. This is deliberate: an empty `bwscript.bin` packaged into your MPQ would shadow the game's real one and wipe out all of the vanilla Brood War AI, so PyMOD would rather produce no file than a stub. If you were expecting one and don't get it, none of your scripts needed it.

## Expanded Files
AI script files have a maximum size, and adding a script that doesn't fit fails the build with a message naming the script, the current size, the maximum, and what the size would have become.

- `expanded` (default `false`): Compiles expanded files, raising the maximum file size.

`expanded` is not needed if your base files are already expanded. Whenever the compiled files end up expanded, by either route, the compile log prints a warning as a reminder that the game needs a plugin to load expanded AI script files.

## See Also
- [PyMOD](/Help/Programs/PyMOD.md)
- [IScript Sources](/Help/Programs/PyMOD/IScript_Sources.md)
- [DAT Sources](/Help/Programs/PyMOD/DAT_Sources.md)
- [Building](/Help/Programs/PyMOD/Building.md)
- [PyAI](/Help/Programs/PyAI.md)
- [AI Language](/Help/Programs/PyAI/AI_Language.md)
- [aiscript.bin](/Help/Files/aiscript.bin.md)
- [Creating Your First AI Script](/Help/Tutorials/Creating_Your_First_AI_Script.md)
