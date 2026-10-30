
import contextlib
import tkinter
from tkinter import TclError
import unittest
from unittest import mock

from . import isolation
from ..Utilities import UIKit as UI
from ..Utilities.UIKit.EventPattern import EventPattern

from typing import Any, Callable, TypeVar

W = TypeVar('W', bound=UI.WindowExtensions)

# `target -> mock.patch(**kwargs)` applied around every window construction. PyMS
# main windows reach out to the world in `__init__` — read/write settings, apply the
# user's theme, check for updates over the network, and install a stdout/stderr
# tracer that logs to disk. Neutralizing those keeps a UI test deterministic and
# disk-free (the project forbids tests writing data to disk). Keyed by target so
# each patch site is unique and `extra_patches` can override a default by path.
# Analytics, settings files, disk writes and modal waits are also isolated for the
# whole test process by `isolation.py`.
#   - `Config._read` returns an empty dict so settings fall back to defaults
#     without touching `Settings/`; `_write` is a no-op so a stray `save()` can't.
#   - `Theme._THEME` is cleared so every window gets the default (unthemed) look.
#   - `trace._TRACER` is set non-None so `setup_trace()` early-returns for every
#     program. Patching the module global (not the function) works regardless of
#     how each program imports `setup_trace`, and avoids redirecting stdout/stderr.
#     It records `trace_error()` calls, which fail the test.
_DEFAULT_PATCHES: dict[str, dict[str, Any]] = {
	'PyMS.Utilities.Config.Config._read': {'return_value': {}},
	'PyMS.Utilities.Config.Config._write': {'return_value': None},
	'PyMS.Utilities.UpdateDialog.UpdateDialog.check_update': {'return_value': None},
	'PyMS.Utilities.UIKit.Theme._THEME': {'new': None},
	'PyMS.Utilities.trace._TRACER': {'new': isolation.TRACER},
}


class UITestCase(unittest.TestCase):
	# Base for in-process Tkinter UI tests: it builds a real main window (without
	# entering `mainloop`), drives it through real widget seams, and asserts on
	# widget and model state. Subclasses call `make_window(...)` then act with the
	# `shortcut`/`click`/`invoke` helpers, pumping the event loop with `pump`.
	# Subclasses overriding `setUp` must call `super().setUp()`.

	def setUp(self) -> None:
		# Fail the test if, while it ran, anything wrote to disk, waited on a modal,
		# or reported an error through the tracer (see `isolation.py`). Registered
		# first so it runs last, after the window is destroyed.
		self._traced_errors_mark = isolation.TRACED_ERRORS.mark()
		marks = (isolation.DISK_WRITES.mark(), isolation.MODALS.mark(), self._traced_errors_mark)
		self.addCleanup(self._assert_isolated, *marks)

	def take_traced_errors(self) -> list[str]:
		# The tracebacks reported through the tracer so far in this test, which no
		# longer fail it. For tests that deliberately exercise a swallowed error.
		return isolation.TRACED_ERRORS.take(self._traced_errors_mark)

	def _assert_isolated(self, disk_writes_mark: int, modals_mark: int, traced_errors_mark: int) -> None:
		problems: list[str] = []
		problems.extend(f'Wrote to disk: {entry}' for entry in isolation.DISK_WRITES.take(disk_writes_mark))
		problems.extend(f'Waited on a modal: {entry}' for entry in isolation.MODALS.take(modals_mark))
		problems.extend(f'Traced error:\n{entry}' for entry in isolation.TRACED_ERRORS.take(traced_errors_mark))
		if problems:
			self.fail('\n'.join(problems))

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
			if 'display' in str(e):
				raise unittest.SkipTest(f'No display available for Tk: {e}')
			# A real error, not a missing display: don't leave a half built root
			# alive to leak into later tests.
			root = getattr(tkinter, '_default_root', None)
			if root is not None:
				self._destroy(root)
			raise
		self.addCleanup(self._destroy, window)
		# Windows stay concealed until `startup()`, which tests don't call; reveal
		# so tests interact with a visible window (keyboard focus needs one).
		window.reveal()
		self.pump(window)
		return window

	def _destroy(self, window: UI.WindowExtensions | tkinter.Tk) -> None:
		# On macOS Aqua, destroying a root without pumping the event loop again
		# leaves its native window (and any dialogs) on screen until the process
		# exits. Hide them and let the event loop order them out while the
		# interpreter still exists, then destroy.
		try:
			for toplevel in reversed(self._toplevels(window)):
				toplevel.withdraw()
			window.withdraw()
			UI.Misc.update_idletasks(window)
			UI.Misc.update(window)
		except Exception:
			pass
		try:
			window.destroy()
		except Exception:
			pass

	def _toplevels(self, widget: tkinter.Misc) -> list[tkinter.Toplevel]:
		toplevels: list[tkinter.Toplevel] = []
		for child in widget.winfo_children():
			if isinstance(child, tkinter.Toplevel):
				toplevels.append(child)
			toplevels.extend(self._toplevels(child))
		return toplevels

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
