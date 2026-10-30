
# Process-wide isolation for the UI tests, installed by `UITests/__init__.py` before
# any test module imports program code (several program modules have import-time
# side effects that the per-window patches in `harness.py` come too late for).
#
# - Analytics is replaced by a no-op stub module, so none of `Utilities/analytics.py`
#   runs (tracking setup, OS probing, saving a generated client id to settings).
# - Settings are never read from or written to `Settings/`, so every test sees the
#   defaults (including the default theme) regardless of the user's own settings.
# - Disk writes are blocked and recorded, so a test can't write files even when the
#   code under test swallows the resulting error.
# - Modal waits (`wait_window`/`wait_variable`, native message/file/color dialogs)
#   are blocked and recorded, so an unexpected dialog fails the test instead of
#   leaving a window waiting for a click.
# - The tracer is a recording stand-in, so errors the program reports through
#   `trace_error()` (and otherwise swallows) aren't silently lost.
#
# `harness.UITestCase` fails any test during which something was recorded.

import builtins
import importlib
import io
import os
import shutil
import sys
import tkinter
import tkinter.commondialog
import traceback
import types
from unittest import mock

from typing import Any, NoReturn


class Recorder:
	def __init__(self) -> None:
		self.entries: list[str] = []

	def record(self, entry: str) -> None:
		self.entries.append(entry)

	def mark(self) -> int:
		return len(self.entries)

	def since(self, mark: int) -> list[str]:
		return self.entries[mark:]

	def take(self, mark: int) -> list[str]:
		# Return and forget the entries recorded since `mark`, for a test that
		# deliberately triggers what is being recorded.
		entries = self.entries[mark:]
		del self.entries[mark:]
		return entries


DISK_WRITES = Recorder()
MODALS = Recorder()
TRACED_ERRORS = Recorder()


class RecordingTracer:
	# Stand-in for `trace._TRACER`: being non-None makes `setup_trace()` early-return
	# (no stdout/stderr redirect, no log file), and code that reports a swallowed
	# exception via `get_tracer().trace_error()` has it recorded rather than dropped.
	program_name = 'UITests'

	def trace_error(self) -> None:
		TRACED_ERRORS.record(traceback.format_exc())


TRACER = RecordingTracer()


def _block_write(kind: str, target: Any) -> NoReturn:
	DISK_WRITES.record(f'{kind} {target!r}')
	raise PermissionError(f'UI tests may not write to disk ({kind} {target!r})')

_real_open = builtins.open
def _guarded_open(file: Any, *args: Any, **kwargs: Any) -> Any:
	mode = args[0] if args else kwargs.get('mode', 'r')
	if not isinstance(file, int) and any(flag in mode for flag in 'wax+'):
		_block_write(f'open({mode!r})', file)
	return _real_open(file, *args, **kwargs)

_WRITE_FLAGS = os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_APPEND | os.O_TRUNC
_real_os_open = os.open
def _guarded_os_open(path: Any, flags: int, *args: Any, **kwargs: Any) -> int:
	if flags & _WRITE_FLAGS:
		_block_write('os.open', path)
	return _real_os_open(path, flags, *args, **kwargs)

def _blocked_write(kind: str) -> Any:
	def blocked(target: Any, *_args: Any, **_kwargs: Any) -> NoReturn:
		_block_write(kind, target)
	return blocked


def _blocked_modal(kind: str) -> Any:
	def blocked(*_args: Any, **_kwargs: Any) -> NoReturn:
		MODALS.record(kind)
		raise AssertionError(f'Unexpected modal in a UI test ({kind}); patch the dialog the test expects')
	return blocked


def _analytics_stub() -> types.ModuleType:
	class NoOpGA:
		def track(self, *_args: Any, **_kwargs: Any) -> None:
			pass

		def set_application(self, *_args: Any, **_kwargs: Any) -> 'NoOpGA':
			return self

	class GAScreen:
		def __init__(self, *_args: Any, **_kwargs: Any) -> None:
			pass

	module = types.ModuleType('PyMS.Utilities.analytics')
	module.__dict__.update(ga=NoOpGA(), GAScreen=GAScreen)
	return module


def install() -> None:
	for module in ('PyMS.Utilities.analytics', 'PyMS.Utilities.PyMSConfig', 'PyMS.Utilities.trace'):
		if module in sys.modules:
			raise RuntimeError(f'{module} was imported before the UI test isolation was installed')
	sys.modules['PyMS.Utilities.analytics'] = _analytics_stub()

	patches: list[Any] = [
		mock.patch('PyMS.Utilities.Config.Config._read', return_value={}),
		mock.patch('PyMS.Utilities.Config.Config._write', return_value=None),
		mock.patch.object(builtins, 'open', _guarded_open),
		mock.patch.object(io, 'open', _guarded_open),
		mock.patch.object(os, 'open', _guarded_os_open),
		mock.patch.object(tkinter.Misc, 'wait_window', _blocked_modal('wait_window')),
		mock.patch.object(tkinter.Misc, 'wait_variable', _blocked_modal('wait_variable')),
		# Every tkinter message box, file dialog, and color chooser shows through this.
		mock.patch.object(tkinter.commondialog.Dialog, 'show', _blocked_modal('native dialog')),
	]
	for name in ('makedirs', 'mkdir', 'remove', 'unlink', 'rename', 'renames', 'replace', 'rmdir', 'removedirs'):
		patches.append(mock.patch.object(os, name, _blocked_write(f'os.{name}')))
	for name in ('rmtree', 'copy', 'copy2', 'copyfile', 'copytree', 'move'):
		patches.append(mock.patch.object(shutil, name, _blocked_write(f'shutil.{name}')))
	# Installed for the life of the test process; never stopped.
	for patcher in patches:
		patcher.start()

	# `trace` creates the logs folder when imported. Import it now so that blocked
	# write happens (and is forgotten) here, not inside whichever test imports it first.
	importlib.import_module('PyMS.Utilities.trace')
	DISK_WRITES.take(0)
