
from .utils import PyLOTestCase

from ...Utilities.CheckSaved import CheckSaved

from unittest import mock


class Test_PyLO_save(PyLOTestCase):
	def test_save_interprets_editor_text_into_model(self) -> None:
		gui = self.make_pylo()
		gui.new()
		gui.text.load('Frame:\n\t(3, 4)')
		with mock.patch('PyMS.FileFormats.LO.LO.save', return_value=None), \
				mock.patch('PyMS.PyLO.PyLO.check_allow_overwrite_internal_file', return_value=True):
			result = gui.saveas(file_path='fake.loa')
		self.assertEqual(result, CheckSaved.saved)
		assert gui.lo is not None
		self.assertEqual(gui.lo.frames, [[[3, 4]]])
		self.assertEqual(gui.file, 'fake.loa')

	def test_failed_save_leaves_model_untouched(self) -> None:
		gui = self.make_pylo()
		gui.new()
		gui.text.load('garbage')
		lo_before = gui.lo
		with mock.patch('PyMS.PyLO.PyLO.ErrorDialog') as error_dialog, \
				mock.patch('PyMS.PyLO.PyLO.check_allow_overwrite_internal_file', return_value=True):
			result = gui.saveas(file_path='fake.loa')
		error_dialog.assert_called_once()
		self.assertEqual(result, CheckSaved.cancelled)
		self.assertIs(gui.lo, lo_before)
		assert gui.lo is not None
		self.assertEqual(gui.lo.frames, [[[0, 0]]])


class Test_PyLO_export(PyLOTestCase):
	def test_export_writes_current_editor_text(self) -> None:
		gui = self.make_pylo()
		gui.new()
		gui.text.load('Frame:\n\t(5, 6) # comment')
		opener = mock.mock_open()
		with mock.patch('PyMS.Utilities.Config.SelectFile.select_save', return_value='out.txt'), \
				mock.patch('builtins.open', opener):
			gui.export()
		written = ''.join(call.args[0] for call in opener().write.call_args_list)
		self.assertEqual(written.rstrip('\n'), 'Frame:\n\t(5, 6) # comment')
		self.assertEqual(gui.status.get(), 'Export Successful!')
