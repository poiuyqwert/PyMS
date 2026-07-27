# Other Sources
Not everything in a mod needs compiling. [PyMOD](/Help/Programs/PyMOD.md) handles anything it doesn't recognize as a source type in the simplest way that works, so you can drop files your mod needs into your project without ceremony.

## Plain Folders
A folder whose name doesn't match any source type is just a folder. It is recreated in the output and everything inside it is handled individually, which is how the folder structure of your mod gets built — `MyMod.mpq/unit/terran/` is two plain folders on the way to the sources inside them.
This is also why source folders don't have to sit at the top of your MPQ. Nest them as deeply as the game's paths require.

## Copied Files
Any file that isn't part of a source folder is copied into your mod as-is. Sounds, videos, and files in formats PyMOD has no compiler for all work this way: put `sound.wav` where you want it and it ends up at that path in your MPQ.
Copied files are hashed like everything else, so an unchanged file is skipped on the next compile. Inside an [MPQ package](/Help/Programs/PyMOD/MPQ_Packages.md) a copied file's compression can be set with a `config.json` named after it — `sound.wav.config.json` beside `sound.wav`.
A copied file that is not inside an MPQ folder is published to `.build/artifacts/` at its matching path, the same as a compiled one.

## Ignored Names
Some names are never treated as sources:

- Anything starting with `.` is skipped entirely, folders and files alike. That is what keeps `.pymod_project.json` and the whole `.build` folder out of your mod, and it means you can hide working files from a build by prefixing them with a dot.
- `config.json` and any `*.config.json` file are configuration, so they are never copied into your mod. Changing one still rebuilds the source it configures.

Note that a file is only skipped for these reasons if PyMOD is walking the folder it is in. Inside a source folder that owns its contents — a `marine.grp/` or an `aiscript.bin/` — nothing is copied anywhere regardless of its name; only the inputs that source looks for are used. Notes, spare art, and old versions can be parked in there safely.

## See Also
- [PyMOD](/Help/Programs/PyMOD.md)
- [MPQ Packages](/Help/Programs/PyMOD/MPQ_Packages.md)
- [Building](/Help/Programs/PyMOD/Building.md)
