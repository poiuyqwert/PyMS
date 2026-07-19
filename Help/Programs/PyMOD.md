# PyMOD
PyMOD is a tool for building complete mod projects. It walks your project folder, detects source types by folder naming conventions, compiles each source into a game file, and can package the results into [.mpq](/Help/Files/MPQ.md) archives ready to load into the game. Builds are incremental: files are hashed so only sources that changed since the last compile are rebuilt.

## Projects
A project is just a folder containing your mod's sources, marked as a PyMOD project by a hidden `.pymod_project.json` file. Use `New` to create a project (the marker is created for you), or `Open` on an existing folder (you will be offered to initialize it as a project if it isn't one yet).

The layout of the folder determines what gets built. Everything you want packaged into an MPQ goes inside a folder whose name ends with `.mpq`:

```
┬ MyMod/
├── .pymod_project.json
└─┬ MyMod.mpq/
  ├── config.json
  ├─┬ arr/
  │ └─┬ units.dat/
  │   ├── config.json
  │   ├── units.dat
  │   ├── Race1.txt
  │   └── Race2.txt
  ├─┬ rez/
  │ └─┬ stat_txt.tbl/
  │   └── stat_txt.txt
  ├─┬ scripts/
  │ └─┬ aiscript.bin/
  │   ├── unitdef.txt
  │   ├── Ter3.txt
  │   ├── PB1A.txt
  │   └── ...
  └─┬ unit/
    ├─┬ terran/
    │ └─┬ marine.grp/
    │   ├── frame 000.bmp
    │   ├── frame 001.bmp
    │   └── ...
    └─┬ protoss/
      └─┬ dragoon.grp/
        ├── config.json
        └── frames.bmp
```

An MPQ is not required, though. Sources outside of any `*.mpq` folder are compiled all the same, and their compiled files are kept in `.build/intermediates/` mirroring your project layout — so you can simply compile your game files and do whatever you want with them (package them yourself, load them with a launcher that supports loose files, copy them into another project, etc.).

## Source types
Source types are detected by folder name:

| Folder name | Source type | Contents |
|-------------|-------------|----------|
| `*.mpq` | [MPQ package](#mpq-packages-mpq) | Everything inside is packaged into an MPQ artifact of the same name |
| `units.dat`, `weapons.dat`, etc. | [DAT file](#dat-files-unitsdat-weaponsdat-etc) | `.txt` entry files (and optionally a base `.dat`), compiled into the DAT file |
| `*.grp` | [GRP graphic](#grp-graphics-grp) | `.bmp` frame files, compiled into a [.grp](/Help/Files/GRP.md) |
| `*.tbl` | [TBL strings](#tbl-strings-tbl) | A `.txt` file of the same base name, compiled into a [.tbl](/Help/Files/TBL.md) |
| `aiscript.bin` | [AI scripts](#ai-scripts-aiscriptbin) | `.txt` AI script sources (and `*def.txt` extdefs, and optionally base `.bin` files), compiled into `aiscript.bin` (and `bwscript.bin` when scripts require it) |
| `iscript.bin` | [Iscripts](#iscripts-iscriptbin) | `.txt` iscript sources (and optionally a base `.bin` file), compiled into `iscript.bin` |

Anything else is handled as described in [Other folders and files](#other-folders-and-files).

Sources can be configured with a `config.json` file inside their folder. Changing a `config.json` triggers a rebuild of that source on the next compile.

### MPQ packages (`*.mpq`)
Everything inside the folder is packaged into an MPQ artifact of the same name. MPQ folders can be nested inside other MPQ folders: the nested MPQ is packaged first, then embedded as a file inside the MPQ containing it (uncompressed by default, per the `autocompression` settings).

The archive can be configured with a `config.json` inside the folder:

| Setting | Default | Description |
|---------|---------|-------------|
| `max_files` | `1024` | Maximum file capacity of the archive |
| `block_size` | `3` | Sector size shift of the archive |
| `autocompression` | Standard, with `.smk`/`.mpq` uncompressed and `.wav` audio compression | Maps file extensions (or `"Default"`) to the compression used for files added to the archive |

The compression of an individual file can be overridden with a sibling `<name>.config.json` file:

| Setting | Default | Description |
|---------|---------|-------------|
| `compression` | From `autocompression` | Compression to use for this specific file (`NoCompression`, `Standard`, `Deflate`, `Audio` levels, etc.) |

### DAT files (`units.dat`, `weapons.dat`, etc.)
A folder named exactly like one of the game's DAT files is compiled into that DAT file: [units.dat](/Help/Files/DAT/units.dat.md), [weapons.dat](/Help/Files/DAT/weapons.dat.md), [flingy.dat](/Help/Files/DAT/flingy.dat.md), [sprites.dat](/Help/Files/DAT/sprites.dat.md), [images.dat](/Help/Files/DAT/images.dat.md), [upgrades.dat](/Help/Files/DAT/upgrades.dat.md), [techdata.dat](/Help/Files/DAT/techdata.dat.md), [sfxdata.dat](/Help/Files/DAT/sfxdata.dat.md), [portdata.dat](/Help/Files/DAT/portdata.dat.md), [mapdata.dat](/Help/Files/DAT/mapdata.dat.md), or [orders.dat](/Help/Files/DAT/orders.dat.md).

The folder contains any number of `.txt` files in the text format exported by PyDAT. Each file can hold any selection of entries (and any selection of properties within an entry), so you can organize your changes however you like — for example a `units.dat/` folder with one `.txt` per race. The files are imported in alphabetical order, so if two files set the same property of the same entry, the later one wins.

The entries are imported on top of a base file. By default this is the unmodified game DAT bundled with PyMS, so your `.txt` files only need to contain what you actually change. To build on top of a different DAT instead, place it in the folder named the same as the folder itself (e.g. `units.dat/units.dat`).

The DAT can be expanded beyond the game's normal entry count with a `config.json` inside the folder:

| Setting | Default | Description |
|---------|---------|-------------|
| `entry_count` | | Expand the DAT to this total entry count (may be rounded up to satisfy the format's constraints). Not required if the base file is already expanded |

If the compiled DAT is expanded — whether through `entry_count` or an already-expanded base file — a warning is output to the compile log as a reminder that the game requires a plugin to use expanded DAT files.

### GRP graphics (`*.grp`)
The folder contains `.bmp` frame files, compiled into a [.grp](/Help/Files/GRP.md) of the same name. By default each `.bmp` is one frame, added in alphabetical order; the single-BMP modes instead take one `.bmp` containing every frame.

| Setting | Default | Description |
|---------|---------|-------------|
| `frames_mode` | `separate_bmps` | `separate_bmps` (one BMP per frame), `single_vertical` (one BMP, frames stacked vertically), or `single_framesets` (one BMP of framesets) |
| `frame_count` | | Number of frames — required for the single-BMP modes |
| `uncompressed` | `false` | Save the GRP uncompressed |

### TBL strings (`*.tbl`)
The folder contains a `.txt` file with the same base name as the folder (e.g. `stat_txt.tbl/stat_txt.txt`), compiled into a [.tbl](/Help/Files/TBL.md) of the folder's name. There is no configuration for TBL sources.

### AI scripts (`aiscript.bin`)
The folder contains `.txt` AI script sources, along with optional `*def.txt` external definition files which are loaded first. All scripts are compiled together into `aiscript.bin` — and `bwscript.bin` when any script requires it (`bwscript.bin` is only produced in that case, so vanilla Brood War AI is not wiped out by a stub file).

By default the compile starts from empty files containing only your scripts. To build on top of existing files instead, place a base `aiscript.bin` in the folder named the same as the folder itself (e.g. `aiscript.bin/aiscript.bin`), optionally with a base `bwscript.bin` beside it. Your scripts are added on top of the base scripts, replacing any base script with the same ID. A base `bwscript.bin` can only be used together with a base `aiscript.bin`, since it can't be interpreted without the `aiscript.bin` that references its scripts.

The files can be expanded beyond the format's normal size limit with a `config.json` inside the folder:

| Setting | Default | Description |
|---------|---------|-------------|
| `expanded` | `false` | Compile expanded files, raising the maximum file size. Not required if the base files are already expanded |

If the compiled files are expanded — whether through `expanded` or already-expanded base files — a warning is output to the compile log as a reminder that the game requires a plugin to use expanded AI script files.

### Iscripts (`iscript.bin`)
The folder contains `.txt` iscript sources in the text format exported by PyICE. All scripts are compiled together into [iscript.bin](/Help/Files/iscript.bin.md).

By default the compile starts from an empty file containing only your scripts. To build on top of an existing file instead, place a base `iscript.bin` in the folder named the same as the folder itself (e.g. `iscript.bin/iscript.bin`). Your scripts are added on top of the base scripts, replacing any base script with the same ID. There is no configuration for iscript sources.

### Other folders and files
Any other folder is treated as a plain folder: it is recreated in the output and its contents are processed individually. Any other file is copied into the mod as-is (inside an MPQ its compression can be configured with a `<name>.config.json`, see [MPQ packages](#mpq-packages-mpq)). Files and folders starting with `.` are ignored, as are `config.json`/`*.config.json` configuration files.

## Building
`Compile` runs the build: sources are compiled into `.build/intermediates/` inside your project, and the final MPQ artifacts (if any) are written to `.build/artifacts/`. Artifacts are built to a staging folder and only replace the previous artifacts once the whole build succeeds, so a failed compile never leaves you without your last good build. Hashes of inputs and outputs are stored in `.build/meta.json` so unchanged sources are skipped on the next compile. `Clean` deletes the intermediates folder to force a full rebuild. `Extract` lets you browse the files in the MPQs configured in the settings (Manage Settings → MPQ Settings).

## Command line
Running `PyMOD.pyw` with a project path compiles it headlessly, printing the build log to the console:

```
PyMOD <project_path>
```

Use `--gui <project_path>` to open a project in the GUI instead.
