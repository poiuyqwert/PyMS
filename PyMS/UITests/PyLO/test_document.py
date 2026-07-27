
from .utils import PyLOTestCase

from ...Utilities.PyMSError import PyMSError

from unittest import mock


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


class Test_PyLO_registry(PyLOTestCase):
	def test_register_attempts_all_extensions_and_reports_once(self) -> None:
		gui = self.make_pylo()
		with mock.patch('PyMS.PyLO.PyLO.registry.register', side_effect=PyMSError('Registry', 'nope')) as register, \
				mock.patch('PyMS.PyLO.PyLO.ErrorDialog') as error_dialog:
			gui.register_registry()
		self.assertEqual(register.call_count, 10)
		error_dialog.assert_called_once()
		self.assertIsInstance(error_dialog.call_args.args[1], PyMSError)
