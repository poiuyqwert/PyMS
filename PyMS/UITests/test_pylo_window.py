
import unittest
from unittest import mock

from .harness import UITestCase

from ..PyLO.PyLO import PyLO
from ..FileFormats.GRP import CacheGRP
from ..Utilities import UIKit as UI
from ..Utilities.CheckSaved import CheckSaved
from ..Utilities.PyMSError import PyMSError

# These tests drive PyLO through its public command methods, asserting on both
# widget and model state. The harness neutralizes settings I/O, analytics, the
# update check, and the tracer; file dialogs and file I/O are mocked so no
# files are read or written.


class PyLOTestCase(UITestCase):
	def make_pylo(self) -> PyLO:
		return self.make_window(PyLO)

	def settle_syntax_coloring(self, gui: PyLO) -> None:
		# Recoloring runs on a chained 1ms `after` timer, so a single pump can
		# race it; pump until the pending update range is fully colored.
		for _ in range(10):
			self.pump(gui)
			if not gui.text.tag_ranges('Update'):
				break


class Test_PyLO_preview(PyLOTestCase):
	def test_previewing_first_frame_displays_frame_number_one(self) -> None:
		gui = self.make_pylo()
		gui.new()
		self.settle_syntax_coloring(gui)
		gui.text.mark_set(UI.INSERT, '2.0 lineend')
		gui.previewupdate()
		self.assertEqual(gui.previewing_basegrp_frame, 0)
		gui.framesupdate()
		self.assertEqual(gui.baseframes.get(), 'Base Frame: 1 / -')

	def test_preview_frame_index_counts_headers_before_cursor(self) -> None:
		gui = self.make_pylo()
		gui.new()
		gui.text.load('Frame:\n\t(0, 0)\nFrame:\n\t(1, 1)\nFrame:\n\t(2, 2)')
		self.settle_syntax_coloring(gui)
		gui.text.mark_set(UI.INSERT, '6.0 lineend')
		gui.previewupdate()
		self.assertEqual(gui.previewing_basegrp_frame, 2)
		self.assertEqual(gui.previewing_offset, (2, 2))

	def test_scrolling_overlay_frame_redraws_preview(self) -> None:
		gui = self.make_pylo()
		gui.new()
		self.settle_syntax_coloring(gui)
		grp = CacheGRP()
		grp.frames = 3
		gui.overlaygrp = grp
		gui.previewupdate()
		self.assertEqual(gui.previewing_overlaygrp_frame, 0)
		gui.scrolling('scroll', '1', 'units')
		self.assertEqual(gui.overlayframe, 1)
		self.assertEqual(gui.previewing_overlaygrp_frame, 1)
		self.assertEqual(gui.overlayframes.get(), 'Overlay Frame: 2 / 3')

	def test_grp_frame_render_failure_falls_back_to_no_image(self) -> None:
		gui = self.make_pylo()
		grp = CacheGRP()
		grp.frames = 3
		gui.basegrp = grp
		self.assertIsNone(gui.base_grp_frame(2))


class Test_PyLO_editor_state(PyLOTestCase):
	def test_editor_disabled_when_no_file_open(self) -> None:
		gui = self.make_pylo()
		gui.action_states()
		self.assertEqual(str(gui.text.text['state']), 'disabled')
		gui.new()
		self.assertEqual(str(gui.text.text['state']), 'normal')


class Test_PyLO_open(PyLOTestCase):
	def test_open_refreshes_frame_status_labels(self) -> None:
		gui = self.make_pylo()
		with mock.patch('PyMS.FileFormats.LO.LO.load', return_value=None):
			gui.open(file='fake.loa')
		self.assertEqual(gui.overlayframes.get(), 'Overlay Frame: 1 / -')


class Test_PyLO_import(PyLOTestCase):
	def test_import_interprets_text_into_model(self) -> None:
		gui = self.make_pylo()
		text = 'Frame:\n    (1, 2)\n'
		with mock.patch('PyMS.Utilities.Config.SelectFile.select_open', return_value='fake.txt'), \
				mock.patch('builtins.open', mock.mock_open(read_data=text)):
			gui.iimport()
		assert gui.lo is not None
		self.assertEqual(gui.lo.frames, [[[1, 2]]])
		self.assertEqual(gui.text.get('1.0', UI.END).rstrip('\n'), 'Frame:\n    (1, 2)')

	def test_import_marks_document_edited(self) -> None:
		# A freshly imported overlay is unsaved work: it must be flagged edited
		# so closing without saving prompts instead of silently discarding it.
		gui = self.make_pylo()
		with mock.patch('PyMS.Utilities.Config.SelectFile.select_open', return_value='fake.txt'), \
				mock.patch('builtins.open', mock.mock_open(read_data='Frame:\n    (1, 2)\n')):
			gui.iimport()
		self.pump(gui)
		self.assertTrue(gui.edited_state.is_edited)
		self.assertEqual(str(gui.editstatus['state']), UI.NORMAL)

	def test_import_without_open_file_leaves_no_save_target_so_save_prompts(self) -> None:
		gui = self.make_pylo()
		text = 'Frame:\n    (1, 2)\n'
		with mock.patch('PyMS.Utilities.Config.SelectFile.select_open', return_value='fake.txt'), \
				mock.patch('builtins.open', mock.mock_open(read_data=text)):
			gui.iimport()
		self.assertIsNone(gui.file)
		with mock.patch('PyMS.Utilities.Config.SelectFile.select_save', return_value='') as select_save:
			result = gui.save()
		select_save.assert_called_once()
		self.assertEqual(result, CheckSaved.cancelled)

	def test_import_into_open_file_keeps_it_as_the_save_target(self) -> None:
		gui = self.make_pylo()
		with mock.patch('PyMS.FileFormats.LO.LO.load', return_value=None):
			gui.open(file='opened.loa')
		self.assertEqual(gui.file, 'opened.loa')
		with mock.patch('PyMS.Utilities.Config.SelectFile.select_open', return_value='fake.txt'), \
				mock.patch('builtins.open', mock.mock_open(read_data='Frame:\n    (3, 4)\n')):
			gui.iimport()
		self.assertEqual(gui.file, 'opened.loa')
		with mock.patch('PyMS.FileFormats.LO.LO.save', return_value=None) as lo_save, \
				mock.patch('PyMS.PyLO.PyLO.check_allow_overwrite_internal_file', return_value=True):
			result = gui.save()
		self.assertEqual(result, CheckSaved.saved)
		lo_save.assert_called_once_with('opened.loa')

	def test_import_with_uncompilable_text_shows_error_and_aborts(self) -> None:
		gui = self.make_pylo()
		with mock.patch('PyMS.Utilities.Config.SelectFile.select_open', return_value='fake.txt'), \
				mock.patch('builtins.open', mock.mock_open(read_data='garbage\n')), \
				mock.patch('PyMS.PyLO.PyLO.ErrorDialog') as error_dialog:
			gui.iimport()
		error_dialog.assert_called_once()
		error = error_dialog.call_args.args[1]
		self.assertIsInstance(error, PyMSError)
		self.assertIn('Unknown line format', str(error))
		self.assertFalse(gui.is_file_open())
		self.assertEqual(gui.text.get('1.0', UI.END).rstrip('\n'), '')


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


class Test_PyLO_registry(PyLOTestCase):
	def test_register_attempts_all_extensions_and_reports_once(self) -> None:
		gui = self.make_pylo()
		with mock.patch('PyMS.PyLO.PyLO.registry.register', side_effect=PyMSError('Registry', 'nope')) as register, \
				mock.patch('PyMS.PyLO.PyLO.ErrorDialog') as error_dialog:
			gui.register_registry()
		self.assertEqual(register.call_count, 10)
		error_dialog.assert_called_once()
		self.assertIsInstance(error_dialog.call_args.args[1], PyMSError)


if __name__ == '__main__':
	unittest.main()
