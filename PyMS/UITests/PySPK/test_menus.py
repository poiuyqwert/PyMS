
from .utils import PySPKTestCase

from ...Utilities import UIKit as UI
from ...Utilities.UIKit.EventPattern import EventPattern
from ...PySPK.PySPK import PySPK
from ...PySPK.Tool import Tool

from unittest import mock

SEPARATOR = '----'
GAP = '<gap>'
SECTION = '<section>'
FLEXIBLE = '<flexible>'

ToolbarLayout = list[str | tuple[str, EventPattern | None]]

EXPECTED_MENUS: list[tuple[str, list[str]]] = [
	('File', [
		'New',
		'Open...',
		SEPARATOR,
		'Save',
		'Save As...',
		SEPARATOR,
		'Import from BMP...',
		'Export to BMP...',
		SEPARATOR,
		'Close',
		SEPARATOR,
		'Check for Updates...',
		SEPARATOR,
		'Exit',
	]),
	('View', [
		'Preview...',
	]),
	('Layer', [
		'Add Layer',
		'Remove Layer',
		SEPARATOR,
		'Move Layer Up',
		'Move Layer Down',
		SEPARATOR,
		'Auto-Lock',
		'Auto-Visibility',
	]),
	('Palette', [
		'Import Star...',
		'Export Star...',
	]),
	('Stars', [
		'Delete Selected Stars...',
		SEPARATOR,
		'Move Stars Up (in List Order)',
		'Move Stars Down (in List Order)',
		'Nudge Stars',
		SEPARATOR,
		'Select Tool',
		'Move Tool',
		'Draw Tool',
	]),
	('Settings', [
		'Manage Settings...',
		SEPARATOR,
		'Set as Default *.spk Editor (Windows Only)',
	]),
	('Help', [
		'View Help',
		SEPARATOR,
		'Donate...',
		'About PySPK',
	]),
]

EXPECTED_NUDGE_MENU = ['Up', 'Down', 'Left', 'Right']

EXPECTED_TOOLBAR: ToolbarLayout = [
	('New', UI.Ctrl.n),
	('Open', UI.Ctrl.o),
	GAP,
	('Save', UI.Ctrl.s),
	('Save As', UI.Ctrl.Alt.a),
	GAP,
	('Import from BMP', UI.Ctrl.i),
	('Export to BMP', UI.Ctrl.e),
	GAP,
	('Close', UI.Ctrl.w),
	SECTION,
	('Preview', UI.Ctrl.l),
	SECTION,
	('Manage Settings', UI.Ctrl.m),
	SECTION,
	('Set as Default *.spk Editor (Windows Only)', None),
	('View Help', UI.Key.F1),
	('About PySPK', None),
	('Donate', None),
	('Check for Updates', None),
	SECTION,
	('Exit', UI.Shortcut.Exit),
]

EXPECTED_LAYERS_TOOLBAR: ToolbarLayout = [
	('Add Layer', UI.Key.Insert),
	('Remove Layer', None),
	FLEXIBLE,
	('Move Layer Up', None),
	('Move Layer Down', None),
	GAP,
	('Auto-Lock', None),
	('Auto-Visibility', None),
]

EXPECTED_PALETTE_TOOLBAR: ToolbarLayout = [
	('Select', UI.Key.m),
	('Move', UI.Key.v),
	('Draw', UI.Key.p),
	FLEXIBLE,
	('Import Star', None),
	('Export Star', None),
]

EXPECTED_STARS_TOOLBAR: ToolbarLayout = [
	('Select', UI.Key.m),
	('Move', UI.Key.v),
	('Draw', UI.Key.p),
	FLEXIBLE,
	('Move Stars Up', None),
	('Move Stars Down', None),
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


def entry_option(menu: UI.Menu, label: str, option: str) -> str:
	return str(menu.entrycget(menu_entries(menu).index(label), option))


def toolbar_layout(toolbar: UI.Toolbar) -> list[str]:
	row = toolbar._row # pylint: disable=protected-access
	layout: list[str] = []
	for child in row.pack_slaves():
		if isinstance(child, (UI.Button, UI.Radiobutton, UI.Checkbutton)):
			layout.append(getattr(child, '_tooltip_Tooltip').text)
		elif str(child.pack_info()['expand']) in ('1', 'True', 'true'):
			layout.append(FLEXIBLE)
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


class Test_PySPK_menubar(PySPKTestCase):
	def test_top_level_menus_in_order(self) -> None:
		gui = self.open_pyspk()
		self.assertEqual(menu_entries(gui.menu), [label for label, _ in EXPECTED_MENUS])

	def test_menu_items_in_order(self) -> None:
		gui = self.open_pyspk()
		for label, expected in EXPECTED_MENUS:
			with self.subTest(menu=label):
				self.assertEqual(menu_entries(cascade(gui.menu, label)), expected)

	def test_nudge_submenu_items_in_order(self) -> None:
		gui = self.open_pyspk()
		self.assertEqual(menu_entries(cascade(cascade(gui.menu, 'Stars'), 'Nudge Stars')), EXPECTED_NUDGE_MENU)

	def test_delete_accelerator_belongs_to_stars_not_layers(self) -> None:
		gui = self.open_pyspk()
		self.assertEqual(entry_option(cascade(gui.menu, 'Layer'), 'Remove Layer', 'accelerator'), '')
		self.assertEqual(entry_option(cascade(gui.menu, 'Stars'), 'Delete Selected Stars...', 'accelerator'), UI.Key.Delete.name())

	def test_file_items_are_disabled_with_no_document(self) -> None:
		gui = self.open_pyspk()
		file_menu = cascade(gui.menu, 'File')
		stars_menu = cascade(gui.menu, 'Stars')
		self.assertEqual(entry_option(file_menu, 'Save', 'state'), UI.DISABLED)
		self.assertEqual(entry_option(stars_menu, 'Draw Tool', 'state'), UI.DISABLED)

	def test_items_follow_open_document_and_star_selection(self) -> None:
		gui = self.with_layers_of_stars()
		file_menu = cascade(gui.menu, 'File')
		stars_menu = cascade(gui.menu, 'Stars')
		self.assertEqual(entry_option(file_menu, 'Save', 'state'), UI.NORMAL)
		self.assertEqual(entry_option(stars_menu, 'Draw Tool', 'state'), UI.NORMAL)
		self.assertEqual(entry_option(stars_menu, 'Delete Selected Stars...', 'state'), UI.DISABLED)
		assert gui.spk is not None
		gui.selected_stars.append(gui.spk.layers[0].stars[0])
		gui.update_selection()
		self.assertEqual(entry_option(stars_menu, 'Delete Selected Stars...', 'state'), UI.NORMAL)
		self.assertEqual(entry_option(stars_menu, 'Move Stars Up (in List Order)', 'state'), UI.NORMAL)


class Test_PySPK_toolbars(PySPKTestCase):
	def test_main_toolbar_buttons_in_order(self) -> None:
		gui = self.open_pyspk()
		self.assertEqual(toolbar_layout(gui.toolbar), expected_layout(EXPECTED_TOOLBAR))

	def test_layers_toolbar_buttons_in_order(self) -> None:
		gui = self.open_pyspk()
		self.assertEqual(toolbar_layout(gui.edit_toolbar), expected_layout(EXPECTED_LAYERS_TOOLBAR))

	def test_palette_toolbar_buttons_in_order(self) -> None:
		gui = self.open_pyspk()
		self.assertEqual(toolbar_layout(gui.palette_tab.toolbar), expected_layout(EXPECTED_PALETTE_TOOLBAR))

	def test_stars_toolbar_buttons_in_order(self) -> None:
		gui = self.open_pyspk()
		self.assertEqual(toolbar_layout(gui.stars_tab.toolbar), expected_layout(EXPECTED_STARS_TOOLBAR))


class Test_PySPK_shortcuts(PySPKTestCase):
	def test_manage_settings_shortcut_triggers_once(self) -> None:
		with mock.patch.object(PySPK, 'mpqsettings') as mpqsettings:
			gui = self.open_pyspk()
			self.show(gui)
			self.shortcut(gui, UI.Ctrl.m)
		mpqsettings.assert_called_once_with()

	def test_disabled_item_shortcut_does_nothing(self) -> None:
		with mock.patch.object(PySPK, 'export') as export:
			gui = self.open_pyspk()
			self.show(gui)
			self.shortcut(gui, UI.Ctrl.e)
		export.assert_not_called()

	def test_insert_is_bound_on_the_window_for_add_layer(self) -> None:
		# Tk on macOS can't synthesize an `Insert` key event (the keysym arrives as `??`),
		# so check the window binding exists and the menu item adds the layer.
		gui = self.with_layers_of_stars()
		assert gui.spk is not None
		self.assertTrue(gui.bind(UI.Key.Insert()))
		layer_menu = cascade(gui.menu, 'Layer')
		self.invoke_menu(layer_menu, menu_entries(layer_menu).index('Add Layer'))
		self.assertEqual(len(gui.spk.layers), 2)

	def test_delete_and_backspace_delete_selected_stars_once(self) -> None:
		with mock.patch.object(PySPK, 'delete_stars') as delete_stars, mock.patch.object(PySPK, 'remove_layer') as remove_layer:
			gui = self.with_layers_of_stars()
			assert gui.spk is not None
			gui.selected_stars.append(gui.spk.layers[0].stars[0])
			gui.update_selection()
			self.show(gui)
			self.shortcut(gui, UI.Key.Delete)
			self.assertEqual(delete_stars.call_count, 1)
			self.shortcut(gui, UI.Key.Backspace)
			self.assertEqual(delete_stars.call_count, 2)
		remove_layer.assert_not_called()

	def test_delete_and_backspace_do_nothing_without_selected_stars(self) -> None:
		with mock.patch.object(PySPK, 'delete_stars') as delete_stars, mock.patch.object(PySPK, 'remove_layer') as remove_layer:
			gui = self.with_layers_of_stars()
			self.show(gui)
			self.shortcut(gui, UI.Key.Delete)
			self.shortcut(gui, UI.Key.Backspace)
		delete_stars.assert_not_called()
		remove_layer.assert_not_called()

	def test_arrow_nudges_selected_star_once(self) -> None:
		gui = self.with_layers_of_stars()
		assert gui.spk is not None
		star = gui.spk.layers[0].stars[0]
		gui.selected_stars.append(star)
		gui.update_selection()
		self.show(gui)
		x, y = star.x, star.y
		self.shortcut(gui, UI.Key.Right)
		self.shortcut(gui, UI.Key.Down)
		self.assertEqual((star.x, star.y), (x + 1, y + 1))

	def test_tool_shortcuts_set_the_tool(self) -> None:
		gui = self.with_layers_of_stars()
		self.show(gui)
		self.shortcut(gui, UI.Key.v)
		self.assertEqual(gui.get_tool(), Tool.move)
		self.shortcut(gui, UI.Key.p)
		self.assertEqual(gui.get_tool(), Tool.draw)
		self.shortcut(gui, UI.Key.m)
		self.assertEqual(gui.get_tool(), Tool.select)

	def test_tool_shortcuts_do_nothing_without_a_file(self) -> None:
		gui = self.open_pyspk()
		self.show(gui)
		self.shortcut(gui, UI.Key.p)
		self.assertEqual(gui.get_tool(), Tool.select)

class Test_PySPK_tool_radios(PySPKTestCase):
	def tool_buttons(self, toolbar: UI.Toolbar) -> list[UI.Radiobutton]:
		row = toolbar._row # pylint: disable=protected-access
		return [child for child in row.winfo_children() if isinstance(child, UI.Radiobutton)]

	def test_tab_toolbar_tool_buttons_select_their_tool(self) -> None:
		gui = self.with_layers_of_stars()
		for tab in (gui.palette_tab, gui.stars_tab):
			buttons = self.tool_buttons(tab.toolbar)
			# Toolbar order is Select, Move, Draw
			for button, tool in ((buttons[1], Tool.move), (buttons[2], Tool.draw), (buttons[0], Tool.select)):
				with self.subTest(tab=type(tab).__name__, tool=tool):
					button.invoke()
					self.pump(gui)
					self.assertEqual(gui.get_tool(), tool)
