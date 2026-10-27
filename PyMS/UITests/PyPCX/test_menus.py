from .utils import PyPCXTestCase

from ...Utilities import UIKit as UI
from ...Utilities.UIKit.EventPattern import EventPattern
from ...PyPCX.PyPCX import PyPCX
from ...FileFormats.Palette import Palette

from unittest import mock

SEPARATOR = '----'
GAP = '<gap>'
SECTION = '<section>'

EXPECTED_MENUS: list[tuple[str, list[str]]] = [
	('File', [
		'Open...',
		SEPARATOR,
		'Save',
		'Save As...',
		SEPARATOR,
		'Import BMP...',
		'Export BMP...',
		SEPARATOR,
		'Close',
		SEPARATOR,
		'Check for Updates...',
		SEPARATOR,
		'Exit',
	]),
	('Palette', [
		'Import Palette...',
		SEPARATOR,
		'Save Palette As',
	]),
	('Settings', [
		'Manage Settings...',
		SEPARATOR,
		'Set as Default *.pcx Editor (Windows Only)',
	]),
	('Help', [
		'View Help',
		SEPARATOR,
		'Donate...',
		'About PyPCX',
	]),
]

EXPECTED_SAVE_PALETTE_MENU = [
	'RIFF *.pal...',
	'JASC *.pal...',
	'StarCraft *.pal...',
	'StarCraft Terrain *.wpe...',
	'Adobe Color Table *.act...',
]

EXPECTED_TOOLBAR: list[str | tuple[str, EventPattern | None]] = [
	('Open', UI.Ctrl.o),
	GAP,
	('Save', UI.Ctrl.s),
	('Save As', UI.Ctrl.Alt.a),
	GAP,
	('Import BMP', UI.Ctrl.i),
	('Export BMP', UI.Ctrl.e),
	GAP,
	('Close', UI.Ctrl.w),
	SECTION,
	('Import Palette', UI.Ctrl.Alt.i),
	GAP,
	('Save Palette as RIFF *.pal', UI.Ctrl.r),
	('Save Palette as JASC *.pal', UI.Ctrl.j),
	('Save Palette as StarCraft *.pal', UI.Ctrl.p),
	('Save Palette as StarCraft Terrain *.wpe', UI.Ctrl.t),
	('Save Palette as Adobe Color Table *.act', UI.Ctrl.a),
	SECTION,
	('Manage Settings', UI.Ctrl.m),
	SECTION,
	('Set as Default *.pcx Editor (Windows Only)', None),
	('View Help', UI.Key.F1),
	('About PyPCX', None),
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


def cascade(menu: UI.Menu, label: str) -> UI.Menu:
	end = menu.index(UI.END) or 0
	for index in range(end + 1):
		if menu.type(index) == 'cascade' and menu.entrycget(index, 'label') == label:
			return menu.nametowidget(menu.entrycget(index, 'menu'))
	raise AssertionError(f'No menu named {label!r}')


def entry_state(menu: UI.Menu, label: str) -> str:
	return str(menu.entrycget(menu_entries(menu).index(label), 'state'))


class Test_PyPCX_menubar(PyPCXTestCase):
	def test_top_level_menus_in_order(self) -> None:
		gui = self.open_pypcx()
		self.assertEqual(menu_entries(gui.menu), [label for label, _ in EXPECTED_MENUS])

	def test_menu_items_in_order(self) -> None:
		gui = self.open_pypcx()
		for label, expected in EXPECTED_MENUS:
			with self.subTest(menu=label):
				self.assertEqual(menu_entries(cascade(gui.menu, label)), expected)

	def test_save_palette_submenu_items_in_order(self) -> None:
		gui = self.open_pypcx()
		submenu = cascade(cascade(gui.menu, 'Palette'), 'Save Palette As')
		self.assertEqual(menu_entries(submenu), EXPECTED_SAVE_PALETTE_MENU)

	def test_file_open_items_follow_document_state(self) -> None:
		gui = self.open_pypcx()
		file_menu = cascade(gui.menu, 'File')
		submenu = cascade(cascade(gui.menu, 'Palette'), 'Save Palette As')
		self.assertEqual(entry_state(file_menu, 'Save'), UI.DISABLED)
		self.assertEqual(entry_state(submenu, 'Adobe Color Table *.act...'), UI.DISABLED)
		self.assertEqual(entry_state(file_menu, 'Import BMP...'), UI.NORMAL)
		self.open_pcx_file(gui)
		self.assertEqual(entry_state(file_menu, 'Save'), UI.NORMAL)
		self.assertEqual(entry_state(submenu, 'Adobe Color Table *.act...'), UI.NORMAL)


class Test_PyPCX_toolbar(PyPCXTestCase):
	def test_toolbar_buttons_in_order(self) -> None:
		gui = self.open_pypcx()
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


class Test_PyPCX_shortcuts(PyPCXTestCase):
	def test_manage_settings_shortcut_triggers_once(self) -> None:
		with mock.patch.object(PyPCX, 'sets') as sets:
			gui = self.open_pypcx()
			self.show(gui)
			self.shortcut(gui, UI.Ctrl.m)
		sets.assert_called_once_with()

	def test_import_bmp_shortcut_triggers_once_with_no_file_open(self) -> None:
		with mock.patch.object(PyPCX, 'iimport') as iimport:
			gui = self.open_pypcx()
			self.show(gui)
			self.shortcut(gui, UI.Ctrl.i)
		iimport.assert_called_once_with()

	def test_disabled_item_shortcut_does_nothing(self) -> None:
		with mock.patch.object(PyPCX, 'export') as export:
			gui = self.open_pypcx()
			self.show(gui)
			self.shortcut(gui, UI.Ctrl.e)
		export.assert_not_called()

	def test_enabled_item_shortcut_triggers_once(self) -> None:
		with mock.patch.object(PyPCX, 'export') as export:
			gui = self.open_pypcx()
			self.open_pcx_file(gui)
			self.show(gui)
			self.shortcut(gui, UI.Ctrl.e)
		export.assert_called_once_with()

	def test_save_palette_submenu_shortcut_triggers_once(self) -> None:
		with mock.patch.object(PyPCX, 'savepal') as savepal:
			gui = self.open_pypcx()
			self.open_pcx_file(gui)
			self.show(gui)
			self.shortcut(gui, UI.Ctrl.a)
		savepal.assert_called_once_with(file_type=Palette.FileType.act)
