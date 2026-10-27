
import importlib, json
from unittest import mock

from ..harness import UITestCase

from ...Utilities import UIKit as UI

from typing import Any

PROGRAMS = ('PyAI', 'PyBIN', 'PyDAT', 'PyFNT', 'PyGOT', 'PyGRP', 'PyICE', 'PyJSON', 'PyLO', 'PyMPQ', 'PyPAL', 'PyPCX', 'PySPK', 'PyTBL', 'PyTILE', 'PyTRG')

# Construction patches some programs need to build without touching disk (see each program's `UITests/<Program>/utils.py`)
EXTRA_PATCHES: dict[str, dict[str, dict[str, Any]]] = {
	'PyBIN': {'PyMS.Utilities.MPQHandler.MPQHandler.get_file': {'return_value': None}},
	'PyJSON': {'PyMS.PyJSON.PyJSON.open': {'new': mock.mock_open(read_data=json.dumps([])), 'create': True}},
}


def descendants(widget: UI.Misc) -> list[UI.Misc]:
	result: list[UI.Misc] = []
	for child in widget.winfo_children():
		result.append(child)
		result.extend(descendants(child))
	return result


def file_menu(gui: Any) -> UI.Menu:
	for index in range((gui.menu.index(UI.END) or 0) + 1):
		if gui.menu.type(index) == 'cascade' and gui.menu.entrycget(index, 'label') == 'File':
			return gui.menu.nametowidget(gui.menu.entrycget(index, 'menu'))
	raise AssertionError('No File menu')


class Test_check_for_updates(UITestCase):
	def make_program(self, program: str) -> tuple[Any, mock.MagicMock]:
		module = importlib.import_module(f'PyMS.{program}.{program}')
		gui = self.make_window(getattr(module, program), extra_patches=EXTRA_PATCHES.get(program))
		patcher = mock.patch(f'PyMS.{program}.{program}.UpdateDialog')
		update_dialog = patcher.start()
		self.addCleanup(patcher.stop)
		return gui, update_dialog

	def check_file_menu_item(self, program: str) -> None:
		gui, update_dialog = self.make_program(program)
		file_menu(gui).invoke('Check for Updates...')
		update_dialog.assert_called_once_with(gui, program)

	def check_toolbar_button(self, program: str) -> None:
		gui, update_dialog = self.make_program(program)
		buttons = [child for child in descendants(gui.toolbar) if isinstance(child, UI.Button) and getattr(getattr(child, '_tooltip_Tooltip', None), 'text', None) == 'Check for Updates']
		self.assertEqual(len(buttons), 1)
		buttons[0].invoke()
		update_dialog.assert_called_once_with(gui, program)


# One test per program and entry point, so each builds a single window and failures name the program
for _program in PROGRAMS:
	setattr(Test_check_for_updates, f'test_{_program}_file_menu_item_checks_for_updates', lambda self, program=_program: self.check_file_menu_item(program))
	setattr(Test_check_for_updates, f'test_{_program}_toolbar_button_checks_for_updates', lambda self, program=_program: self.check_toolbar_button(program))
