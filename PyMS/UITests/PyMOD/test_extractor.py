
from .utils import PyMODTestCase, PROJECT_PATH

from ...PyMOD.PyMOD import PyMOD
from ...PyMOD import Extractor
from ...PyMOD.Extractor.DefaultExtractorDialog import DefaultExtractorDialog
from ...PyMOD.Extractor.DestinationView import DestinationView
from ...PyMOD.Extractor.ExtractorDialog import ExtractorDialog
from ...PyMOD.CompileStep.PackageMPQ import PackageMPQ
from ...PyMOD.Project import Project
from ...PyMPQ.CompressionSetting import CompressionOption
from ...Utilities import UIKit as UI
from ...Utilities import JSON
from ...Utilities.MPQHandler import MPQHandler
from ...Utilities.PyMSError import PyMSError

import io, json, os
from unittest import mock

from typing import Any, BinaryIO


class Test_PyMOD_find_extractor(PyMODTestCase):
	# `find_extractor` is the whole dispatch: highest confidence wins, ties go to
	# the earlier registration, and anything unclaimed falls back to the default.

	def make_extractor_type(self, confidence: float) -> type[ExtractorDialog]:
		class StubExtractorDialog(ExtractorDialog):
			@classmethod
			def matches(cls, mpq_file_name: str) -> float:
				return confidence

			# Only ever used for dispatch, never opened
			def perform_extract(self, destination_path: str) -> JSON.Object:
				return {}
		return StubExtractorDialog

	def test_an_unclaimed_file_falls_back_to_the_default_extractor(self) -> None:
		self.assertIs(Extractor.find_extractor('unit\\terran\\marine.grp'), DefaultExtractorDialog)

	def test_a_registered_extractor_claims_the_file(self) -> None:
		claiming = self.make_extractor_type(1)
		with mock.patch.object(Extractor, 'EXTRACTOR_TYPES', [self.make_extractor_type(0), claiming]):
			self.assertIs(Extractor.find_extractor('scripts\\aiscript.bin'), claiming)

	def test_the_highest_confidence_extractor_wins(self) -> None:
		most_confident = self.make_extractor_type(1)
		with mock.patch.object(Extractor, 'EXTRACTOR_TYPES', [self.make_extractor_type(0.5), most_confident]):
			self.assertIs(Extractor.find_extractor('scripts\\aiscript.bin'), most_confident)

	def test_equal_confidence_goes_to_the_earlier_registration(self) -> None:
		first = self.make_extractor_type(1)
		with mock.patch.object(Extractor, 'EXTRACTOR_TYPES', [first, self.make_extractor_type(1)]):
			self.assertIs(Extractor.find_extractor('scripts\\aiscript.bin'), first)

	def test_the_default_extractor_never_claims_a_file(self) -> None:
		# It is the fallback rather than a candidate, so it must not be registered
		# and must not out-score a real extractor if it ever is.
		self.assertNotIn(DefaultExtractorDialog, Extractor.EXTRACTOR_TYPES)
		self.assertEqual(DefaultExtractorDialog.matches('unit\\terran\\marine.grp'), 0)


class Test_PyMOD_DefaultExtractorDialog(PyMODTestCase):
	# The dialog writes real files, so both the MPQ read and the disk writes are
	# stubbed and the tests assert on what would have been written.

	MPQ_FILE_NAME = 'unit\\terran\\marine.grp'
	FILE_DATA = b'GRP\x00fake frames'
	MPQ_FOLDER_PATH = os.path.join(PROJECT_PATH, 'MyMod.mpq')

	def make_dialog(self, gui: PyMOD, mpq_folders: list[str] | None = None) -> DefaultExtractorDialog:
		project = Project(PROJECT_PATH)
		def fake_walk(_path: str, topdown: bool = True) -> list[tuple[str, list[str], list[str]]]:
			assert topdown, 'The source walk must be top-down so directory pruning works'
			folders = [self.MPQ_FOLDER_PATH] if mpq_folders is None else mpq_folders
			folder_names = [os.path.basename(folder) for folder in folders]
			return [(PROJECT_PATH, folder_names, [])] + [(os.path.join(PROJECT_PATH, folder_name), [], []) for folder_name in folder_names]
		with mock.patch('PyMS.PyMOD.Project._os.walk', side_effect=fake_walk), \
				mock.patch.object(UI.WindowExtensions, 'grab_wait', lambda self: None):
			dialog = DefaultExtractorDialog(gui, mpqhandler=gui.mpqhandler, project=project, config=gui.config_, mpq_file_name=self.MPQ_FILE_NAME)
		self.addCleanup(self._destroy, dialog)
		self.pump(dialog)
		return dialog

	def press_extract(self, dialog: DefaultExtractorDialog) -> dict[str, bytes]:
		# Captures every write the extract would make, keyed by path, so nothing
		# reaches disk and the config can be asserted on alongside the file data.
		written: dict[str, bytes] = {}
		def fake_load_file(_self: MPQHandler, path: str, *_args: Any, **_kwargs: Any) -> BinaryIO:
			self.assertEqual(path, 'MPQ:' + self.MPQ_FILE_NAME, 'The MPQ ref must keep its prefix so the bundled MPQ folder is a fallback')
			return io.BytesIO(self.FILE_DATA)
		def fake_open(path: str, mode: str = 'r', **_kwargs: Any) -> Any:
			file = io.BytesIO() if 'b' in mode else io.StringIO()
			def capture() -> None:
				value = file.getvalue()
				written[path] = value if isinstance(value, bytes) else value.encode('utf-8')
			file.close = capture # type: ignore[method-assign]
			return file
		with mock.patch.object(MPQHandler, 'load_file', autospec=True, side_effect=fake_load_file), \
				mock.patch('PyMS.PyMOD.Extractor.DefaultExtractorDialog.os.makedirs'), \
				mock.patch('PyMS.PyMOD.Extractor.DefaultExtractorDialog.open', fake_open, create=True), \
				mock.patch('PyMS.PyMOD.Extractor.ExtractorDialog.open', fake_open, create=True), \
				mock.patch('PyMS.PyMOD.Extractor.ExtractorDialog.os.path.exists', return_value=False), \
				mock.patch('PyMS.PyMOD.Source.Item.os.path.isfile', return_value=True):
			dialog.ok()
		return written

	def test_the_destination_defaults_to_the_mpq_path_inside_the_mpq_folder(self) -> None:
		gui = self.make_window(PyMOD)
		dialog = self.make_dialog(gui)
		# `unit\terran\marine.grp` in the archive is the folder layout `PackageMPQ`
		# turns back into that same archive path.
		self.assertEqual(dialog.destination_view.sub_path.get(), os.path.join('unit', 'terran', 'marine.grp'))
		self.assertEqual(dialog.destination_view.destination_path(), os.path.join(self.MPQ_FOLDER_PATH, 'unit', 'terran', 'marine.grp'))

	def test_the_project_root_is_the_destination_when_there_are_no_mpq_folders(self) -> None:
		gui = self.make_window(PyMOD)
		dialog = self.make_dialog(gui, mpq_folders=[])
		self.assertEqual(dialog.destination_view.selected_root(), PROJECT_PATH)

	def test_extracting_writes_the_file_and_no_config_by_default(self) -> None:
		gui = self.make_window(PyMOD)
		dialog = self.make_dialog(gui)
		written = self.press_extract(dialog)
		destination_path = os.path.join(self.MPQ_FOLDER_PATH, 'unit', 'terran', 'marine.grp')
		self.assertEqual(written, {destination_path: self.FILE_DATA})
		self.assertTrue(dialog.extracted)

	def test_overriding_the_compression_writes_a_config_the_packager_can_read(self) -> None:
		gui = self.make_window(PyMOD)
		dialog = self.make_dialog(gui)
		dialog.mpq_config_view.override.set(True)
		dialog.mpq_config_view.compression_index.set(dialog.mpq_config_view.COMPRESSION_CHOICES.index(CompressionOption.Deflate))
		dialog.mpq_config_view.choose_compression(dialog.mpq_config_view.compression_index.get())
		dialog.mpq_config_view.compression_level.set(3)
		written = self.press_extract(dialog)
		destination_path = os.path.join(self.MPQ_FOLDER_PATH, 'unit', 'terran', 'marine.grp')
		config_path = destination_path + '.config.json'
		self.assertEqual(written[destination_path], self.FILE_DATA)
		config_json = json.loads(written[config_path].decode('utf-8'))
		self.assertEqual(config_json, {'compression': 'deflate:3'})
		# The written config is only useful if the packaging step decodes it, so
		# assert on the contract between the two rather than just the JSON.
		assert JSON.is_json_object(config_json)
		file_config = PackageMPQ.FileConfig.from_json(config_json)
		self.assertEqual(file_config.compression, 'deflate:3')

	def test_a_declined_overwrite_leaves_the_destination_alone(self) -> None:
		gui = self.make_window(PyMOD)
		dialog = self.make_dialog(gui)
		with mock.patch('PyMS.PyMOD.Extractor.ExtractorDialog.os.path.exists', return_value=True), \
				mock.patch.object(UI.MessageBox, 'askyesno', return_value=False) as askyesno, \
				mock.patch.object(MPQHandler, 'load_file', autospec=True) as load_file:
			dialog.ok()
		self.assertTrue(askyesno.called)
		self.assertFalse(load_file.called)
		self.assertFalse(dialog.extracted)


class Test_PyMOD_DestinationView(PyMODTestCase):
	# The destination is user editable, so every path it can produce has to stay
	# inside the chosen folder.

	def make_view(self, gui: PyMOD, mpq_file_name: str = 'unit\\terran\\marine.grp') -> DestinationView:
		project = Project(PROJECT_PATH)
		with mock.patch('PyMS.PyMOD.Project._os.walk', return_value=[(PROJECT_PATH, [], [])]):
			view = DestinationView(gui, project=project, mpq_file_name=mpq_file_name)
		self.addCleanup(view.destroy)
		return view

	def test_an_empty_path_is_rejected(self) -> None:
		gui = self.make_window(PyMOD)
		view = self.make_view(gui)
		view.sub_path.set('   ')
		with self.assertRaises(PyMSError) as cm:
			view.destination_path()
		self.assertIn('Enter a path for the extracted file', str(cm.exception))

	def test_an_absolute_path_is_rejected(self) -> None:
		gui = self.make_window(PyMOD)
		view = self.make_view(gui)
		view.sub_path.set(os.path.join(os.sep, 'etc', 'passwd'))
		with self.assertRaises(PyMSError) as cm:
			view.destination_path()
		self.assertIn('must be a path relative to the destination folder', str(cm.exception))

	def test_a_path_escaping_the_destination_folder_is_rejected(self) -> None:
		gui = self.make_window(PyMOD)
		view = self.make_view(gui)
		view.sub_path.set(os.path.join(os.pardir, os.pardir, 'marine.grp'))
		with self.assertRaises(PyMSError) as cm:
			view.destination_path()
		self.assertIn('is not inside the destination folder', str(cm.exception))

	def test_the_resolved_path_is_displayed(self) -> None:
		gui = self.make_window(PyMOD)
		view = self.make_view(gui)
		# Relative to the project, so the label identifies the file rather than
		# stretching the dialog to the width of wherever the project lives.
		self.assertEqual(view.full_path.get(), os.path.join('unit', 'terran', 'marine.grp'))
		# The label tracks the entry so an invalid path explains itself before the
		# Extract button is ever pressed.
		view.sub_path.set('')
		self.assertEqual(view.full_path.get(), 'Enter a path for the extracted file')
