from .utils import PyGRPTestCase

from ...Utilities import UIKit as UI
from ...Utilities.UIKit.EventPattern import EventPattern
from ...PyGRP.PyGRP import PyGRP
from ...PyGRP.utils import BMPStyle

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
		'Close',
		SEPARATOR,
		'Exit',
	]),
	('Edit', [
		'Select All',
	]),
	('View', [
		'Hex Frame Numbers',
		'Palette',
		SEPARATOR,
		'Show Preview',
		'GRP Outline (Green)',
		'Frame Outline (Red)',
		'Background Color...',
		SEPARATOR,
		'Playback',
	]),
	('Frames', [
		'Import Frames...',
		'Export Selected Frames...',
		SEPARATOR,
		'Move Frames Up',
		'Move Frames Down',
		SEPARATOR,
		'Remove Frames',
	]),
	('Settings', [
		'Manage Settings...',
		'BMP Style',
		'Save Uncompressed',
		SEPARATOR,
		'Set as Default *.grp Editor (Windows Only)',
	]),
	('Help', [
		'View Help',
		SEPARATOR,
		'Donate...',
		'About PyGRP',
	]),
]

EXPECTED_PLAYBACK = [
	'Jump to First Frame',
	'Jump 17 Frames Back',
	'Jump 1 Frame Back',
	'Jump 1 Frame Forward',
	'Jump 17 Frames Forward',
	'Jump to Last Frame',
	SEPARATOR,
	'Play Every 17th Frame Backward',
	'Play Every Frame Backward',
	'Stop Playing',
	'Play Every Frame Forward',
	'Play Every 17th Frame Forward',
	SEPARATOR,
	'Loop Preview',
]

EXPECTED_TOOLBAR: list[str | tuple[str, EventPattern | None]] = [
	('New', UI.Ctrl.n),
	('Open', UI.Ctrl.o),
	GAP,
	('Save', UI.Ctrl.s),
	('Save As', UI.Ctrl.Alt.a),
	GAP,
	('Close', UI.Ctrl.w),
	SECTION,
	('Import Frames', UI.Ctrl.i),
	('Export Selected Frames', UI.Ctrl.e),
	GAP,
	('Move Frames Up', UI.Ctrl.u),
	('Move Frames Down', UI.Ctrl.d),
	GAP,
	('Remove Frames', UI.Key.Delete),
	SECTION,
	('Manage Settings', UI.Ctrl.m),
	SECTION,
	('Set as Default *.grp Editor (Windows Only)', None),
	('View Help', UI.Key.F1),
	('About PyGRP', None),
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


class Test_PyGRP_menubar(PyGRPTestCase):
	def test_top_level_menus_in_order(self) -> None:
		gui = self.make_window(PyGRP)
		self.assertEqual(menu_entries(gui.menu), [label for label, _ in EXPECTED_MENUS])

	def test_menu_items_in_order(self) -> None:
		gui = self.make_window(PyGRP)
		for label, expected in EXPECTED_MENUS:
			with self.subTest(menu=label):
				self.assertEqual(menu_entries(cascade(gui.menu, label)), expected)

	def test_submenu_items_in_order(self) -> None:
		gui = self.make_window(PyGRP)
		view_menu = cascade(gui.menu, 'View')
		self.assertEqual(menu_entries(cascade(view_menu, 'Playback')), EXPECTED_PLAYBACK)
		self.assertEqual(menu_entries(cascade(view_menu, 'Palette')), list(gui.palettes))
		settings_menu = cascade(gui.menu, 'Settings')
		self.assertEqual(menu_entries(cascade(settings_menu, 'BMP Style')), [style.display_name for style in BMPStyle.ALL()])

	def test_frame_items_disabled_without_file(self) -> None:
		gui = self.make_window(PyGRP)
		frames_menu = cascade(gui.menu, 'Frames')
		self.assertEqual(entry_state(frames_menu, 'Import Frames...'), UI.DISABLED)
		self.assertEqual(entry_state(frames_menu, 'Remove Frames'), UI.DISABLED)

	def test_frame_items_follow_selection_state(self) -> None:
		gui = self.with_frames(3)
		frames_menu = cascade(gui.menu, 'Frames')
		gui.listbox.select_clear(0, UI.END)
		gui.listbox.select_set(0)
		gui.action_states()
		self.assertEqual(entry_state(frames_menu, 'Import Frames...'), UI.NORMAL)
		self.assertEqual(entry_state(frames_menu, 'Remove Frames'), UI.NORMAL)
		self.assertEqual(entry_state(frames_menu, 'Move Frames Up'), UI.DISABLED)
		self.assertEqual(entry_state(frames_menu, 'Move Frames Down'), UI.NORMAL)

	def test_playback_items_follow_preview_state(self) -> None:
		gui = self.with_frames(3)
		gui.action_states()
		playback_menu = cascade(cascade(gui.menu, 'View'), 'Playback')
		self.assertEqual(entry_state(playback_menu, 'Jump to Last Frame'), UI.NORMAL)
		self.assertEqual(entry_state(playback_menu, 'Stop Playing'), UI.DISABLED)
		gui.showpreview.set(False)
		gui.showprev()
		self.assertEqual(entry_state(playback_menu, 'Jump to Last Frame'), UI.DISABLED)

	def test_view_checks_share_widget_variables(self) -> None:
		gui = self.make_window(PyGRP)
		view_menu = cascade(gui.menu, 'View')
		hex_index = menu_entries(view_menu).index('Hex Frame Numbers')
		self.assertEqual(str(view_menu.entrycget(hex_index, 'variable')), str(gui.hex))
		before = gui.hex.get()
		self.invoke_menu(view_menu, hex_index)
		self.assertEqual(gui.hex.get(), not before)

	def test_palette_radio_selects_palette_list_row(self) -> None:
		gui = self.make_window(PyGRP)
		names = list(gui.palettes)
		if len(names) < 2:
			self.skipTest('Needs at least two bundled palettes')
		target = next(name for name in names if name != gui.pal)
		palette_menu = cascade(cascade(gui.menu, 'View'), 'Palette')
		self.invoke_menu(palette_menu, names.index(target))
		self.assertEqual(gui.pal, target)
		self.assertEqual([int(i) for i in gui.pallist.curselection()], [names.index(target)])

	def test_palette_list_selection_updates_palette_radios(self) -> None:
		gui = self.make_window(PyGRP)
		names = list(gui.palettes)
		if len(names) < 2:
			self.skipTest('Needs at least two bundled palettes')
		target = next(name for name in names if name != gui.pal)
		gui.pallist.select_clear(0, UI.END)
		gui.pallist.select_set(names.index(target))
		gui.changepalette()
		self.assertEqual(gui.palette_name.get(), target)


class Test_PyGRP_toolbar(PyGRPTestCase):
	def test_toolbar_buttons_in_order(self) -> None:
		gui = self.make_window(PyGRP)
		row = gui.toolbar._row # pylint: disable=protected-access
		layout: list[str] = []
		for child in row.pack_slaves():
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


class Test_PyGRP_shortcuts(PyGRPTestCase):
	def test_manage_settings_shortcut_triggers_once(self) -> None:
		with mock.patch.object(PyGRP, 'settings') as settings:
			gui = self.make_window(PyGRP)
			self.show(gui)
			self.shortcut(gui, UI.Ctrl.m)
		settings.assert_called_once_with()

	def test_move_up_shortcut_triggers_once(self) -> None:
		with mock.patch.object(PyGRP, 'shift') as shift:
			gui = self.with_frames(3)
			gui.listbox.select_clear(0, UI.END)
			gui.listbox.select_set(1)
			gui.action_states()
			self.show(gui)
			self.shortcut(gui, UI.Ctrl.u)
		shift.assert_called_once_with(-1)

	def test_disabled_item_shortcut_does_nothing(self) -> None:
		with mock.patch.object(PyGRP, 'exports') as exports:
			gui = self.make_window(PyGRP)
			self.show(gui)
			self.shortcut(gui, UI.Ctrl.e)
		exports.assert_not_called()

	def test_select_all_shortcut_selects_every_frame(self) -> None:
		gui = self.with_frames(3)
		gui.listbox.select_clear(0, UI.END)
		self.show(gui)
		self.shortcut(gui, UI.Ctrl.a)
		self.assertEqual(self.selection(gui), [0, 1, 2])
