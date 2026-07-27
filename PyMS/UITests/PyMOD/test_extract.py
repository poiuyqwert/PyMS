
from .utils import PyMODTestCase

from ...PyMOD.PyMOD import PyMOD
from ...PyMOD.ExtractDialog import ExtractDialog
from ...Utilities import UIKit as UI
from ...Utilities import Assets
from ...Utilities.UIKit.Widgets.Extensions import MiscExtensions
from ...Utilities.MPQHandler import MPQHandler

import os
from unittest import mock

from typing import Any, Callable


class Test_PyMOD_extract(PyMODTestCase):
	# The Extract dialog is built entirely in its constructor — widgets, the file
	# listing, and the write trace on the search variable — so these tests build
	# the real dialog rather than stubbing it.

	EXTRACT_FILES = ['unit\\terran\\marine.grp', 'sound\\misc\\click.wav']

	def make_extract_dialog(self, gui: PyMOD, files: list[str]) -> ExtractDialog:
		def fake_walk(path: str) -> list[tuple[str, list[str], list[str]]]:
			self.assertEqual(path, Assets.mpq_dir, 'The listing must walk the bundled MPQ folder')
			walked: dict[str, list[str]] = {}
			for file_name in files:
				*directories, base_name = file_name.split('\\')
				walked.setdefault(os.path.join(Assets.mpq_dir, *directories), []).append(base_name)
			return [(directory, [], base_names) for directory, base_names in walked.items()]
		def list_inline(_self: MiscExtensions, callback: Callable[[Any], None], background_function: Callable[..., Any], *args: Any, **kwargs: Any) -> None:
			callback(background_function(*args, **kwargs))
		# The listing runs on a background thread polled by `after`; run it inline so
		# the dialog's file list is settled by the time the constructor returns. The
		# MPQs and the bundled folder are stubbed out so nothing is read from disk.
		with mock.patch.object(MPQHandler, 'list_files', autospec=True, return_value=[]), \
				mock.patch('PyMS.PyMOD.ExtractDialog.os.walk', side_effect=fake_walk), \
				mock.patch.object(MiscExtensions, 'after_background', autospec=True, side_effect=list_inline), \
				mock.patch.object(UI.WindowExtensions, 'grab_wait', lambda self: None):
			dialog = ExtractDialog(gui, gui.mpqhandler, gui.config_)
		self.addCleanup(self._destroy, dialog)
		self.pump(dialog)
		return dialog

	def listed_files(self, dialog: ExtractDialog) -> tuple[str, ...]:
		return tuple(dialog.listbox.get(0, UI.END))

	def test_opening_lists_every_available_file(self) -> None:
		gui = self.make_window(PyMOD)
		dialog = self.make_extract_dialog(gui, self.EXTRACT_FILES)
		# The default `*` search matches everything, and the listing is sorted.
		self.assertEqual(self.listed_files(dialog), tuple(sorted(self.EXTRACT_FILES)))
		self.assertEqual(str(dialog.extract_button['state']), UI.NORMAL)

	def test_editing_the_search_schedules_a_filtered_update(self) -> None:
		gui = self.make_window(PyMOD)
		dialog = self.make_extract_dialog(gui, self.EXTRACT_FILES)
		self.assertIsNone(dialog.searchtimer)
		dialog.search.set('*.grp')
		# Setting the variable must reach `updatesearch` through its write trace,
		# which debounces by scheduling the update. Asserting on the scheduled timer
		# rather than waiting the debounce out keeps the test deterministic.
		self.assertIsNotNone(dialog.searchtimer)
		dialog.updatelist()
		self.assertEqual(self.listed_files(dialog), ('unit\\terran\\marine.grp',))

	def test_a_search_matching_nothing_disables_extracting(self) -> None:
		gui = self.make_window(PyMOD)
		dialog = self.make_extract_dialog(gui, self.EXTRACT_FILES)
		dialog.search.set('*.dat')
		dialog.updatelist()
		self.assertEqual(self.listed_files(dialog), ())
		self.assertEqual(str(dialog.extract_button['state']), UI.DISABLED)
