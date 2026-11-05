
from .utils import PyGRAFTTestCase

from ...Utilities import UIKit as UI
from ...Utilities.UIKit.EventPattern import EventPattern

SEPARATOR = '----'
GAP = '<gap>'
SECTION = '<section>'

ToolbarLayout = list[str | tuple[str, EventPattern | None]]

EXPECTED_MENUS: list[tuple[str, list[str]]] = [
	('File', [
		'New',
		'Open...',
		'Open Directory...',
		'Open MPQ...',
		SEPARATOR,
		'Save',
		'Save As...',
		'Save MPQ...',
		SEPARATOR,
		'Import from TXT...',
		'Export to TXT...',
		'Import FireGraft Project...',
		SEPARATOR,
		'Check for Updates...',
		SEPARATOR,
		'Exit',
	]),
	('Settings', [
		'Manage Settings...',
		'Reload Data Files',
		SEPARATOR,
		'Set as Default *.graft Editor (Windows Only)',
	]),
	('Help', [
		'View Help',
		SEPARATOR,
		'Donate...',
		'About PyGRAFT',
	]),
]

EXPECTED_TOOLBAR: ToolbarLayout = [
	('New', UI.Ctrl.n),
	('Open', UI.Ctrl.o),
	('Open Directory', UI.Ctrl.d),
	('Open MPQ', UI.Ctrl.Alt.o),
	GAP,
	('Save', UI.Ctrl.s),
	('Save As', UI.Ctrl.Alt.s),
	('Save MPQ', UI.Ctrl.Alt.m),
	GAP,
	('Import from TXT', UI.Ctrl.i),
	('Export to TXT', UI.Ctrl.e),
	SECTION,
	('Manage Settings', UI.Ctrl.m),
	('Reload Data Files', None),
	SECTION,
	('Set as Default *.graft Editor (Windows Only)', None),
	('View Help', UI.Key.F1),
	('About PyGRAFT', None),
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


def toolbar_layout(toolbar: UI.Toolbar) -> list[str]:
	row = toolbar._row # pylint: disable=protected-access
	layout: list[str] = []
	for child in row.pack_slaves():
		if isinstance(child, (UI.Button, UI.Radiobutton, UI.Checkbutton)):
			layout.append(getattr(child, '_tooltip_Tooltip').text)
		elif int(child['width']) == UI.Toolbar.GAP_SIZE:
			layout.append(GAP)
		else:
			layout.append(SECTION)
	return layout


def expected_layout(items: ToolbarLayout) -> list[str]:
	expected: list[str] = []
	for item in items:
		if isinstance(item, str):
			expected.append(item)
			continue
		tooltip, shortcut = item
		if shortcut is not None:
			tooltip += f' ({shortcut.description()})'
		expected.append(tooltip)
	return expected


class Test_PyGRAFT_menubar(PyGRAFTTestCase):
	def test_top_level_menus_in_order(self) -> None:
		gui = self.open_pygraft()
		self.assertEqual(menu_entries(gui.menu), [label for label, _ in EXPECTED_MENUS])

	def test_menu_items_in_order(self) -> None:
		gui = self.open_pygraft()
		for label, expected in EXPECTED_MENUS:
			with self.subTest(menu=label):
				self.assertEqual(menu_entries(cascade(gui.menu, label)), expected)

	def test_toolbar_layout(self) -> None:
		gui = self.open_pygraft()
		self.assertEqual(toolbar_layout(gui.toolbar), expected_layout(EXPECTED_TOOLBAR))
