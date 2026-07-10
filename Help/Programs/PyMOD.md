# PyMOD
PyMOD is a tool for building complete mod projects. It walks your project folder, detects source types by folder naming conventions, compiles each source into an intermediate file, and packages the results into [.mpq](/Help/Files/MPQ.md) archives ready to load into the game. Builds are incremental: files are hashed so only sources that changed since the last compile are rebuilt.

## Projects
A project is just a folder containing your mod's sources, marked as a PyMOD project by a hidden `.pymod_project.json` file. Use `New` to create a project (the marker is created for you), or `Open` on an existing folder (you will be offered to initialize it as a project if it isn't one yet).

The layout of the folder determines what gets built. Everything you want packaged into an MPQ goes inside a folder whose name ends with `.mpq`:

```
MyMod/
  .pymod_project.json
  MyMod.mpq/
    config.json
    arr/
      units.dat
	  units.dat.config.json
    rez/
      stat_txt.tbl/
        stat_txt.txt
    scripts/
      aiscript.bin/
		unitdef.txt 
		Ter3.txt
		PB1A.txt
    unit/terran/marine.grp/
      frame 000.bmp
      frame 001.bmp
      ...
	unit/protoss/dragoon.grp/
	  config.json
	  frames.bmp
```

## Source types
Source types are detected by folder name:

| Folder name | Source type | Contents |
|-------------|-------------|----------|
| `*.mpq` | MPQ package | Everything inside is packaged into an MPQ artifact of the same name |
| `*.grp` | GRP graphic | `.bmp` frame files, compiled into a [.grp](/Help/Files/GRP.md) |
| `*.tbl` | TBL strings | A `.txt` file of the same base name, compiled into a [.tbl](/Help/Files/TBL.md) |
| `aiscript.bin` | AI scripts | `.txt` AI script sources (and `*def.txt` extdefs), compiled into `aiscript.bin` (and `bwscript.bin` when scripts require it) |

Any other folder is treated as a plain folder, and any other file is copied into the mod as-is. Files and folders starting with `.` are ignored, as are `config.json`/`*.config.json` configuration files (see below). MPQ folders can be nested inside other MPQ folders: the nested MPQ is packaged first, then embedded as a file inside the MPQ containing it (uncompressed by default, per the `autocompression` settings).

## Configuration
Folder sources can be configured with a `config.json` file inside the folder, and file sources with a sibling `<name>.config.json` file. Changing a `config.json` triggers a rebuild of that source on the next compile.

### MPQ package (`config.json` inside a `*.mpq` folder)
| Setting | Default | Description |
|---------|---------|-------------|
| `max_files` | `1024` | Maximum file capacity of the archive |
| `block_size` | `3` | Sector size shift of the archive |
| `autocompression` | Standard, with `.smk`/`.mpq` uncompressed and `.wav` audio compression | Maps file extensions (or `"Default"`) to the compression used for files added to the archive |

### Per-file compression (`<name>.config.json` next to a file in a `*.mpq` folder)
| Setting | Default | Description |
|---------|---------|-------------|
| `compression` | From `autocompression` | Compression to use for this specific file (`NoCompression`, `Standard`, `Deflate`, `Audio` levels, etc.) |

### GRP graphic (`config.json` inside a `*.grp` folder)
| Setting | Default | Description |
|---------|---------|-------------|
| `frames_mode` | `separate_bmps` | `separate_bmps` (one BMP per frame), `single_vertical` (one BMP, frames stacked vertically), or `single_framesets` (one BMP of framesets) |
| `frame_count` | | Number of frames — required for the single-BMP modes |
| `uncompressed` | `false` | Save the GRP uncompressed |

## Building
`Compile` runs the build: sources are compiled into `.build/intermediates/` inside your project, and the final MPQ artifacts are written to `.build/artifacts/`. Hashes of inputs and outputs are stored in `.build/meta.json` so unchanged sources are skipped on the next compile. `Clean` deletes the intermediates folder to force a full rebuild. `Extract` lets you browse the files in the MPQs configured in the settings (Manage Settings → MPQ Settings).

## Command line
Running `PyMOD.pyw` with a project path compiles it headlessly, printing the build log to the console:

```
PyMOD <project_path>
```

Use `--gui <project_path>` to open a project in the GUI instead.
