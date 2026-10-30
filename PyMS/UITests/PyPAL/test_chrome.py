
from .utils import PyPALTestCase, ERROR_DIALOG

from ...FileFormats.Palette import Palette
from ...Utilities import UIKit as UI
from ...Utilities.PyMSError import PyMSError

from unittest import mock


class Test_PyPAL_update_title(PyPALTestCase):
	def test_title_without_document(self) -> None:
		gui = self.open_pypal()
		gui.file = None
		gui.palette = None
		gui.update_title()
		self.assertNotIn('(', gui.title())

	def test_title_for_unsaved_new_document(self) -> None:
		gui = self.open_pypal()
		gui.palette = Palette()
		gui.file = None
		gui.update_title()
		self.assertIn('(Untitled.pal)', gui.title())

	def test_title_for_named_file(self) -> None:
		gui = self.open_pypal()
		gui.file = 'colors.pal'
		gui.update_title()
		self.assertIn('(colors.pal)', gui.title())


class Test_PyPAL_edit_indicator(PyPALTestCase):
	def test_mark_edited_enables_indicator(self) -> None:
		gui = self.open_pypal()
		gui.mark_edited(True)
		self.assertTrue(gui.edited)
		self.assertEqual(str(gui.editstatus['state']), UI.NORMAL)

	def test_mark_edited_false_disables_indicator(self) -> None:
		gui = self.open_pypal()
		gui.mark_edited(False)
		self.assertFalse(gui.edited)
		self.assertEqual(str(gui.editstatus['state']), UI.DISABLED)


class Test_PyPAL_registry(PyPALTestCase):
	def test_register_registers_both_palette_extensions(self) -> None:
		gui = self.open_pypal()
		with mock.patch('PyMS.PyPAL.PyPAL.registry.register') as register, \
				mock.patch(ERROR_DIALOG) as error_dialog:
			gui.register_registry()
		self.assertEqual(register.call_count, 2)
		error_dialog.assert_not_called()

	def test_register_error_stops_and_reports(self) -> None:
		gui = self.open_pypal()
		with mock.patch('PyMS.PyPAL.PyPAL.registry.register', side_effect=PyMSError('Registry', 'boom')) as register, \
				mock.patch(ERROR_DIALOG) as error_dialog:
			gui.register_registry()
		register.assert_called_once()
		error_dialog.assert_called_once()


class Test_PyPAL_secondary_dialogs(PyPALTestCase):
	def test_settings_opens_settings_dialog(self) -> None:
		gui = self.open_pypal()
		with mock.patch('PyMS.PyPAL.PyPAL.SettingsDialog') as dialog:
			gui.sets()
		dialog.assert_called_once_with(gui, gui.config_)

	def test_help_opens_help_dialog(self) -> None:
		gui = self.open_pypal()
		with mock.patch('PyMS.PyPAL.PyPAL.HelpDialog') as dialog:
			gui.help()
		dialog.assert_called_once()

	def test_about_opens_about_dialog(self) -> None:
		gui = self.open_pypal()
		with mock.patch('PyMS.PyPAL.PyPAL.AboutDialog') as dialog:
			gui.about()
		dialog.assert_called_once()

	def test_sponsor_opens_sponsor_dialog(self) -> None:
		gui = self.open_pypal()
		with mock.patch('PyMS.PyPAL.PyPAL.SponsorDialog') as dialog:
			gui.sponsor()
		dialog.assert_called_once_with(gui)
