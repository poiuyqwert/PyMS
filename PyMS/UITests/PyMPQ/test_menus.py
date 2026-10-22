from .utils import PyMPQTestCase

from ...Utilities import UIKit as UI
from ...Utilities.UIKit.EventPattern import EventPattern
from ...PyMPQ.PyMPQ import PyMPQ
from ...PyMPQ.CompressionSetting import CompressionOption
from ...PyMPQ.Locales import LOCALE_CHOICES

from unittest import mock

SETTINGS_DIALOG = 'PyMS.PyMPQ.PyMPQ.SettingsDialog'

SEPARATOR = '----'
GAP = '<gap>'
SECTION = '<section>'

EXPECTED_MENUS: list[tuple[str, list[str]]] = [
	('File', [
		'New...',
		'Open...',
		SEPARATOR,
		'Close',
		SEPARATOR,
		'Exit',
	]),
	('Files', [
		'Add Files...',
		'Add Directory...',
		'Delete Files',
		SEPARATOR,
		'Open File',
		'Rename File',
		'Change Locale...',
		SEPARATOR,
		'Extract Files...',
		SEPARATOR,
		'Compact Archive',
	]),
	('Settings', [
		'Manage Settings...',
		'Compression',
		'Encrypt',
		'Locale',
		SEPARATOR,
		'Set as Default *.mpq Editor (Windows Only)',
	]),
	('Help', [
		'View Help',
		SEPARATOR,
		'Donate...',
		'About PyMPQ',
	]),
]

EXPECTED_COMPRESSION_MENU = [
	'Auto-Select',
	SEPARATOR,
	'None',
	'Standard',
	'Deflate',
	'Audio',
]

EXPECTED_DEFLATE_MENU = ['Default', '0 (None)', '1 (Best Speed)', '2', '3', '4', '5', '6', '7', '8', '9 (Best Compression)']

EXPECTED_AUDIO_MENU = ['Lowest (Best Quality)', 'Medium', 'Highest (Least Space)']

EXPECTED_LOCALE_MENU = [
	'Neutral (English) [0]',
	'Chinese (Taiwan) [1028]',
	'Czech [1029]',
	'German [1031]',
	'English (US) [1033]',
	'Spanish [1034]',
	'French [1036]',
	'Italian [1040]',
	'Japanese [1041]',
	'Korean [1042]',
	'Polish [1045]',
	'Portuguese [1046]',
	'Russian [1049]',
	'English (UK) [2057]',
	'Other...',
]

EXPECTED_CONTEXT_MENU = [
	'Open File',
	SEPARATOR,
	'Extract Files...',
	'Delete Files',
	'Rename File',
	'Change Locale...',
]

EXPECTED_TOOLBAR: list[str | tuple[str, EventPattern | None]] = [
	('New', UI.Ctrl.n),
	('Open', UI.Ctrl.o),
	GAP,
	('Close', UI.Ctrl.w),
	SECTION,
	('Add Files', UI.Ctrl.i),
	('Add Directory', UI.Ctrl.d),
	('Delete Files', UI.Key.Delete),
	('Extract Files', UI.Ctrl.e),
	GAP,
	('Rename File', UI.Ctrl.r),
	('Compact Archive', UI.Ctrl.p),
	SECTION,
	('Manage Settings', UI.Ctrl.m),
	SECTION,
	('Set as Default *.mpq Editor (Windows Only)', None),
	('View Help', UI.Key.F1),
	('About PyMPQ', None),
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


def cascade(menu: UI.Menu, label: str) -> UI.Menu:
	end = menu.index(UI.END) or 0
	for index in range(end + 1):
		if menu.type(index) == 'cascade' and menu.entrycget(index, 'label') == label:
			return menu.nametowidget(menu.entrycget(index, 'menu'))
	raise AssertionError(f'No menu named {label!r}')


def entry_state(menu: UI.Menu, label: str) -> str:
	return str(menu.entrycget(menu_entries(menu).index(label), 'state'))


def toolbar_button(gui: PyMPQ, tooltip: str) -> UI.Button:
	for child in gui.toolbar._row.pack_slaves(): # pylint: disable=protected-access
		if isinstance(child, UI.Button) and getattr(child, '_tooltip_Tooltip').text.startswith(tooltip):
			return child
	raise AssertionError(f'No toolbar button {tooltip!r}')


class Test_PyMPQ_menubar(PyMPQTestCase):
	def test_top_level_menus_in_order(self) -> None:
		gui = self.make_pympq()
		self.assertEqual(menu_entries(gui.menu), [label for label, _ in EXPECTED_MENUS])

	def test_menu_items_in_order(self) -> None:
		gui = self.make_pympq()
		for label, expected in EXPECTED_MENUS:
			with self.subTest(menu=label):
				self.assertEqual(menu_entries(cascade(gui.menu, label)), expected)

	def test_settings_submenus_in_order(self) -> None:
		gui = self.make_pympq()
		settings_menu = cascade(gui.menu, 'Settings')
		compression_menu = cascade(settings_menu, 'Compression')
		self.assertEqual(menu_entries(compression_menu), EXPECTED_COMPRESSION_MENU)
		self.assertEqual(menu_entries(cascade(compression_menu, 'Deflate')), EXPECTED_DEFLATE_MENU)
		self.assertEqual(menu_entries(cascade(compression_menu, 'Audio')), EXPECTED_AUDIO_MENU)
		self.assertEqual(len(EXPECTED_LOCALE_MENU), len(LOCALE_CHOICES))
		self.assertEqual(menu_entries(cascade(settings_menu, 'Locale')), EXPECTED_LOCALE_MENU)

	def test_context_menu_items_in_order(self) -> None:
		gui = self.make_pympq()
		self.assertEqual(menu_entries(gui.listmenu), EXPECTED_CONTEXT_MENU)

	def test_files_items_follow_archive_and_selection_state(self) -> None:
		gui = self.make_pympq()
		files_menu = cascade(gui.menu, 'Files')
		for label in ('Add Files...', 'Delete Files', 'Open File', 'Change Locale...', 'Compact Archive'):
			self.assertEqual(entry_state(files_menu, label), UI.DISABLED, label)
		self.seed_mpq(gui, [b'readme.txt'])
		with mock.patch.object(gui.listbox, 'cur_selection', return_value=[0]):
			gui.action_states()
		for label in ('Add Files...', 'Add Directory...', 'Delete Files', 'Open File', 'Rename File', 'Change Locale...', 'Extract Files...'):
			self.assertEqual(entry_state(files_menu, label), UI.NORMAL, label)


class Test_PyMPQ_toolbar(PyMPQTestCase):
	def test_toolbar_buttons_in_order(self) -> None:
		gui = self.make_pympq()
		layout: list[str] = []
		for child in gui.toolbar._row.pack_slaves(): # pylint: disable=protected-access
			if isinstance(child, UI.Button):
				layout.append(getattr(child, '_tooltip_Tooltip').text)
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

	def test_manage_settings_button_opens_settings_dialog(self) -> None:
		gui = self.make_pympq()
		with mock.patch(SETTINGS_DIALOG) as settings_dialog:
			self.invoke(toolbar_button(gui, 'Manage Settings'))
		settings_dialog.assert_called_once_with(gui, gui.config_)


class Test_PyMPQ_shortcuts(PyMPQTestCase):
	def test_manage_settings_shortcut_triggers_once(self) -> None:
		with mock.patch.object(PyMPQ, 'mansets') as mansets:
			gui = self.make_pympq()
			self.show(gui)
			self.shortcut(gui, UI.Ctrl.m)
		mansets.assert_called_once_with()

	def test_disabled_item_shortcut_does_nothing(self) -> None:
		with mock.patch.object(PyMPQ, 'extract') as extract:
			gui = self.make_pympq()
			self.show(gui)
			self.shortcut(gui, UI.Ctrl.e)
		extract.assert_not_called()

	def test_enabled_item_shortcut_triggers_once(self) -> None:
		with mock.patch.object(PyMPQ, 'extract') as extract:
			gui = self.make_pympq()
			self.seed_mpq(gui, [b'readme.txt'])
			with mock.patch.object(gui.listbox, 'cur_selection', return_value=[0]):
				gui.action_states()
			self.show(gui)
			self.shortcut(gui, UI.Ctrl.e)
		extract.assert_called_once_with()

	def test_compression_and_encrypt_shortcuts_update_settings(self) -> None:
		gui = self.make_pympq()
		self.show(gui)
		self.shortcut(gui, UI.Key.F3)
		self.assertEqual(gui.compvar.get(), str(CompressionOption.Standard.setting()))
		self.shortcut(gui, UI.Key.F9)
		self.assertEqual(gui.compvar.get(), str(CompressionOption.Deflate.setting(0)))
		encrypt = gui.encvar.get()
		self.shortcut(gui, UI.Key.F5)
		self.assertEqual(gui.encvar.get(), not encrypt)
