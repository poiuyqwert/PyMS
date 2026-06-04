# PyMS

Cross-platform StarCraft: BroodWar modding suite. ~16 Tkinter GUI programs that edit the binary file formats used by the game (`.bin`, `.dat`, `.grp`, `.mpq`, `.tbl`, etc.), each with a matching command-line mode for compile/decompile workflows.

## Layout

Paths below are relative to this directory (the git repo root). The Python package lives in the `PyMS/` subdirectory. Internal imports are absolute from the package's parent, e.g. `from PyMS.Utilities import Assets`, so **this directory must be on `sys.path`** — which is why the `.pyw` entry points sit here, alongside the `PyMS/` package, rather than inside it.

- `*.pyw` — entry points, one per program (`PyAI.pyw`, `PyDAT.pyw`, ...). Each calls `check_compat(...)` then dispatches: no args → launch GUI; args → run the CLI via `optparse`.
- `PyMS/<Program>/` — GUI code for each program. `<Program>.py` holds the main window class; sibling files are dialogs, config, and program-specific logic.
- `PyMS/FileFormats/` — the heart of the project: readers/writers/encoders for every BroodWar binary format (`AIBIN`, `DAT`, `GRP`, `MPQ`, `TBL`, `Tileset`, `CHK`, `TRG`, `IScriptBIN`, ...). Editing-program logic should call into these, not reimplement parsing.
- `PyMS/Utilities/` — shared infrastructure: `UIKit/` (Tkinter widget wrappers, theming, syntax highlighting), `CodeHandlers/` (generic lexer/parser/compiler framework reused by AI/IScript script languages), `Config.py`/`PyMSConfig.py` (settings), `Assets.py` (resource paths), `IO.py`, `Struct.py` (binary struct helpers), `analytics.py`.
- `PyMS/Tests/` — `unittest` suite mirroring the format/utility modules.
- `PyMS/MPQ/`, `PyMS/Data/`, `PyMS/Images/`, `Palettes/`, `Help/` — bundled game data, assets, and Markdown help docs.
- `Settings/` — per-program runtime settings (`.txt`, JSON-ish). User-editable; not code.

## Environment

- Python **3.11–3.13** only (`check_compat` warns/blocks otherwise). `.python-version` pins 3.13.12 via pyenv.
- Runtime dep: **Pillow** (version pinned per Python version in `requirements.txt`).

## Conventions

- **Indentation is tabs** (`.editorconfig`: `indent_style = tab`), LF line endings, final newline. Match this exactly.
- **Prefer modern Python 3 features over their Python 2 equivalents** everywhere — f-strings instead of `%` formatting or `.format()`, modern type annotations (`def f(x: int) -> str:`, `list[int]`, `str | None`) instead of `# type:` comments, `super()` with no args, walrus, etc. New code should read as idiomatic Python 3.
- **Exception — Python 2-parseable files.** The `.pyw` entry points and any module imported at their top level (e.g. `PyMS.Utilities.Compatibility`) run *before* `check_compat()` can report "your Python version is unsupported." On Python 2 a syntax error would crash with a traceback instead of that friendly message, so these files must parse cleanly on Python 2. That means:
  - No f-strings — use `%` formatting or `.format()` (these files carry `# pylint: disable=consider-using-f-string`).
  - No type annotations in syntax — use the `# type: (...) -> ...` comment style instead of `def f(x: int) -> str:` or `x: int = 0`.
  - No other Python 3-only syntax: no `str | None` unions (use `# type: str | None` comments), no walrus `:=`, no `async`/`await`, no positional-only `/` params, no `yield from` reliance on 3-only behavior, no `nonlocal` edge cases, etc.
  - Keep heavy imports *inside* functions (as the existing `.pyw` files do), so only the minimal top-level module graph needs to satisfy this constraint.

  Keep this boundary tight: a single Python 3-only token anywhere in this import graph defeats the whole point of the version check. Everything reachable only at runtime (inside `main()`, the GUI classes, FileFormats, etc.) is free to use modern syntax.
- `pylint` is heavily relaxed (see disabled rules in `.vscode/settings.json`): things like `invalid-name`, `wildcard-import`, `line-too-long`, missing docstrings are intentionally off. Don't "fix" those.
- Many modules do `from ..Utilities.UIKit import *` — wildcard UIKit imports are the established pattern for GUI files.
- `versions.json` holds the per-program version numbers.
- Do not place any issue number references (like ISS-001 for example) in code/comments/tests
- Test names/comments should describe the invariant, not the bug

## Working notes

- A single program spans three layers: the `.pyw` entry point, the `PyMS/<Program>/` GUI, and the `PyMS/FileFormats/<Format>/` parser. Trace through all three when changing behavior.
- Most `PyMS/FileFormats/` modules do double duty: they parse/write the raw binary game file **and** serialize to / parse from a human-editable **text format** (the decompiled source the GUI and CLI round-trip — e.g. AI/IScript scripts, `.dat` text dumps, `.trg` triggers). The shared `PyMS/Utilities/CodeHandlers/` framework (lexer → parser → compiler → serializer) backs the scriptable ones.
- **This is the highest-risk surface in the project.** Both the binary and text formats round-trip real user data and real game files: a parsing change can silently corrupt saved work or produce files BroodWar can't load.
  - **Changes here must stay backwards compatible unless the task explicitly says otherwise.** Text that parsed before must still parse; binary that loaded before must still load. Don't rename, reorder, or repurpose existing tokens, keywords, or struct fields, and don't tighten parsing so previously-valid input now errors — add new syntax/fields additively.
  - Verify with round-trips: parse → serialize → parse should be stable, and binary load → save should stay byte-identical where it was before. Prefer adding/adjusting a `PyMS/Tests/` case over manual verification.
- Don't edit files under `Settings/`, `PyMS/Logs/`, or bundled data dirs as part of code changes — those are runtime/user state.
