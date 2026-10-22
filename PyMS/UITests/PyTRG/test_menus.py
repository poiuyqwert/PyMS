from .utils import PyTRGTestCase

from ...Utilities import UIKit as UI
from ...Utilities.UIKit.EventPattern import EventPattern
from ...PyTRG.PyTRG import PyTRG

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
		'Save GOT Compatible TRG...',
		SEPARATOR,
		'Import Text...',
		'Export Text...',
		SEPARATOR,
		'Close',
		SEPARATOR,
		'Exit',
	]),
	('Edit', [
		'Undo',
		'Redo',
		SEPARATOR,
		'Cut',
		'Copy',
		'Paste',
		SEPARATOR,
		'Select All',
		SEPARATOR,
		'Find/Replace...',
		'Find Next',
		SEPARATOR,
		'Test Code',
	]),
	('Settings', [
		'Manage Settings...',
		'Syntax Highlighting...',
		SEPARATOR,
		'Set as Default *.trg Editor (Windows Only)',
	]),
	('Help', [
		'View Help',
		SEPARATOR,
		'Donate...',
		'About PyTRG',
	]),
]

EXPECTED_TOOLBAR: list[str | tuple[str, EventPattern | None]] = [
	('New', UI.Ctrl.n),
	('Open', UI.Ctrl.o),
	GAP,
	('Save', UI.Ctrl.s),
	('Save As', UI.Ctrl.Alt.a),
	('Save GOT Compatible TRG', UI.Ctrl.g),
	GAP,
	('Import Text', UI.Ctrl.i),
	('Export Text', UI.Ctrl.e),
	GAP,
	('Close', UI.Ctrl.w),
	SECTION,
	('Find/Replace', UI.Ctrl.f),
	GAP,
	('Test Code', UI.Ctrl.t),
	SECTION,
	('Manage Settings', UI.Ctrl.m),
	('Syntax Highlighting', UI.Ctrl.Alt.c),
	SECTION,
	('Set as Default *.trg Editor (Windows Only)', None),
	('View Help', UI.Key.F1),
	('About PyTRG', None),
	('Donate', None),
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


def cascade(gui: PyTRG, label: str) -> UI.Menu:
	end = gui.menu.index(UI.END) or 0
	for index in range(end + 1):
		if gui.menu.entrycget(index, 'label') == label:
			return gui.nametowidget(gui.menu.entrycget(index, 'menu'))
	raise AssertionError(f'No menu named {label!r}')


def item_index(menu: UI.Menu, label: str) -> int:
	return menu_entries(menu).index(label)


class Test_PyTRG_menubar(PyTRGTestCase):
	def test_top_level_menus_in_order(self) -> None:
		gui = self.make_pytrg()
		self.assertEqual(menu_entries(gui.menu), [label for label, _ in EXPECTED_MENUS])

	def test_menu_items_in_order(self) -> None:
		gui = self.make_pytrg()
		for label, expected in EXPECTED_MENUS:
			with self.subTest(menu=label):
				self.assertEqual(menu_entries(cascade(gui, label)), expected)

	def test_file_open_items_follow_document_state(self) -> None:
		gui = self.make_pytrg()
		edit_menu = cascade(gui, 'Edit')
		test_index = item_index(edit_menu, 'Test Code')
		self.assertEqual(str(edit_menu.entrycget(test_index, 'state')), UI.DISABLED)
		gui.new()
		self.assertEqual(str(edit_menu.entrycget(test_index, 'state')), UI.NORMAL)
		gui.close()
		self.assertEqual(str(edit_menu.entrycget(test_index, 'state')), UI.DISABLED)

	def test_edit_items_show_editor_accelerators(self) -> None:
		gui = self.make_pytrg()
		edit_menu = cascade(gui, 'Edit')
		for label, shortcut in (('Undo', UI.Ctrl.z), ('Redo', UI.Ctrl.y), ('Cut', UI.Ctrl.x), ('Copy', UI.Ctrl.c), ('Paste', UI.Ctrl.v), ('Select All', UI.Ctrl.a)):
			with self.subTest(item=label):
				self.assertEqual(edit_menu.entrycget(item_index(edit_menu, label), 'accelerator'), shortcut.name())

	def test_edit_menu_states_follow_editor(self) -> None:
		gui = self.make_pytrg()
		gui.new()
		gui.text.load('Trigger(All players):')
		edit_menu = cascade(gui, 'Edit')
		gui.update_edit_menu()
		self.assertEqual(str(edit_menu.entrycget(item_index(edit_menu, 'Undo'), 'state')), UI.DISABLED)
		self.assertEqual(str(edit_menu.entrycget(item_index(edit_menu, 'Copy'), 'state')), UI.DISABLED)
		gui.text.insert(UI.END, '\n')
		gui.select_all()
		gui.update_edit_menu()
		self.assertEqual(str(edit_menu.entrycget(item_index(edit_menu, 'Undo'), 'state')), UI.NORMAL)
		self.assertEqual(str(edit_menu.entrycget(item_index(edit_menu, 'Copy'), 'state')), UI.NORMAL)

	def test_select_all_item_selects_editor_text(self) -> None:
		gui = self.make_pytrg()
		gui.new()
		gui.text.load('Trigger(All players):')
		edit_menu = cascade(gui, 'Edit')
		self.invoke_menu(edit_menu, item_index(edit_menu, 'Select All'))
		self.assertEqual(gui.text.get('sel.first', 'sel.last'), 'Trigger(All players):\n')


class Test_PyTRG_toolbar(PyTRGTestCase):
	def test_toolbar_buttons_in_order(self) -> None:
		gui = self.make_pytrg()
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


class Test_PyTRG_shortcuts(PyTRGTestCase):
	def test_test_code_shortcut_triggers_once(self) -> None:
		with mock.patch.object(PyTRG, 'test') as test:
			gui = self.make_pytrg()
			gui.new()
			self.show(gui)
			self.shortcut(gui, UI.Ctrl.t)
		test.assert_called_once_with()

	def test_manage_settings_shortcut_triggers_once(self) -> None:
		with mock.patch.object(PyTRG, 'settings') as settings:
			gui = self.make_pytrg()
			self.show(gui)
			self.shortcut(gui, UI.Ctrl.m)
		settings.assert_called_once_with()

	def test_disabled_item_shortcut_does_nothing(self) -> None:
		with mock.patch.object(PyTRG, 'export') as export:
			gui = self.make_pytrg()
			self.show(gui)
			self.shortcut(gui, UI.Ctrl.e)
		export.assert_not_called()

	def test_find_next_shortcut_works_before_find_was_opened(self) -> None:
		with mock.patch.object(PyTRG, 'find_next') as find_next:
			gui = self.make_pytrg()
			gui.new()
			self.show(gui)
			self.shortcut(gui, UI.Key.F3)
		find_next.assert_called_once_with()

	def test_find_next_opens_finder_when_no_search(self) -> None:
		gui = self.make_pytrg()
		gui.new()
		self.assertIsNone(gui.findwindow)
		gui.find_next()
		self.assertIsNotNone(gui.findwindow)

	def test_find_next_searches_with_existing_term(self) -> None:
		gui = self.make_pytrg()
		gui.new()
		gui.text.load('alpha\nbeta\n')
		gui.find()
		assert gui.findwindow is not None
		gui.findwindow.find.set('beta')
		gui.text.mark_set(UI.INSERT, '1.0')
		gui.find_next()
		self.assertEqual(gui.text.get('sel.first', 'sel.last'), 'beta')

	def test_editor_keys_are_not_bound_on_the_window(self) -> None:
		# The text widget handles these itself, so a window binding would run them twice
		gui = self.make_pytrg()
		for shortcut in (UI.Ctrl.z, UI.Ctrl.y, UI.Ctrl.x, UI.Ctrl.c, UI.Ctrl.v, UI.Ctrl.a):
			with self.subTest(shortcut=shortcut.name()):
				self.assertEqual(gui.bind(shortcut()), '')
