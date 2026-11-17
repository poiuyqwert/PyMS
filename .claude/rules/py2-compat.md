---
paths:
  - "*.pyw"
  - "PyMS/Utilities/Compatibility.py"
---

# Python 2-parseable files

The `.pyw` entry points and any module imported at their top level (e.g. `PyMS.Utilities.Compatibility`) run *before* `check_compat()` can report "your Python version is unsupported." On Python 2 a syntax error would crash with a traceback instead of that friendly message, so these files must parse cleanly on Python 2. That means:

- No f-strings — use `%` formatting or `.format()` (these files carry `# pylint: disable=consider-using-f-string`).
- No type annotations in syntax — use the `# type: (...) -> ...` comment style instead of `def f(x: int) -> str:` or `x: int = 0`.
- No other Python 3-only syntax: no `str | None` unions (use `# type: str | None` comments), no walrus `:=`, no `async`/`await`, no positional-only `/` params, no `yield from` reliance on 3-only behavior, no `nonlocal` edge cases, etc.
- Keep heavy imports *inside* functions (as the existing `.pyw` files do), so only the minimal top-level module graph needs to satisfy this constraint.

Keep this boundary tight: a single Python 3-only token anywhere in this import graph defeats the whole point of the version check. Everything reachable only at runtime (inside `main()`, the GUI classes, FileFormats, etc.) is free to use modern syntax.

`.pyw` entry points are invisible to mypy's type inference: they use `# type:` comments, so mypy usually can't infer instance types and won't flag calls to renamed/removed methods there. Check `.pyw` callers by reading/grepping.
