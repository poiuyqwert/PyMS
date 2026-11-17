# Layout

The Python package lives in the `PyMS/` subdirectory. Internal imports are absolute from the package's parent, e.g. `from PyMS.Utilities import Assets`, so **this directory must be on `sys.path`** — which is why the `.pyw` entry points sit here, alongside the `PyMS/` package, rather than inside it.

- `*.pyw` — entry points, one per program (`PyAI.pyw`, `PyDAT.pyw`, ...). Each calls `check_compat(...)` then dispatches: no args → launch GUI; args → run the CLI via `optparse`.
- `PyMS/<Program>/` — GUI code for each program. `<Program>.py` holds the main window class; sibling files are dialogs, config, and program-specific logic.
- `PyMS/FileFormats/` — the heart of the project: readers/writers/encoders for every BroodWar binary format (`AIBIN`, `DAT`, `GRP`, `MPQ`, `TBL`, `Tileset`, `CHK`, `TRG`, `IScriptBIN`, ...).
- `PyMS/Utilities/` — shared infrastructure: `UIKit/` (Tkinter widget wrappers, theming, syntax highlighting), `CodeHandlers/` (generic lexer/parser/compiler framework for the script languages), `Config.py`/`PyMSConfig.py` (settings), `Assets.py` (resource paths), `IO.py`, `Struct.py` (binary struct helpers), `analytics.py`.
- `PyMS/Tests/` — `unittest` suite, one folder per source module.
- `PyMS/UITests/` — in-process Tkinter UI automation tests (separate package; `harness.py` provides `UITestCase`), one folder per program plus `UIKit/` and `Utilities/`.
- `PyMS/MPQ/`, `PyMS/Data/`, `PyMS/Images/`, `Palettes/`, `Help/` — bundled game data, assets, and Markdown help docs.
- `Settings/` — per-program runtime settings (`.txt`, JSON-ish). User-editable; not code.

A single program spans three layers: the `.pyw` entry point, the `PyMS/<Program>/` GUI, and the `PyMS/FileFormats/<Format>/` parser. Trace through all three when changing behavior.

Area-specific rules live in `.claude/rules/` and load when matching files are read: `code-structure.md` (where functions live, no superfluous abstractions, layering, keysyms, image types), `fileformats.md`, `py2-compat.md`, `tests.md`, `ui-tests.md`, `help-docs.md`.

# Environment

- Python **3.11–3.13** only (`check_compat` warns/blocks otherwise). `.python-version` pins 3.13.12 via pyenv.
- `pylint` and `mypy` for static analysis; `unittest` for tests.
- Runtime dep: `Pillow` (version pinned per Python version in `requirements.txt`).
- `pyenv` for managing python versions (always use pyenv to run python, pylint, mypy, and tests).

# Conventions

- **Indentation is tabs** (`.editorconfig`: `indent_style = tab`), LF line endings, final newline. Match this exactly.
- **Prefer modern Python 3 features** everywhere — f-strings, modern type annotations (`def f(x: int) -> str:`, `list[int]`, `str | None`), no-arg `super()`, walrus, etc.
- **Exception — Python 2-parseable files:** the `.pyw` entry points and modules imported at their top level (e.g. `PyMS.Utilities.Compatibility`) must parse on Python 2 so `check_compat()` can report an unsupported version. No f-strings, syntax annotations, or other 3-only syntax there — full rules in `.claude/rules/py2-compat.md`; read it before editing those files or adding a top-level import to them.
- `pylint` is heavily relaxed (see disabled rules in `.vscode/settings.json`): things like `invalid-name`, `line-too-long`, missing docstrings are intentionally off. Don't "fix" those.
- **No wildcard imports** (`from X import *`). The only exceptions are the public-API barrels (`Utilities/UIKit/__init__.py` plus its `Constants`/`Widgets` submodules, and `FileFormats/CHK/__init__.py`), each backed by an explicit literal `__all__` and a local `# pylint: disable=wildcard-import`.
- **Namespace vs. explicit imports.** When a file would pull a large share of a module's surface (more than ~5 names *and* ≥75% of its exports — and always for `UIKit`), import the module under an alias and qualify each use: `from ..Utilities import UIKit as UI` → `UI.Frame`, `from ..FileFormats import DAT` → `DAT.UnitsDAT`. Otherwise import the specific names explicitly: `from ..Widgets import Frame, Label`.
- **FileFormats are the highest-risk surface**: binary and text formats round-trip real user data and game files. Changes must stay backwards compatible unless the task says otherwise — see `.claude/rules/fileformats.md`.
- **Don't add superfluous abstractions:** no trivial helpers, single-value wrapper classes, parallel data tables, empty subclasses, type factories, single-use constants, or speculative caching/fallbacks. Self-audit every new function/class before reporting. Full rules are in `.claude/rules/code-structure.md`.
- Do not place any issue number references (like ISS-001 for example) in code/comments/tests.
- Don't edit files under `Settings/`, `PyMS/Logs/`, or bundled data dirs as part of code changes — those are runtime/user state.

# Help docs

Help docs are part of the deliverable, not a follow-up. Any change a user can see or feel ships with the matching `Help/` updates in the **same** change: a new feature or dialog, a renamed/moved menu item or button, a changed or added keyboard shortcut, a reworked workflow, a new/removed/renamed setting, changed format support or limits, and changed error/validation behavior a doc describes. Purely internal changes need no doc update — say so explicitly rather than silently skipping. Authoring rules (the in-app viewer supports a restricted Markdown subset) are in `.claude/rules/help-docs.md`.

# Development Workflow

## 1. Make changes

- If the functionality is testable, write tests to exercise all code paths (rules in `.claude/rules/tests.md`).
- If a bug is being fixed, write tests to exercise the bug first, and then implement the fix.
- If the change is visible to the user, update the affected `Help/` pages in the same change and run the help link test: `pyenv exec python -m unittest PyMS.Tests.Help.test_help_links`.

## 2. Run all tests

Run from this directory (the one containing the `.pyw` launchers and the `PyMS/` package):

- Full suite: `pyenv exec python -m unittest discover -t . -s PyMS/Tests -p 'test_*.py'` — the `-t .` matters; without it discovery imports tests as `Tests.*` and their relative imports fail.
- Single module: `pyenv exec python -m unittest PyMS.Tests.<Sub>.<test_module>`
- Single UI module: `pyenv exec python -m unittest PyMS.UITests.<Sub>.<test_module>` (e.g. `PyMS.UITests.PyPAL.test_clipboard`)
- One UI folder: `pyenv exec python -m unittest discover -t . -s PyMS/UITests/<Sub> -p 'test_*.py'`
- All UI automation tests (only when warranted — see below): `pyenv exec python -m unittest discover -t . -s PyMS/UITests -p 'test_*.py'`

Note: SFmpq tests are expected to fail on macOS at this time.

Choosing UI tests: the `PyMS/Tests` suite always runs in full, but the UITest suite is slow, so scope it to the change's surface area — work out which programs and widgets can actually reach the edited code, and run only those UITests:

- **Program-local change** (`PyMS/Py<PROG>/...`): run only `UITests/Py<PROG>/`, and if the change is confined to one dialog/tab, only the modules that exercise it (e.g. a PyGRAFT requirements-editor change runs `PyMS.UITests.PyGRAFT.test_requirements_editor` — no PyPAL tests).
- **Shared widget/dialog change** (`Utilities/UIKit/...`, shared dialogs, settings/theme code): run its `UITests/UIKit/` or `UITests/Utilities/` module, then grep for the widget's users and also run the UITests of programs that use it in the changed way.
- **Full UITest suite** only for broad changes: the harness/isolation (`UITests/harness.py`, `isolation.py`, `__init__.py`), theming or event-loop plumbing every window uses, `MainWindow`/shared base classes, refactors spanning many programs — or when asked.
- **No UI reachability** (e.g. FileFormats parsing no UI test drives, Help docs): no UITests needed.

When reporting results, say which UITest modules/folders ran and why the rest were skipped.

## 3. Static analysis

Run both `pylint` and `mypy`, fix all issues reported (do not use `# pylint: disable=<rule>` or `#type: ignore[<rule>]` to "fix" issues without checking with the user first).

- **Always run `pylint` with the arguments configured in `.vscode/settings.json`** (the `pylint.args` array — currently the `--disable=...` rule list and `--indent-string='\t'`), so the CLI matches the editor's behavior.
- **Check the whole affected surface, not just the files you edited.** Renaming or removing a public method (or changing its signature) has a blast radius of *every* caller, so after any such change run mypy package-wide: `pyenv exec mypy PyMS/`. (Don't add `*.pyw` — mypy aborts on the duplicate `__main__` modules.)
- **`.pyw` entry points are invisible to mypy's type inference** (they use `# type:` comments), so check `.pyw` callers of changed APIs by grepping.
- **Don't trust the incremental `.mypy_cache` when verifying a cross-cutting change.** It can report phantom errors from an intermediate state, or hide real ones. Verify with `pyenv exec mypy --no-incremental ...` (or `rm -rf .mypy_cache` first), and confirm any reported error by actually reading the cited line before acting on it.

## 4. Repeat steps 2 and 3 until all tests pass and no static analysis issues remain
