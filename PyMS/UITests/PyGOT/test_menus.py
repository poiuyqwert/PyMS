
from .utils import PyGOTTestCase

from ...Utilities import UIKit as UI
from ...Utilities.UIKit.EventPattern import EventPattern
from ...PyGOT.PyGOT import PyGOT

from unittest import mock

SEPARATOR = '----'
GAP = '<gap>'
SECTION = '<section>'

EXPECTED_MENUS: list[tuple[str, list[str]]] = [
	('File', [
		'New',
		'Open...',
		SEPARATOR,
		'Save',
		'Save As...',
		SEPARATOR,
		'Import Game Template...',
		'Export Game Template...',
		SEPARATOR,
		'Close',
		SEPARATOR,
		'Check for Updates...',
		SEPARATOR,
		'Exit',
	]),
	('TRG', [
		'Convert TRG to GOT Compatible...',
		'Revert GOT Compatible TRG...',
	]),
	('Settings', [
		'Manage Settings...',
		SEPARATOR,
		'Set as Default *.got Editor (Windows Only)',
	]),
	('Help', [
		'View Help',
		SEPARATOR,
		'Donate...',
		'About PyGOT',
	]),
]

EXPECTED_TOOLBAR: list[str | tuple[str, EventPattern | None]] = [
	('New', UI.Ctrl.n),
	('Open', UI.Ctrl.o),
	GAP,
	('Save', UI.Ctrl.s),
	('Save As', UI.Ctrl.Alt.a),
	GAP,
	('Import Game Template', UI.Ctrl.i),
	('Export Game Template', UI.Ctrl.e),
	GAP,
	('Close', UI.Ctrl.w),
	SECTION,
	('Convert TRG to GOT Compatible', UI.Ctrl.t),
	('Revert GOT Compatible TRG', UI.Ctrl.Alt.t),
	SECTION,
	('Manage Settings', UI.Ctrl.m),
	SECTION,
	('Set as Default *.got Editor (Windows Only)', None),
	('View Help', UI.Key.F1),
	('About PyGOT', None),
	('Donate', None),
	('Check for Updates', None),
	SECTION,
	('Exit', UI.Shortcut.Exit),
]


def menu_entries(menu: UI.Menu) -> list[str]:
	end = menu.index(UI.END)
	if end is None:
		return []
	entries: list[str] = []
	for index in range(end + 1):
		if menu.type(index) == 'separator':
			entries.append(SEPARATOR)
		else:
			entries.append(str(menu.entrycget(index, 'label')))
	return entries


def cascade(gui: PyGOT, label: str) -> UI.Menu:
	end = gui.menu.index(UI.END) or 0
	for index in range(end + 1):
		if gui.menu.entrycget(index, 'label') == label:
			return gui.nametowidget(gui.menu.entrycget(index, 'menu'))
	raise AssertionError(f'No menu named {label!r}')


class Test_PyGOT_menubar(PyGOTTestCase):
	def test_top_level_menus_in_order(self) -> None:
		gui = self.make_pygot()
		labels = menu_entries(gui.menu)
		self.assertEqual(labels, [label for label, _ in EXPECTED_MENUS])

	def test_menu_items_in_order(self) -> None:
		gui = self.make_pygot()
		for label, expected in EXPECTED_MENUS:
			with self.subTest(menu=label):
				self.assertEqual(menu_entries(cascade(gui, label)), expected)

	def test_file_open_items_follow_document_state(self) -> None:
		gui = self.make_pygot()
		file_menu = cascade(gui, 'File')
		save_index = menu_entries(file_menu).index('Save')
		self.assertEqual(str(file_menu.entrycget(save_index, 'state')), UI.DISABLED)
		gui.new()
		gui.action_states()
		self.assertEqual(str(file_menu.entrycget(save_index, 'state')), UI.NORMAL)


class Test_PyGOT_toolbar(PyGOTTestCase):
	def test_toolbar_buttons_in_order(self) -> None:
		gui = self.make_pygot()
		row = gui.toolbar._row # pylint: disable=protected-access
		layout: list[str] = []
		for child in row.pack_slaves():
			if isinstance(child, UI.Button):
				tooltip = getattr(child, '_tooltip_Tooltip')
				layout.append(tooltip.text)
			elif int(child['width']) == UI.Toolbar.GAP_SIZE:
				layout.append(GAP)
			else:
				layout.append(SECTION)
		expected: list[str] = []
		for item in EXPECTED_TOOLBAR:
			if isinstance(item, str):
				expected.append(item)
				continue
			tooltip, shortcut = item
			if shortcut is not None:
				tooltip += f' ({shortcut.description()})'
			expected.append(tooltip)
		self.assertEqual(layout, expected)


class Test_PyGOT_shortcuts(PyGOTTestCase):
	def test_convert_trg_shortcut_triggers_once(self) -> None:
		with mock.patch.object(PyGOT, 'trg') as trg:
			gui = self.make_pygot()
			self.show(gui)
			self.shortcut(gui, UI.Ctrl.t)
		trg.assert_called_once()

	def test_manage_settings_shortcut_triggers_once(self) -> None:
		with mock.patch.object(PyGOT, 'sets') as sets:
			gui = self.make_pygot()
			self.show(gui)
			self.shortcut(gui, UI.Ctrl.m)
		sets.assert_called_once_with()

	def test_disabled_item_shortcut_does_nothing(self) -> None:
		with mock.patch.object(PyGOT, 'export') as export:
			gui = self.make_pygot()
			self.show(gui)
			self.shortcut(gui, UI.Ctrl.e)
		export.assert_not_called()

	def test_enabled_item_shortcut_triggers_once(self) -> None:
		with mock.patch.object(PyGOT, 'export') as export:
			gui = self.make_pygot()
			gui.new()
			gui.action_states()
			self.show(gui)
			self.shortcut(gui, UI.Ctrl.e)
		export.assert_called_once_with()
