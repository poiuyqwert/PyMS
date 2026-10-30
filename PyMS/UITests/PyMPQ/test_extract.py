
import os
from unittest import mock

from .utils import PyMPQTestCase

# Extract targets are derived paths (chosen directory + the archive's internal
# file paths), so no dialog ever checks them — `extract` itself must run the
# internal-file overwrite check on every output path.

SELECT_DIRECTORY = 'PyMS.Utilities.Config.SelectDirectory.select_open'
ALLOW_OVERWRITE = 'PyMS.PyMPQ.PyMPQ.check_allow_overwrite_internal_file'


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
