
import time
from unittest import mock

from ..harness import UITestCase

from ...Utilities import UIKit as UI
from ...Utilities.PyMSConfig import PYMS_CONFIG
from ...Utilities.PyMSError import PyMSError
from ...Utilities.UpdateDialog import UpdateDialog, ChangeLogDialog

from typing import Any, Callable

# The harness neutralizes the automatic check for every window it builds, so
# keep a handle on the real one to test it directly.
check_update = UpdateDialog.check_update

INSTALLED = {'PyMS': '1.2.0', 'PyTest': '2.0.0'}
CURRENT = dict(INSTALLED)
NEWER = {'PyMS': '1.3.0', 'PyTest': '2.1.0'}

def installed_version(program: str) -> str:
	return INSTALLED[program]


class _Host(UI.MainWindow):
	pass


class _DeferredThread:
	# Stands in for the worker thread: `start` queues the target for the test to run
	# on the main thread. A real thread could garbage collect Tk objects left over
	# from earlier tests off the main thread, which aborts the interpreter.
	def __init__(self, pending: list[Callable[[], None]], target: Callable[[], None], **_kwargs: Any) -> None:
		self.pending = pending
		self.target = target

	def start(self) -> None:
		self.pending.append(self.target)


class Test_UpdateDialog(UITestCase):
	def setUp(self) -> None:
		super().setUp()
		self.pending: list[Callable[[], None]] = []
		for patcher in (
			mock.patch.object(UI.WindowExtensions, 'grab_wait', lambda self: None),
			mock.patch.object(UpdateDialog, 'POLL_MS', 1),
			mock.patch('PyMS.Utilities.Assets.version', installed_version),
			mock.patch.dict(PYMS_CONFIG.reminder.pyms_version.data, clear=True),
			mock.patch('PyMS.Utilities.UpdateDialog.Thread', lambda **kwargs: _DeferredThread(self.pending, **kwargs)),
		):
			patcher.start()
			self.addCleanup(patcher.stop)
		self.window = self.make_window(_Host)
		# Tk reports callback exceptions and carries on, which would hide failures in the result poll
		callback_errors: list[BaseException] = []
		self.window.report_callback_exception = lambda _type, error, _tb: callback_errors.append(error) # type: ignore[method-assign]
		self.addCleanup(lambda: self.assertEqual(callback_errors, []))

	def fetch_returns(self, *results: dict[str, str] | Exception) -> None:
		# Each fetch consumes the next result
		remaining = list(results)
		def fetch() -> dict[str, str]:
			result = remaining.pop(0)
			if isinstance(result, Exception):
				raise result
			return result
		patcher = mock.patch.object(UpdateDialog, 'fetch_versions', side_effect=fetch)
		patcher.start()
		self.addCleanup(patcher.stop)

	def run_fetches(self) -> None:
		while self.pending:
			self.pending.pop(0)()

	def settle(self, run_fetches: bool = True) -> None:
		# Let any finished fetch be delivered by the result poll
		if run_fetches:
			self.run_fetches()
		deadline = time.monotonic() + 0.05
		while time.monotonic() < deadline:
			self.pump(self.window)
			time.sleep(0.005)

	def wait_until(self, condition: Callable[[], bool]) -> None:
		self.run_fetches()
		deadline = time.monotonic() + 5
		while not condition():
			self.assertLess(time.monotonic(), deadline, 'Timed out waiting for the update check')
			self.pump(self.window)
			time.sleep(0.005)

	def dialogs(self) -> list[UpdateDialog]:
		return [child for child in self.window.winfo_children() if isinstance(child, UpdateDialog)]

	def descendants(self, widget: UI.Misc) -> list[UI.Misc]:
		result: list[UI.Misc] = []
		for child in widget.winfo_children():
			result.append(child)
			result.extend(self.descendants(child))
		return result

	def text(self, dialog: UpdateDialog | ChangeLogDialog) -> str:
		return '\n'.join(str(widget.cget('text')) for widget in self.descendants(dialog.body) if isinstance(widget, UI.Label) and not isinstance(widget, UI.Hotlink))

	def buttons(self, dialog: UpdateDialog | ChangeLogDialog) -> dict[str, UI.Button]:
		return {str(widget.cget('text')): widget for widget in self.descendants(dialog.body) if isinstance(widget, UI.Button)}

	def has_checkbox(self, dialog: UpdateDialog) -> bool:
		return any(isinstance(widget, UI.Checkbutton) for widget in self.descendants(dialog.body))

	def manual_check(self) -> UpdateDialog:
		dialog = UpdateDialog(self.window, 'PyTest')
		self.pump(self.window)
		return dialog

	def wait_for_result(self, dialog: UpdateDialog) -> None:
		self.wait_until(lambda: 'Checking for updates' not in self.text(dialog))

	# Manual check

	def test_manual_check_shows_loading_until_the_check_finishes(self) -> None:
		self.fetch_returns(CURRENT)
		dialog = self.manual_check()
		self.settle(run_fetches=False)
		self.assertEqual(dialog.title(), 'Check for Updates')
		self.assertIn('Checking for updates...', self.text(dialog))
		self.assertEqual(list(self.buttons(dialog)), ['Cancel'])
		self.wait_for_result(dialog)
		self.assertIn("You're running the latest version of PyTest (2.0.0) and PyMS (1.2.0).", self.text(dialog))
		self.assertEqual(list(self.buttons(dialog)), ['Ok'])

	def test_manual_check_shows_errors_and_can_retry(self) -> None:
		self.fetch_returns(PyMSError('Update', "Couldn't download the latest version information from GitHub (offline)."), NEWER)
		dialog = self.manual_check()
		self.wait_for_result(dialog)
		self.assertIn('Unable to check for updates.', self.text(dialog))
		self.assertIn('(offline)', self.text(dialog))
		buttons = self.buttons(dialog)
		self.assertEqual(list(buttons), ['Ok', 'Retry'])
		buttons['Retry'].invoke()
		self.pump(self.window)
		self.wait_for_result(dialog)
		self.assertIn('Your version of PyTest (2.0.0) is older than the current version (2.1.0).', self.text(dialog))

	def test_manual_check_shows_unexpected_failures_as_errors(self) -> None:
		self.fetch_returns(RuntimeError('boom'))
		dialog = self.manual_check()
		self.wait_for_result(dialog)
		self.assertIn("Couldn't check for updates (boom).", self.text(dialog))

	def test_manual_check_shows_invalid_versions_as_errors(self) -> None:
		self.fetch_returns({'PyMS': '1.2.0'})
		dialog = self.manual_check()
		self.wait_for_result(dialog)
		self.assertIn('has no valid version for PyMS and PyTest', self.text(dialog))

	def test_manual_check_lists_every_outdated_component(self) -> None:
		self.fetch_returns(NEWER)
		dialog = self.manual_check()
		self.wait_for_result(dialog)
		self.assertEqual(dialog.title(), 'New Version Found')
		text = self.text(dialog)
		self.assertIn('Your version of PyTest (2.0.0) is older than the current version (2.1.0).', text)
		self.assertIn('Your version of PyMS (1.2.0) is older than the current version (1.3.0).', text)
		self.assertTrue(self.has_checkbox(dialog))

	def test_manual_check_ignores_dont_remind_me(self) -> None:
		PYMS_CONFIG.reminder.pyms_version.data.update(NEWER)
		self.fetch_returns(NEWER)
		dialog = self.manual_check()
		self.wait_for_result(dialog)
		self.assertIn('Your version of PyTest (2.0.0) is older than the current version (2.1.0).', self.text(dialog))

	def test_dont_remind_me_is_saved_on_ok(self) -> None:
		self.fetch_returns(NEWER)
		dialog = self.manual_check()
		self.wait_for_result(dialog)
		dialog.dont_remind_me.set(True)
		self.buttons(dialog)['Ok'].invoke()
		self.pump(self.window)
		self.assertEqual(PYMS_CONFIG.reminder.pyms_version.data, NEWER)
		self.assertEqual(self.dialogs(), [])

	def test_ok_without_dont_remind_me_saves_nothing(self) -> None:
		self.fetch_returns(NEWER)
		dialog = self.manual_check()
		self.wait_for_result(dialog)
		self.buttons(dialog)['Ok'].invoke()
		self.pump(self.window)
		self.assertEqual(PYMS_CONFIG.reminder.pyms_version.data, {})

	def test_cancel_during_check_discards_the_result(self) -> None:
		self.fetch_returns(NEWER)
		dialog = self.manual_check()
		with mock.patch.object(UpdateDialog, 'fetched') as fetched:
			self.buttons(dialog)['Cancel'].invoke()
			self.pump(self.window)
			self.assertEqual(self.dialogs(), [])
			self.settle()
		fetched.assert_not_called()

	# Automatic check

	def run_automatic_check(self, *results: dict[str, str] | Exception) -> list[UpdateDialog]:
		self.fetch_returns(*results)
		check_update(self.window, 'PyTest')
		self.settle()
		return self.dialogs()

	def test_automatic_check_is_silent_on_error(self) -> None:
		self.assertEqual(self.run_automatic_check(PyMSError('Update', 'offline')), [])

	def test_automatic_check_is_silent_when_current(self) -> None:
		self.assertEqual(self.run_automatic_check(CURRENT), [])

	def test_automatic_check_respects_dont_remind_me(self) -> None:
		PYMS_CONFIG.reminder.pyms_version.data.update(NEWER)
		self.assertEqual(self.run_automatic_check(NEWER), [])

	def test_automatic_check_shows_available_update(self) -> None:
		dialogs = self.run_automatic_check(NEWER)
		self.assertEqual(len(dialogs), 1)
		self.assertEqual(dialogs[0].title(), 'New Version Found')
		self.assertIn('Your version of PyTest (2.0.0) is older than the current version (2.1.0).', self.text(dialogs[0]))
		self.assertEqual(list(self.buttons(dialogs[0])), ['Ok', 'Change Log'])

	# Change log

	CHANGE_LOG = '# Change Log\n\n# October 29, 2026\n\n## PyTest v2.1.0\n- Added a shiny new feature.\n'

	def change_log_returns(self, *results: str | Exception) -> None:
		# Each fetch consumes the next result
		remaining = list(results)
		def fetch() -> str:
			result = remaining.pop(0)
			if isinstance(result, Exception):
				raise result
			return result
		patcher = mock.patch.object(UpdateDialog, 'fetch_change_log', side_effect=fetch)
		patcher.start()
		self.addCleanup(patcher.stop)

	def open_change_log(self) -> ChangeLogDialog:
		self.fetch_returns(NEWER)
		dialog = self.manual_check()
		self.wait_for_result(dialog)
		self.buttons(dialog)['Change Log'].invoke()
		self.pump(self.window)
		change_logs = [child for child in dialog.winfo_children() if isinstance(child, ChangeLogDialog)]
		self.assertEqual(len(change_logs), 1)
		return change_logs[0]

	def rendered(self, dialog: ChangeLogDialog) -> str:
		assert dialog.markdownview is not None
		return dialog.markdownview.textview.get('1.0', UI.END)

	def wait_for_change_log(self, dialog: ChangeLogDialog) -> None:
		self.wait_until(lambda: 'Loading change log' not in self.text(dialog))

	def test_change_log_is_only_offered_for_available_updates(self) -> None:
		self.fetch_returns(CURRENT)
		dialog = self.manual_check()
		self.wait_for_result(dialog)
		self.assertNotIn('Change Log', self.buttons(dialog))

	def test_change_log_shows_the_downloaded_change_log(self) -> None:
		self.change_log_returns(self.CHANGE_LOG)
		change_log = self.open_change_log()
		self.assertEqual(change_log.title(), 'Change Log')
		self.assertIn('Loading change log...', self.text(change_log))
		self.assertEqual(list(self.buttons(change_log)), ['Cancel'])
		self.wait_for_change_log(change_log)
		rendered = self.rendered(change_log)
		self.assertIn('PyTest v2.1.0', rendered)
		self.assertIn('Added a shiny new feature.', rendered)
		self.assertEqual(list(self.buttons(change_log)), ['Ok'])

	def test_change_log_shows_errors_and_can_retry(self) -> None:
		self.change_log_returns(PyMSError('Update', "Couldn't download the latest change log from GitHub (offline)."), self.CHANGE_LOG)
		change_log = self.open_change_log()
		self.wait_for_change_log(change_log)
		self.assertIn('Unable to load the change log.', self.text(change_log))
		self.assertIn('(offline)', self.text(change_log))
		buttons = self.buttons(change_log)
		self.assertEqual(list(buttons), ['Ok', 'Retry'])
		buttons['Retry'].invoke()
		self.pump(self.window)
		self.wait_for_change_log(change_log)
		self.assertIn('Added a shiny new feature.', self.rendered(change_log))

	def test_change_log_ok_returns_to_the_update_dialog(self) -> None:
		self.change_log_returns(self.CHANGE_LOG)
		change_log = self.open_change_log()
		self.wait_for_change_log(change_log)
		self.buttons(change_log)['Ok'].invoke()
		self.pump(self.window)
		self.assertEqual(len(self.dialogs()), 1)
		self.assertEqual([child for child in self.dialogs()[0].winfo_children() if isinstance(child, ChangeLogDialog)], [])
