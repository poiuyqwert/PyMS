
import contextlib
from tkinter import TclError
import unittest
from unittest import mock

from ..Utilities import UIKit as UI
from ..Utilities.UIKit.EventPattern import EventPattern

from typing import Any, Callable, TypeVar

W = TypeVar('W', bound=UI.WindowExtensions)

# A non-None stand-in for the trace module's installed-tracer global; see below.
_TRACE_SENTINEL = mock.MagicMock()

# `target -> mock.patch(**kwargs)` applied around every window construction. PyMS
# main windows reach out to the world in `__init__` — read/write settings, fire
# analytics, check for updates over the network, and install a stdout/stderr
# tracer that logs to disk. Neutralizing those keeps a UI test deterministic and
# disk-free (the project forbids tests writing data to disk). Keyed by target so
# each patch site is unique and `extra_patches` can override a default by path.
#   - `Config._read` returns an empty dict so settings fall back to defaults
#     without touching `Settings/`; `_write` is a no-op so a stray `save()` can't.
#   - `trace._TRACER` is set non-None so `setup_trace()` early-returns for every
#     program. Patching the module global (not the function) works regardless of
#     how each program imports `setup_trace`, and avoids redirecting stdout/stderr.
_DEFAULT_PATCHES: dict[str, dict[str, Any]] = {
	'PyMS.Utilities.Config.Config._read': {'return_value': {}},
	'PyMS.Utilities.Config.Config._write': {'return_value': None},
	'PyMS.Utilities.UpdateDialog.UpdateDialog.check_update': {'return_value': None},
	'PyMS.Utilities.analytics.ga.track': {'return_value': None},
	'PyMS.Utilities.analytics.ga.set_application': {'return_value': None},
	'PyMS.Utilities.trace._TRACER': {'new': _TRACE_SENTINEL},
}


class UITestCase(unittest.TestCase):
	# Base for in-process Tkinter UI tests: it builds a real main window (without
	# entering `mainloop`), drives it through real widget seams, and asserts on
	# widget and model state. Subclasses call `make_window(...)` then act with the
	# `shortcut`/`click`/`invoke` helpers, pumping the event loop with `pump`.

	def make_window(self, factory: Callable[[], W], extra_patches: dict[str, dict[str, Any]] | None = None) -> W:
		# Build a window with `_DEFAULT_PATCHES` (plus any program-specific
		# `extra_patches`, which override a default sharing the same target path)
		# active for the whole test, then settle the event loop. The window is
		# destroyed and the patches lifted automatically on teardown.
		#
		# Tk needs a display connection; without one (headless shell, no window
		# server) constructing the window raises TclError. Translate that into a
		# skip rather than a failure so `unittest discover` stays green in
		# environments that can't show a window. A single throwaway root cannot be
		# used to probe up front — on macOS Aqua a created-then-destroyed extra
		# root corrupts a subsequently created root and segfaults the interpreter.
		# Fonts are pooled per Tk interpreter; this test is about to build a fresh
		# root, so drop any instances pooled against an earlier test's (now
		# destroyed) root before they are looked up against the new one.
		UI.Font.clear_pool()
		patches = {**_DEFAULT_PATCHES, **(extra_patches or {})}
		stack = contextlib.ExitStack()
		self.addCleanup(stack.close)
		for target, kwargs in patches.items():
			stack.enter_context(mock.patch(target, **kwargs))
		try:
			window = factory()
		except TclError as e:
			raise unittest.SkipTest(f'No display available for Tk: {e}')
		self.addCleanup(self._destroy, window)
		self.pump(window)
		return window

	def _destroy(self, window: UI.WindowExtensions) -> None:
		try:
			window.destroy()
		except TclError:
			pass

	def pump(self, widget: UI.Misc, count: int = 2) -> None:
		# Flush queued events, idle tasks, and geometry so the UI reflects the
		# action just performed — what `mainloop()` does per frame.
		for _ in range(count):
			widget.update_idletasks()
			widget.update()

	def show(self, window: UI.WindowExtensions) -> None:
		# Map and focus the window so a synthesized key event reaches it: toolbar
		# shortcuts both short-circuit on non-viewable buttons and (being key
		# events) route to the focused widget. A test driving an action via its
		# shortcut must show the window first.
		window.deiconify()
		self.pump(window)
		window.focus_force()
		self.pump(window)

	def shortcut(self, window: UI.Misc, pattern: EventPattern) -> None:
		window.event_generate(pattern.event())
		self.pump(window)

	def click(self, widget: UI.Misc, x: int, y: int, pattern: EventPattern = UI.Mouse.Click_Left) -> None:
		widget.event_generate(pattern.event(), x=x, y=y)
		self.pump(widget)

	def invoke(self, button: UI.Button) -> None:
		button.invoke()
		self.pump(button)

	def invoke_menu(self, menu: UI.Menu, index: int) -> None:
		menu.invoke(index)
		self.pump(menu)
