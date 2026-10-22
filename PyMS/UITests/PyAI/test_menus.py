from .utils import PyAITestCase

from ...PyAI.PyAI import PyAI
from ...PyAI.Sort import SortBy
from ...Utilities import UIKit as UI
from ...Utilities.UIKit.EventPattern import EventPattern

from unittest import mock

# Layout of the menubar and toolbar, and how their shortcuts are bound: every
# shortcut is bound once, by its menubar item, and the toolbar and the script
# list's context menu only display it.

SEPARATOR = '-'
GAP = '<gap>'
SECTION = '<section>'

EXPECTED_MENUBAR = ['File', 'Edit', 'View', 'Scripts', 'Settings', 'Help']

EXPECTED_MENUS: dict[str, list[str]] = {
	'File': [
		'New',
		'Open...',
		'Open Default Scripts',
		'Open MPQ...',
		SEPARATOR,
		'Save',
		'Save As...',
		'Save MPQ...',
		SEPARATOR,
		'Close',
		SEPARATOR,
		'Exit',
	],
	'Edit': [
		'Undo',
		'Redo',
		SEPARATOR,
		'Select All',
		SEPARATOR,
		'Find Scripts...',
	],
	'View': [
		'File Order',
		'Sort by ID',
		'Sort by BroodWar',
		'Sort by Flags',
		'Sort by String',
	],
	'Scripts': [
		'Add Blank Script...',
		'Remove Scripts',
		SEPARATOR,
		'Edit AI Script...',
		'Edit AI ID, String, and Extra Info...',
		'Edit Flags...',
		SEPARATOR,
		'Import Scripts...',
		'Import a List of Files...',
		'Export Scripts...',
	],
	'Settings': [
		'Manage Settings...',
		'Decompiling Format...',
		'Manage External Definition Files...',
		SEPARATOR,
		'Open TBL and DAT Settings...',
		'Save TBL and DAT Settings...',
		SEPARATOR,
		'Set as Default *.bin Editor (Windows Only)',
	],
	'Help': [
		'View Help',
		SEPARATOR,
		'Donate...',
		'About PyAI',
	],
}

ToolbarItem = str | tuple[str, EventPattern | None]

EXPECTED_TOOLBAR_ROWS: list[list[ToolbarItem]] = [
	[
		('New', UI.Ctrl.n),
		('Open', UI.Ctrl.o),
		('Open Default Scripts', UI.Ctrl.d),
		('Open MPQ', UI.Ctrl.Alt.o),
		GAP,
		('Save', UI.Ctrl.s),
		('Save As', UI.Ctrl.Alt.a),
		('Save MPQ', UI.Ctrl.Alt.m),
		GAP,
		('Close', UI.Ctrl.w),
		SECTION,
		('Undo', UI.Ctrl.z),
		('Redo', UI.Ctrl.y),
		SECTION,
		('File Order', None),
		('Sort by ID', None),
		('Sort by BroodWar', None),
		('Sort by Flags', None),
		('Sort by String', None),
		SECTION,
		('Manage Settings', UI.Ctrl.u),
		SECTION,
		('Set as Default *.bin Editor (Windows Only)', None),
		('View Help', UI.Key.F1),
		('About PyAI', None),
		('Donate', None),
		SECTION,
		('Exit', UI.Shortcut.Exit),
	],
	[
		('Add Blank Script', UI.Key.Insert),
		('Remove Scripts', UI.Key.Delete),
		GAP,
		('Find Scripts', UI.Ctrl.f),
		SECTION,
		('Edit AI Script', UI.Ctrl.e),
		('Edit AI ID, String, and Extra Info', UI.Ctrl.i),
		('Edit Flags', UI.Ctrl.g),
		GAP,
		('Import Scripts', UI.Ctrl.Alt.i),
		('Import a List of Files', UI.Ctrl.l),
		('Export Scripts', UI.Ctrl.Alt.e),
		SECTION,
		('Decompiling Format', None),
		('Manage External Definition Files', UI.Ctrl.x),
		GAP,
		('Open TBL and DAT Settings', None),
		('Save TBL and DAT Settings', None),
	],
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
			entries.append(menu.entrycget(index, 'label'))
	return entries


def cascade(menu: UI.Menu, label: str) -> UI.Menu:
	return menu.nametowidget(menu.entrycget(menu_entries(menu).index(label), 'menu'))


def toolbar_rows(toolbar: UI.Toolbar) -> list[list[str]]:
	rows: list[list[str]] = []
	for row in toolbar.pack_slaves():
		layout: list[str] = []
		for child in row.pack_slaves():
			tooltip = getattr(child, '_tooltip_Tooltip', None)
			if tooltip is not None:
				layout.append(tooltip.text)
			elif int(child['width']) == UI.Toolbar.GAP_SIZE:
				layout.append(GAP)
			else:
				layout.append(SECTION)
		rows.append(layout)
	return rows


def expected_toolbar_rows() -> list[list[str]]:
	rows: list[list[str]] = []
	for row in EXPECTED_TOOLBAR_ROWS:
		layout: list[str] = []
		for item in row:
			if isinstance(item, str):
				layout.append(item)
				continue
			tooltip, shortcut = item
			if shortcut is not None:
				tooltip += f' ({shortcut.description()})'
			layout.append(tooltip)
		rows.append(layout)
	return rows


class Test_PyAI_menubar(PyAITestCase):
	def test_menubar_menus_in_order(self) -> None:
		gui = self.make_pyai()
		self.assertEqual(menu_entries(gui.menu), EXPECTED_MENUBAR)

	def test_menu_items_in_order(self) -> None:
		gui = self.make_pyai()
		for label, expected in EXPECTED_MENUS.items():
			with self.subTest(menu=label):
				self.assertEqual(menu_entries(cascade(gui.menu, label)), expected)

	def test_file_open_items_follow_document_state(self) -> None:
		gui = self.make_pyai()
		scripts_menu = cascade(gui.menu, 'Scripts')
		index = menu_entries(scripts_menu).index('Add Blank Script...')
		self.assertEqual(str(scripts_menu.entrycget(index, 'state')), UI.DISABLED)
		gui.new()
		self.pump(gui)
		self.assertEqual(str(scripts_menu.entrycget(index, 'state')), UI.NORMAL)


class Test_PyAI_toolbar(PyAITestCase):
	def test_toolbar_buttons_in_order(self) -> None:
		gui = self.make_pyai()
		self.assertEqual(toolbar_rows(gui.toolbar), expected_toolbar_rows())

	def test_sort_radios_select_the_list_sort(self) -> None:
		gui = self.make_pyai()
		gui.new()
		self.pump(gui)
		radios = [child for child in gui.toolbar.pack_slaves()[0].pack_slaves() if isinstance(child, UI.Radiobutton)]
		expected = [SortBy.file_order, SortBy.id, SortBy.bw, SortBy.flags, SortBy.string]
		self.assertEqual(len(radios), len(expected))
		for radio, sort_by in zip(radios, expected):
			with self.subTest(sort=sort_by):
				radio.invoke()
				self.pump(gui)
				self.assertEqual(gui.get_sortby(), sort_by)


class Test_PyAI_shortcuts(PyAITestCase):
	def test_find_shortcut_triggers_once(self) -> None:
		with mock.patch.object(PyAI, 'find') as find:
			gui = self.make_pyai()
			gui.new()
			self.show(gui)
			self.shortcut(gui, UI.Ctrl.f)
		find.assert_called_once_with()

	def test_disabled_item_shortcut_does_nothing(self) -> None:
		# Find Scripts is disabled until a file is open.
		with mock.patch.object(PyAI, 'find') as find:
			gui = self.make_pyai()
			self.show(gui)
			self.shortcut(gui, UI.Ctrl.f)
		find.assert_not_called()

	def test_selection_shortcut_follows_selection_without_context_menu(self) -> None:
		# Edit Flags is shared with the script list's context menu; its shortcut
		# follows the current selection, whether or not the context menu was shown.
		with mock.patch.object(PyAI, 'editflags') as editflags:
			gui = self.make_pyai()
			gui.new()
			self.show(gui)
			self.shortcut(gui, UI.Ctrl.g)
			editflags.assert_not_called()
			with mock.patch.object(gui, 'has_scripts_selected', return_value=True):
				gui.action_states()
			self.shortcut(gui, UI.Ctrl.g)
		editflags.assert_called_once_with()

	def test_select_all_shortcut_triggers_once(self) -> None:
		with mock.patch.object(PyAI, 'select_all') as select_all:
			gui = self.make_pyai()
			gui.new()
			self.show(gui)
			self.shortcut(gui, UI.Ctrl.a)
		select_all.assert_called_once_with()
