
from unittest import mock

from ..harness import UITestCase

from ...PyAI.PyAI import PyAI
from ...Utilities.CheckSaved import CheckSaved

# These tests drive PyAI through its public command methods, asserting on both
# widget and model state. The harness neutralizes settings I/O, analytics, the
# update check, and the tracer; file dialogs and file I/O are mocked so no
# files are read or written.
#
# The internal-file overwrite check must prompt exactly once per path:
# `SelectFile.select_save` already checks paths chosen through its dialog, so
# `saveas` must only check paths that were passed in (e.g. re-saving to the
# currently open files).

SELECT_SAVE = 'PyMS.Utilities.Config.SelectFile.select_save'
ALLOW_OVERWRITE = 'PyMS.PyAI.PyAI.check_allow_overwrite_internal_file'
AIBIN_SAVE = 'PyMS.FileFormats.AIBIN.AIBIN.AIBIN.save'


class PyAITestCase(UITestCase):
	def make_pyai(self) -> PyAI:
		return self.make_window(PyAI)


class Test_PyAI_save(PyAITestCase):
	def test_saveas_does_not_recheck_overwrite_of_dialog_chosen_path(self) -> None:
		gui = self.make_pyai()
		gui.new()
		with mock.patch(SELECT_SAVE, return_value='fake_ai.bin'), \
				mock.patch(AIBIN_SAVE, return_value=None), \
				mock.patch(ALLOW_OVERWRITE, return_value=True) as allow_overwrite:
			result = gui.saveas()
		self.assertEqual(result, CheckSaved.saved)
		allow_overwrite.assert_not_called()
		self.assertEqual(gui.aiscript, 'fake_ai.bin')

	def test_saveas_does_not_recheck_overwrite_of_dialog_chosen_bwscript_path(self) -> None:
		gui = self.make_pyai()
		gui.new()
		assert gui.ai is not None
		with mock.patch(SELECT_SAVE, side_effect=['fake_ai.bin', 'fake_bw.bin']), \
				mock.patch(AIBIN_SAVE, return_value=None), \
				mock.patch.object(gui.ai, 'has_bwscripts', return_value=True), \
				mock.patch(ALLOW_OVERWRITE, return_value=True) as allow_overwrite:
			result = gui.saveas()
		self.assertEqual(result, CheckSaved.saved)
		allow_overwrite.assert_not_called()
		self.assertEqual(gui.aiscript, 'fake_ai.bin')
		self.assertEqual(gui.bwscript, 'fake_bw.bin')

	def test_save_to_existing_paths_checks_overwrite_of_both_files(self) -> None:
		# No dialog is shown when re-saving to the open files, so `saveas` is the
		# only overwrite guard for these paths.
		gui = self.make_pyai()
		gui.new()
		assert gui.ai is not None
		with mock.patch(AIBIN_SAVE, return_value=None), \
				mock.patch.object(gui.ai, 'has_bwscripts', return_value=True), \
				mock.patch(ALLOW_OVERWRITE, return_value=True) as allow_overwrite:
			result = gui.save()
		self.assertEqual(result, CheckSaved.saved)
		self.assertEqual([call.args[0] for call in allow_overwrite.call_args_list], ['aiscript.bin', 'bwscript.bin'])

	def test_save_without_bwscripts_does_not_check_overwrite_of_unwritten_bwscript(self) -> None:
		# bwscript.bin is only written when the file has bwscripts, so a file
		# without them must not prompt about overwriting the bwscript path.
		gui = self.make_pyai()
		gui.new()
		with mock.patch(AIBIN_SAVE, return_value=None), \
				mock.patch(ALLOW_OVERWRITE, return_value=True) as allow_overwrite:
			result = gui.save()
		self.assertEqual(result, CheckSaved.saved)
		self.assertEqual([call.args[0] for call in allow_overwrite.call_args_list], ['aiscript.bin'])

	def test_save_declining_overwrite_cancels_without_saving(self) -> None:
		gui = self.make_pyai()
		gui.new()
		with mock.patch(AIBIN_SAVE, return_value=None) as aibin_save, \
				mock.patch(ALLOW_OVERWRITE, return_value=False):
			result = gui.save()
		self.assertEqual(result, CheckSaved.cancelled)
		aibin_save.assert_not_called()
