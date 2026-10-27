
from ...Utilities.UpdateDialog import UpdateDialog
from ...Utilities.PyMSConfig import PYMS_CONFIG
from ...Utilities.PyMSError import PyMSError

import unittest, urllib.error
from unittest import mock

INSTALLED = {'PyMS': '1.2.0', 'PyTest': '2.0.0'}

def installed_version(program: str) -> str:
	return INSTALLED[program]

def response(data: bytes) -> mock.MagicMock:
	resp = mock.MagicMock()
	resp.__enter__.return_value.read.return_value = data
	return resp


class Test_fetch_versions(unittest.TestCase):
	def test_returns_parsed_versions(self) -> None:
		with mock.patch('urllib.request.urlopen', return_value=response(b'{"PyMS": "1.2.0", "PyTest": "2.0.0"}')):
			self.assertEqual(UpdateDialog.fetch_versions(), {'PyMS': '1.2.0', 'PyTest': '2.0.0'})

	def test_network_failure_is_a_pymserror(self) -> None:
		with mock.patch('urllib.request.urlopen', side_effect=urllib.error.URLError('offline')):
			with self.assertRaises(PyMSError) as cm:
				UpdateDialog.fetch_versions()
		self.assertIn("Couldn't download the latest version information", str(cm.exception))
		self.assertIsInstance(cm.exception.__cause__, urllib.error.URLError)

	def test_invalid_json_is_a_pymserror(self) -> None:
		with mock.patch('urllib.request.urlopen', return_value=response(b'<html>')):
			with self.assertRaises(PyMSError) as cm:
				UpdateDialog.fetch_versions()
		self.assertIn('version information downloaded from GitHub is invalid', str(cm.exception))

	def test_non_object_json_is_a_pymserror(self) -> None:
		with mock.patch('urllib.request.urlopen', return_value=response(b'[]')):
			with self.assertRaises(PyMSError) as cm:
				UpdateDialog.fetch_versions()
		self.assertIn('version information downloaded from GitHub is invalid', str(cm.exception))


@mock.patch('PyMS.Utilities.Assets.version', installed_version)
class Test_outdated(unittest.TestCase):
	def test_current_versions_are_not_outdated(self) -> None:
		self.assertEqual(UpdateDialog.outdated('PyTest', {'PyMS': '1.2.0', 'PyTest': '2.0.0'}), (False, False))

	def test_older_installed_versions_are_outdated(self) -> None:
		self.assertEqual(UpdateDialog.outdated('PyTest', {'PyMS': '1.3.0', 'PyTest': '2.0.0'}), (True, False))
		self.assertEqual(UpdateDialog.outdated('PyTest', {'PyMS': '1.2.0', 'PyTest': '2.0.1'}), (False, True))
		self.assertEqual(UpdateDialog.outdated('PyTest', {'PyMS': '2.0.0', 'PyTest': '3.0.0'}), (True, True))

	def test_newer_installed_versions_are_not_outdated(self) -> None:
		self.assertEqual(UpdateDialog.outdated('PyTest', {'PyMS': '1.1.9', 'PyTest': '1.9.9'}), (False, False))

	def test_missing_program_is_a_pymserror(self) -> None:
		with self.assertRaises(PyMSError) as cm:
			UpdateDialog.outdated('PyTest', {'PyMS': '1.2.0'})
		self.assertIn('has no valid version for PyMS and PyTest', str(cm.exception))

	def test_malformed_version_is_a_pymserror(self) -> None:
		with self.assertRaises(PyMSError) as cm:
			UpdateDialog.outdated('PyTest', {'PyMS': 'latest', 'PyTest': '2.0.0'})
		self.assertIn('has no valid version for PyMS and PyTest', str(cm.exception))


class Test_reminder_suppressed(unittest.TestCase):
	LATEST = {'PyMS': '1.3.0', 'PyTest': '2.1.0'}

	def suppressed(self, reminders: dict[str, str]) -> bool:
		with mock.patch.dict(PYMS_CONFIG.reminder.pyms_version.data, reminders, clear=True):
			return UpdateDialog.reminder_suppressed('PyTest', self.LATEST)

	def test_no_reminders_does_not_suppress(self) -> None:
		self.assertFalse(self.suppressed({}))

	def test_reminders_for_both_latest_versions_suppress(self) -> None:
		self.assertTrue(self.suppressed({'PyMS': '1.3.0', 'PyTest': '2.1.0'}))

	def test_reminder_for_only_one_component_does_not_suppress(self) -> None:
		self.assertFalse(self.suppressed({'PyMS': '1.3.0'}))
		self.assertFalse(self.suppressed({'PyTest': '2.1.0'}))

	def test_reminders_for_older_versions_do_not_suppress(self) -> None:
		self.assertFalse(self.suppressed({'PyMS': '1.3.0', 'PyTest': '2.0.0'}))
