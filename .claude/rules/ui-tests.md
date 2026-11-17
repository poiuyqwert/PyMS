---
paths:
  - "PyMS/UITests/**"
---

# UI automation test harness

`PyMS/UITests/` holds in-process Tkinter UI automation tests — a separate top-level package, sibling of `Tests/`, so the main test discovery never imports them. `UITests/harness.py` provides `UITestCase`.

- `UITestCase.make_window(factory, extra_patches=())` builds a real main window with the default patches active (Config `_read`/`_write`, default theme, update check, recording tracer) so tests are deterministic and disk-free. Drive it *without* `startup()`/`mainloop()`; pump the event loop with the harness's `pump()` (it calls `UI.Misc.update_idletasks`/`update` explicitly so a window defining its own `update` method can't shadow the pump).
- `UITests/__init__.py` installs process-wide isolation (`UITests/isolation.py`) before any program code is imported: analytics is a no-op stub module, settings are never read from or written to `Settings/`, disk writes are blocked, and modal waits (`wait_window`/`wait_variable`, native message/file/color dialogs) are blocked. Exceptions raised inside Tk callbacks (bindings, `after` callbacks, widget commands — normally just printed as "Exception in Tkinter callback") are recorded too, via a patched `Tk.report_callback_exception`. `UITestCase` **fails** a test that wrote to disk, hit a modal, reported an error via `get_tracer().trace_error()`, or raised out of a Tk callback — even when the code under test swallowed it. So: mock saves/exports in memory (e.g. `mock.patch('builtins.open', mock.mock_open())` and assert on the written data), patch every dialog a test expects (e.g. `UI.WindowExtensions.grab_wait`, `tkinter.messagebox.*`), and use `self.take_traced_errors()` / `self.take_callback_exceptions()` in a test that deliberately triggers a traced error / callback exception. Subclasses overriding `setUp` must call `super().setUp()`.
- Teardown withdraws the window and its Toplevels and pumps before `destroy()` — on macOS Aqua a root destroyed without pumping leaves its native window on screen until the process exits.
- **Never create a throwaway second `Tk()` root** (e.g. to probe for a display) — on macOS Aqua a created-then-destroyed extra root corrupts the next root and segfaults the interpreter. Detect "no display" by catching `tkinter.TclError` when the window is constructed and raising `unittest.SkipTest` (the harness only skips when the error mentions the display; any other `TclError` is a real failure).
- Keyboard-shortcut tests need the window shown *and* focused: `deiconify()` + `focus_force()` + pump. Build shortcut event strings with the event patterns (e.g. `UI.Ctrl.n.event()`), which resolve to `<Command-n>` on macOS.
