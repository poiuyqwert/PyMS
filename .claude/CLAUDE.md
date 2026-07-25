# Layout

The Python package lives in the `PyMS/` subdirectory. Internal imports are absolute from the package's parent, e.g. `from PyMS.Utilities import Assets`, so **this directory must be on `sys.path`** — which is why the `.pyw` entry points sit here, alongside the `PyMS/` package, rather than inside it.

- `*.pyw` — entry points, one per program (`PyAI.pyw`, `PyDAT.pyw`, ...). Each calls `check_compat(...)` then dispatches: no args → launch GUI; args → run the CLI via `optparse`.
- `PyMS/<Program>/` — GUI code for each program. `<Program>.py` holds the main window class; sibling files are dialogs, config, and program-specific logic.
- `PyMS/FileFormats/` — the heart of the project: readers/writers/encoders for every BroodWar binary format (`AIBIN`, `DAT`, `GRP`, `MPQ`, `TBL`, `Tileset`, `CHK`, `TRG`, `IScriptBIN`, ...). Editing-program logic should call into these, not reimplement parsing.
- `PyMS/Utilities/` — shared infrastructure: `UIKit/` (Tkinter widget wrappers, theming, syntax highlighting), `CodeHandlers/` (generic lexer/parser/compiler framework reused by AI/IScript script languages), `Config.py`/`PyMSConfig.py` (settings), `Assets.py` (resource paths), `IO.py`, `Struct.py` (binary struct helpers), `analytics.py`.
- `PyMS/Tests/` — `unittest` suite mirroring the format/utility modules.
- `PyMS/UITests/` — in-process Tkinter UI automation tests (a separate top-level package, sibling of `Tests/`, so the main test discovery never imports them). `UITests/harness.py` provides `UITestCase`.
- `PyMS/MPQ/`, `PyMS/Data/`, `PyMS/Images/`, `Palettes/`, `Help/` — bundled game data, assets, and Markdown help docs.
- `Settings/` — per-program runtime settings (`.txt`, JSON-ish). User-editable; not code.

# Environment

- Python **3.11–3.13** only (`check_compat` warns/blocks otherwise). `.python-version` pins 3.13.12 via pyenv.
- `pylint` and `mypy` for static analysis
- `unittest` framework for tests
- Runtime dep: `Pillow` (version pinned per Python version in `requirements.txt`).
- `pyenv` for managing python versions (always use pyenv to run python, pylint, mypy, and tests)

# Conventions

- **Indentation is tabs** (`.editorconfig`: `indent_style = tab`), LF line endings, final newline. Match this exactly.
- **Prefer modern Python 3 features over their Python 2 equivalents** everywhere — f-strings instead of `%` formatting or `.format()`, modern type annotations (`def f(x: int) -> str:`, `list[int]`, `str | None`) instead of `# type:` comments, `super()` with no args, walrus, etc. New code should read as idiomatic Python 3.
- **Exception — Python 2-parseable files.** The `.pyw` entry points and any module imported at their top level (e.g. `PyMS.Utilities.Compatibility`) run *before* `check_compat()` can report "your Python version is unsupported." On Python 2 a syntax error would crash with a traceback instead of that friendly message, so these files must parse cleanly on Python 2. That means:
  - No f-strings — use `%` formatting or `.format()` (these files carry `# pylint: disable=consider-using-f-string`).
  - No type annotations in syntax — use the `# type: (...) -> ...` comment style instead of `def f(x: int) -> str:` or `x: int = 0`.
  - No other Python 3-only syntax: no `str | None` unions (use `# type: str | None` comments), no walrus `:=`, no `async`/`await`, no positional-only `/` params, no `yield from` reliance on 3-only behavior, no `nonlocal` edge cases, etc.
  - Keep heavy imports *inside* functions (as the existing `.pyw` files do), so only the minimal top-level module graph needs to satisfy this constraint.

  Keep this boundary tight: a single Python 3-only token anywhere in this import graph defeats the whole point of the version check. Everything reachable only at runtime (inside `main()`, the GUI classes, FileFormats, etc.) is free to use modern syntax.
- `pylint` is heavily relaxed (see disabled rules in `.vscode/settings.json`): things like `invalid-name`, `line-too-long`, missing docstrings are intentionally off. Don't "fix" those.
- **Always run `pylint` with the arguments configured in `.vscode/settings.json`** (the `pylint.args` array — currently the `--disable=...` rule list and `--indent-string='\t'`). Pass those exact arguments on the command line so the CLI matches the editor's behavior; otherwise pylint will report rules that are intentionally disabled for this project.
- **No wildcard imports** (`from X import *`) — `wildcard-import` is enabled in pylint. The only exceptions are the public-API barrels (`Utilities/UIKit/__init__.py` plus its `Constants`/`Widgets` submodules, and `FileFormats/CHK/__init__.py`): they re-export deliberately, each backed by an explicit (literal) `__all__` and a local `# pylint: disable=wildcard-import`.
- **Namespace vs. explicit imports.** When a file would pull a large share of a module's surface (rule of thumb: more than ~5 names *and* ≥75% of its exports — and always for `UIKit`), import the module under an alias and qualify each use: `from ..Utilities import UIKit as UI` → `UI.Frame`, `from ..FileFormats import DAT` → `DAT.UnitsDAT` (mirrors the existing `Assets` convention). Otherwise import the specific names explicitly: `from ..Widgets import Frame, Label`.
- **Key event checks compare keysyms**: `Keysym(event.keysym) == Key.Return` (via the barrel: `UI.Keysym(...) == UI.Key.Return`). Never compare `event.keycode` to numbers (platform-specific — Return is 13 on Windows, 36 on macOS) or `event.keysym` to `.name()`/string literals. A keysym alone can't verify modifiers, so `== Ctrl.Return` is always False — modifier combos need real event bindings.
- **Image types.** `PIL.Image` is for pixel construction only (FileFormats) — never handed to widgets. FileFormats converters (`GRP.frame_to_photo`, `Tileset.megatile_to_photo`/`minitile_to_photo`, `FNT.letter_to_photo`, ...) return plain `ImageTk.PhotoImage` so callers need no casts. `tkinter.PhotoImage` is only for bundled GIF assets (`Assets.get_image`) and UIKit component icon params. For GUI-layer annotations meaning "any displayable image" (caches, delegate protocols, `Canvas.create_image`) use `UI.AnyPhotoImage` (= `tk.PhotoImage | ImageTk.PhotoImage`, in `UIKit/Types.py`) — prefer it over `UI.ImageTk.PhotoImage`, which needs a `type: ignore`. Don't reintroduce `tkinter.Image`/`BitmapImage` or casts between image types. Gotchas: `Assets.py` must import `AnyPhotoImage` under `if TYPE_CHECKING:` (a runtime import from the UIKit barrel is circular), and keep strong references to Tk images (e.g. caches like `canvas_images`) or Tk garbage-collects them out from under widgets.
- Do not place any issue number references (like ISS-001 for example) in code/comments/tests
- Test names/comments should describe the invariant, not the bug
- **Tests that assert a `PyMSError` is raised must validate it's the *expected* error**, not just that some `PyMSError` occurred. Capture the exception and assert on a distinctive substring of its message — bare `with self.assertRaises(PyMSError):` is not enough:
  ```python
  with self.assertRaises(PyMSError) as cm:
      some_call()
  self.assertIn('<distinctive part of the expected message>', str(cm.exception))
  ```
  Pick a stable substring (prefer the static, non-interpolated part of the `raise PyMSError('Type', '...')` message, specific enough to identify that error path), and run the test to confirm it matches the actual message.
- **Tests must not write generated test data to disk.** Don't create temp files/dirs (or write into `Settings/`, bundled data, etc.) to feed or capture test data. Instead keep it in-memory: use the `Utilities/IO.py` helpers (`IO.InputText`/`IO.InputBytes` accept a path, a file-like object, *or* a raw `str`/`bytes`; `IO.output_to_text`/`IO.output_to_bytes` capture a writer's output), `io.StringIO`/`io.BytesIO`, or `unittest.mock` to stub the I/O boundary. When a class reads/writes files through a small overridable seam (e.g. `Config._read`/`_write`), mock that method to supply or capture data rather than going through the filesystem. Reading committed read-only fixtures under `PyMS/Tests/` is fine; producing new on-disk files during a test run is not.

# Help docs (`Help/`)

Help content is Markdown rendered in two places: on GitHub, and in-app by the custom viewer (`PyMS/Utilities/Markdown.py` + `MarkdownView.py`). Every page must render correctly and have working links in **both**.

## When to update

Help docs are part of the deliverable, not a follow-up. Any change a user can see or feel ships with the matching `Help/` updates in the **same** change: a new feature or dialog, a renamed/moved menu item or button, a changed or added keyboard shortcut, a reworked workflow, a new/removed/renamed setting, changed format support or limits, and changed error/validation behavior a doc describes.

- Find the affected pages by grepping `Help/` for the program name, feature name, menu label, or shortcut you touched — don't assume one page. Coverage spans `Help/Programs/<Program>.md` plus its `Help/Programs/<Program>/` sub-pages, `Help/Files/` (format/reference pages, e.g. command and field references), and `Help/Tutorials/` (step-by-step walkthroughs, which go stale fastest because they name concrete UI elements).
- Reference pages that mirror a registry (command references, `.dat` field lists) must be re-checked against the code when the registry changes — a new command or field is a doc change too.
- Purely internal changes (refactors, perf, parser internals with no visible difference) need no doc update — say so explicitly rather than silently skipping.

## Authoring rules

Write GitHub Flavored Markdown restricted as follows:

- **Never use** (unsupported by the in-app parser): tables, raw HTML, setext headings (ATX `#` only), reference links (`[text][ref]`), autolinks (`<url>`/bare URLs — always `[text](url)`), task lists, footnotes, and backslash escapes (use a code span to show a literal `*`, `_`, etc.).
- **Also avoid** (parsed but rendered wrong in-app): thematic breaks (`---` renders as nothing), block quotes (`>` renders as an unstyled paragraph), and italic/strikethrough (markers are stripped but no styling applied — `**bold**` is the only emphasis that renders).
- **Links**: cross-page links are root-absolute with the `.md` extension, e.g. `[units.dat](/Help/Files/DAT/units.dat.md)` or `[...](/Help/Files/iscript.bin.md#animations)` — the in-app resolver (`Assets.HelpFolder.index()`) only accepts `/Help/...` paths, and GitHub resolves them too. File-relative links (`PyAI.md`, `../Files/GRP.md`) are silently dead in-app. Same-page links are `[text](#anchor)`. External links need an explicit scheme (`https://...`). Never put a code span inside link text (it's parsed first and destroys the link).
- **Heading anchors**: the in-app slugger (`ATXHeading.anchor()`) matches GitHub's: lowercase; letters, digits, underscores, hyphens, and spaces are kept (all other punctuation dropped, including backticks — a code-span heading like `` ### `wait_build` `` anchors as `#wait_build`); spaces become hyphens. Heading text must be unique within its file: GitHub deduplicates repeated headings with `-1` suffixes, but the in-app viewer does not. The underscore rule from the Code bullet applies to headings too — put identifiers with underscores in code spans, or paired `_` will be eaten as italic markers and change both the rendering and the anchor.
- **Paragraphs**: the in-app viewer turns every source newline into a line break (GitHub joins them with a space), so keep each paragraph on a single source line. For a deliberate break inside a paragraph end the line with two trailing spaces — never `\`, which renders literally.
- **Lists**: number ordered lists sequentially from `1.` (the in-app viewer numbers by position, ignoring source numbers). Indent nested lists/continuation lines to the parent item's text column — unindented (lazy) continuation closes the list in-app. At most 3 nesting levels render distinctly.
- **Code**: fenced and 4-space-indented blocks both work; a fence language is ignored in-app but fine for GitHub highlighting. Code blocks don't wrap in-app, so keep lines short. Write keyboard shortcuts as code spans in Windows form (`` `Ctrl+Shift+A` ``) — the viewer converts them to Mac symbols automatically. Put identifiers containing underscores in code spans (`some_var_name` would otherwise be mis-italicized in-app).
- **Images**: `![alt](/Help/path/image.png)` — resolved under `Help/` by `Assets.help_image()`, file extension required; alt/title become the tooltip.

## Anchor and link stability

The `Help/` pages are read on GitHub, so every heading is a public URL people link to and share. **Treat existing heading text and page paths as a stable API** and make a best effort to keep them as-is:

- Prefer editing a section's body over re-titling it, and prefer adding a new heading over renaming an existing one. Rewording a heading changes its anchor (see the Heading anchors rule) and breaks every external link to it.
- Don't rename or move a `.md` file, or reshuffle a page's heading hierarchy, for tidiness alone. Adding new sections is free — it doesn't disturb existing anchors.
- If a rename/move really is required, update every in-repo link to it (the link test finds the broken ones) and call out in your report that previously shared external links will break.

## Validating links

Any change to a heading, a link, an image path, or a page filename must be verified with the link validation test:

```
pyenv exec python -m unittest PyMS.Tests.Help.test_help_links
```

It parses every `Help/**/*.md` with `Markdown.Document.parse` and checks that links are same-page `#anchor`, root-absolute `/Help/....md`, or external with a scheme; that cross-page targets resolve through `Assets.help_tree().index()`; that every `#anchor` matches a real heading in the target page; that heading anchors are unique per page; and that image paths point at files that exist. It's part of the full suite, but run it directly after touching docs — it's fast and names the offending page and link.

# Working notes

- A single program spans three layers: the `.pyw` entry point, the `PyMS/<Program>/` GUI, and the `PyMS/FileFormats/<Format>/` parser. Trace through all three when changing behavior.
- Most `PyMS/FileFormats/` modules do double duty: they parse/write the raw binary game file **and** serialize to / parse from a human-editable **text format** (the decompiled source the GUI and CLI round-trip — e.g. AI/IScript scripts, `.dat` text dumps, `.trg` triggers). The shared `PyMS/Utilities/CodeHandlers/` framework (lexer → parser → compiler → serializer) backs the scriptable ones.
- **This is the highest-risk surface in the project.** Both the binary and text formats round-trip real user data and real game files: a parsing change can silently corrupt saved work or produce files BroodWar can't load.
  - **Changes here must stay backwards compatible unless the task explicitly says otherwise.** Text that parsed before must still parse; binary that loaded before must still load. Don't rename, reorder, or repurpose existing tokens, keywords, or struct fields, and don't tighten parsing so previously-valid input now errors — add new syntax/fields additively.
  - Verify with round-trips: parse → serialize → parse should be stable, and binary load → save should stay byte-identical where it was before. Prefer adding/adjusting a `PyMS/Tests/` case over manual verification.
- Don't edit files under `Settings/`, `PyMS/Logs/`, or bundled data dirs as part of code changes — those are runtime/user state.

# Development Workflow

## 1. Make changes

- If the functionality is testable, write tests to exercise all code paths.
- If a bug is being fixed, write tests to exercise the bug first, and then implement the fix
- If the change is visible to the user, update the affected `Help/` pages in the same change and run the help link test — see **Help docs (`Help/`)**.

## 2. Run all tests

Run from this directory (the one containing the `.pyw` launchers and the `PyMS/` package):

- Full suite: `pyenv exec python -m unittest discover -t . -s PyMS/Tests -p 'test_*.py'` — the `-t .` matters; without it discovery imports tests as `Tests.*` and their relative imports fail.
- Single module: `pyenv exec python -m unittest PyMS.Tests.<Sub>.<test_module>`
- UI automation tests: `pyenv exec python -m unittest discover -t . -s PyMS/UITests -p 'test_*.py'`

Note: SFmpq tests are expected to fail on macOS at this time

UI automation test notes (see `PyMS/UITests/harness.py`):

- `UITestCase.make_window(factory, extra_patches=())` builds a real main window with the default patches active (Config `_read`/`_write`, analytics, update check) so tests are deterministic and disk-free. Drive it *without* `startup()`/`mainloop()`; pump the event loop with the harness's `pump()` (it calls `UI.Misc.update_idletasks`/`update` explicitly so a window defining its own `update` method can't shadow the pump).
- **Never create a throwaway second `Tk()` root** (e.g. to probe for a display) — on macOS Aqua a created-then-destroyed extra root corrupts the next root and segfaults the interpreter. Detect "no display" by catching `tkinter.TclError` when the window is constructed and raising `unittest.SkipTest`.
- Keyboard-shortcut tests need the window shown *and* focused: `deiconify()` + `focus_force()` + pump. Build shortcut event strings with the event patterns (e.g. `UI.Ctrl.n.event()`), which resolve to `<Command-n>` on macOS.

## 3. Static analysis

Run both `pylint` and `mypy`, fix all issues reported (do not use `# pylint: disable=<rule>` or `#type: ignore[<rule>]` to "fix" issues without checking with the user first)

- **Check the whole affected surface, not just the files you edited.** A change to a public method/class/signature can break callers in files you never opened. Renaming or removing a public method (or changing its signature) has a blast radius of *every* caller, so a file-scoped `mypy` run cannot see the breakage. After any such change, run mypy package-wide — `pyenv exec mypy --no-incremental PyMS/` — not just on the changed module. (Don't pass multiple `.pyw` files in one run: mypy maps each script to module `__main__` and aborts with a duplicate-module error. Check `.pyw` files one at a time, or by reading/grepping as below.)
- **Don't trust the incremental `.mypy_cache` when verifying a cross-cutting change.** It can report phantom errors from an intermediate state, or hide real ones. Verify with `pyenv exec mypy --no-incremental ...` (or `rm -rf .mypy_cache` first), and confirm any reported error by actually reading the cited line before acting on it.
- **`.pyw` entry points are invisible to mypy's type inference.** They use the Python-2 `# type:` comment style, so mypy usually can't infer instance types and therefore won't flag calls to renamed/removed methods there. Check `.pyw` callers by reading/grepping, not by relying on mypy.

## 4. Repeat steps 2 and 3 until all tests pass and no static analysis issues remain
