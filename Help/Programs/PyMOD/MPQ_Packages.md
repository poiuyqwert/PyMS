# MPQ Packages
A folder whose name ends with `.mpq` is packaged by [PyMOD](/Help/Programs/PyMOD.md) into an [MPQ](/Help/Files/MPQ.md) archive of the same name. Everything inside the folder is compiled first and then added to the archive, so a `MyMod.mpq/` folder becomes a `MyMod.mpq` you can load into the game.
The folder layout inside the `.mpq` folder is the layout inside the archive, so it has to match the paths the game looks the files up by — for example `MyMod.mpq/unit/terran/marine.grp/` produces the archive file `unit\terran\marine.grp`. Use the [Extract](/Help/Programs/PyMOD.md#extract) dialog to look up the path of a file you want to override.
An MPQ folder is not required. Sources outside of one are still compiled, and their compiled files are published as loose files in `.build/artifacts/`.

## Archive Settings
A `config.json` in the `.mpq` folder configures the archive itself:

- `max_files` (default `1024`): The maximum number of files the archive can hold. Adding more files than this fails the build, so raise it if you outgrow it.
- `block_size` (default `3`): The sector size shift of the archive.
- `autocompression`: Chooses the compression for each file by its extension. The default is `standard` for everything, except `.mpq` and `.smk` files which are stored uncompressed and `.wav` files which use `audio:1`.

`autocompression` is an object mapping a file extension (with the dot) to a compression, plus a `Default` entry used for extensions not listed:

```
{
	"max_files": 1024,
	"block_size": 3,
	"autocompression": {
		".mpq": "none",
		".smk": "none",
		".wav": "audio:1",
		"Default": "standard"
	}
}
```

## Compression
A compression is written as a type, optionally followed by a colon and a level:

- `none`: Stored uncompressed. Use this for data the game reads directly and for files that are already compressed.
- `standard`: The compression the game uses for most of its files, and the right choice unless you have a reason to pick something else.
- `deflate`: Zlib compression, with levels `0` (default) through `10` (best compression).
- `audio`: Lossy compression for sounds, with levels `0` (best quality), `1` (medium), and `2` (least space).
- `auto`: Leaves the choice to the MPQ library.

The level is optional, is ignored by the types that have no levels, and is clamped if you go past the highest one. A compression type that is not one of the names above, or a level that is not a number, fails the build rather than silently packaging the file with a different setting.

## Overriding One File's Compression
The compression chosen by `autocompression` can be overridden for an individual file with a `compression` setting. Where that setting goes depends on the kind of source:

- For a compiled source (anything with its own folder, like `marine.grp/` or `stat_txt.tbl/`) put `compression` in that folder's own `config.json`, alongside its compile settings.
- For a plain copied file put it in a `config.json` named after the file — `sound.wav` is configured by `sound.wav.config.json` beside it.

So a GRP that should be stored uncompressed uses one `config.json` for both jobs:

```
{
	"frames_mode": "single_framesets",
	"frame_count": 229,
	"compression": "none"
}
```

The compile log names the compression used for every file it adds, and whether it came from the `autocompression` settings or from a `config.json`, so you can check what you actually got.

## Nested MPQs
An `.mpq` folder can contain another `.mpq` folder. The inner archive is packaged first and then added to the outer archive as a single file, which is how a mod ships an MPQ inside its own MPQ. By default nested archives are stored uncompressed (they are already compressed), which is what the `.mpq` entry in the default `autocompression` settings does.
A nested archive's `config.json` does double duty just like a compiled source's does: the archive settings configure the nested archive, and a `compression` setting there controls how it is stored inside its parent.
Only top level `.mpq` folders become artifacts. A nested archive is built inside `.build/intermediates/` and only ships inside its parent, so you will not find it in `.build/artifacts/` on its own.

## See Also
- [PyMOD](/Help/Programs/PyMOD.md)
- [Building](/Help/Programs/PyMOD/Building.md)
- [Other Sources](/Help/Programs/PyMOD/Other_Sources.md)
- [MPQ](/Help/Files/MPQ.md)
- [PyMPQ](/Help/Programs/PyMPQ.md)
- [Building a Mod Project](/Help/Tutorials/Building_a_Mod_Project.md)
