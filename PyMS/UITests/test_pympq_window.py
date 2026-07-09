
import os
import unittest
from unittest import mock

from .harness import UITestCase

from ..PyMPQ.PyMPQ import PyMPQ

# These tests drive PyMPQ through its public command methods. The harness
# neutralizes settings I/O, analytics, the update check, and the tracer; the
# archive, file dialogs, and file I/O are mocked so no files are read or
# written.
#
# Extract targets are derived paths (chosen directory + the archive's internal
# file paths), so no dialog ever checks them — `extract` itself must run the
# internal-file overwrite check on every output path.

SELECT_DIRECTORY = 'PyMS.Utilities.Config.SelectDirectory.select_open'
ALLOW_OVERWRITE = 'PyMS.PyMPQ.PyMPQ.check_allow_overwrite_internal_file'


class PyMPQTestCase(UITestCase):
	def make_pympq(self) -> PyMPQ:
		return self.make_window(PyMPQ)

	def seed_mpq(self, gui: PyMPQ, file_names: list[bytes]) -> mock.MagicMock:
		# Stand in for an opened archive: `extract` only opens it as a context
		# manager and calls `read_file`, taking entries from `display_files`.
		mpq = mock.MagicMock()
		mpq.read_file.return_value = b'data'
		gui.mpq = mpq
		gui.display_files = [mock.Mock(file_name=file_name, locale=0) for file_name in file_names]
		return mpq


class Test_PyMPQ_extract(PyMPQTestCase):
	def test_extract_checks_overwrite_of_each_derived_output_path(self) -> None:
		gui = self.make_pympq()
		self.seed_mpq(gui, [b'scripts\\aiscript.bin', b'readme.txt'])
		opener = mock.mock_open()
		with mock.patch.object(gui.listbox, 'cur_selection', return_value=[0, 1]), \
				mock.patch(SELECT_DIRECTORY, return_value='fake_dir'), \
				mock.patch('os.makedirs'), \
				mock.patch('builtins.open', opener), \
				mock.patch(ALLOW_OVERWRITE, return_value=True) as allow_overwrite:
			gui.extract()
		expected_paths = [os.path.join('fake_dir', 'scripts', 'aiscript.bin'), os.path.join('fake_dir', 'readme.txt')]
		self.assertEqual([call.args[0] for call in allow_overwrite.call_args_list], expected_paths)
		self.assertEqual([call.args[0] for call in opener.call_args_list], expected_paths)

	def test_extract_skips_files_whose_overwrite_is_declined(self) -> None:
		gui = self.make_pympq()
		mpq = self.seed_mpq(gui, [b'scripts\\aiscript.bin', b'readme.txt'])
		opener = mock.mock_open()
		with mock.patch.object(gui.listbox, 'cur_selection', return_value=[0, 1]), \
				mock.patch(SELECT_DIRECTORY, return_value='fake_dir'), \
				mock.patch('os.makedirs'), \
				mock.patch('builtins.open', opener), \
				mock.patch(ALLOW_OVERWRITE, side_effect=[False, True]):
			gui.extract()
		self.assertEqual([call.args[0] for call in opener.call_args_list], [os.path.join('fake_dir', 'readme.txt')])
		mpq.read_file.assert_called_once_with(b'readme.txt', 0)


if __name__ == '__main__':
	unittest.main()
