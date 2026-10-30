from .utils import PyBINTestCase

from ...PyBIN.PyBIN import PyBIN
from ...FileFormats import DialogBIN
from ...Utilities import UIKit as UI

from unittest import mock

SEPARATOR = '----'
GAP = '<gap>'
SECTION = '<section>'
SPACER = '<spacer>'

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

def submenu(menu: UI.Menu, label: str) -> UI.Menu:
	return menu.nametowidget(menu.entrycget(label, 'menu'))

def menu_index(menu: UI.Menu, label: str) -> int:
	index = menu.index(label)
	assert index is not None
	return index

def toolbar_layout(toolbar: UI.Toolbar) -> list[str]:
	# The toolbar's buttons and spacers in packed order; spacers are Frames sized by kind.
	layout: list[str] = []
	row = toolbar.pack_slaves()[0]
	for child in row.pack_slaves():
		tooltip = getattr(child, '_tooltip_Tooltip', None)
		if tooltip is not None:
			layout.append(tooltip.text)
		elif child.pack_info().get('expand'):
			layout.append(SPACER)
		elif int(child.cget('width')) == UI.Toolbar.SECTION_SIZE:
			layout.append(SECTION)
		else:
			layout.append(GAP)
	return layout

def with_key(label: str, shortcut: UI.EventPattern) -> str:
	return f'{label} ({shortcut.description()})'


class Test_PyBIN_menubar(PyBINTestCase):
	def test_menubar_top_level_menus(self) -> None:
		gui = self.make_pybin()
		self.assertEqual(menu_entries(gui.menu), ['File', 'View', 'Widgets', 'Settings', 'Help'])

	def test_menu_items(self) -> None:
		gui = self.make_pybin()
		expected = {
			'File': ['New', 'Open...', SEPARATOR, 'Save', 'Save As...', SEPARATOR, 'Import from TXT...', 'Export to TXT...', SEPARATOR, 'Close', SEPARATOR, 'Check for Updates...', SEPARATOR, 'Exit'],
			'View': ['Preview Settings Panel'],
			'Widgets': ['Add Widget', 'Remove Widget', SEPARATOR, 'Edit Widget...', SEPARATOR, 'Move Widget Up', 'Move Widget Down'],
			'Settings': ['Manage Settings...', SEPARATOR, 'Set as Default *.bin Editor (Windows Only)'],
			'Help': ['View Help', SEPARATOR, 'Donate...', 'About PyBIN'],
		}
		for label, items in expected.items():
			with self.subTest(menu=label):
				self.assertEqual(menu_entries(submenu(gui.menu, label)), items)

	def test_add_widget_submenu_matches_type_popup(self) -> None:
		gui = self.make_pybin()
		add_menu = submenu(submenu(gui.menu, 'Widgets'), 'Add Widget')
		entries = menu_entries(add_menu)
		self.assertEqual(entries, menu_entries(gui.type_menu))
		self.assertEqual(entries[-2:], [SEPARATOR, 'Group'])
		self.assertEqual(entries[0], DialogBIN.BINWidget.TYPE_NAMES[DialogBIN.BINWidget.TYPE_DEFAULT_BTN])
		self.assertEqual(entries[-3], DialogBIN.BINWidget.TYPE_NAMES[DialogBIN.BINWidget.TYPE_HTML] + ' (SC:R)')

	def test_shortcut_accelerators(self) -> None:
		gui = self.make_pybin()
		file_menu = submenu(gui.menu, 'File')
		self.assertEqual(file_menu.entrycget('Save As...', 'accelerator'), UI.Ctrl.Alt.a.name())
		self.assertEqual(submenu(gui.menu, 'Help').entrycget('View Help', 'accelerator'), UI.Key.F4.name())
		self.assertEqual(submenu(gui.menu, 'Widgets').entrycget('Edit Widget...', 'accelerator'), UI.Key.Return.name())


class Test_PyBIN_toolbar(PyBINTestCase):
	def test_main_toolbar_layout(self) -> None:
		gui = self.make_pybin()
		self.assertEqual(toolbar_layout(gui.toolbar), [
			with_key('New', UI.Ctrl.n),
			with_key('Open', UI.Ctrl.o),
			GAP,
			with_key('Save', UI.Ctrl.s),
			with_key('Save As', UI.Ctrl.Alt.a),
			GAP,
			with_key('Import from TXT', UI.Ctrl.i),
			with_key('Export to TXT', UI.Ctrl.e),
			GAP,
			with_key('Close', UI.Ctrl.w),
			SECTION,
			with_key('Manage Settings', UI.Ctrl.m),
			SECTION,
			'Set as Default *.bin Editor (Windows Only)',
			with_key('View Help', UI.Key.F4),
			'About PyBIN',
			'Donate',
			'Check for Updates',
			SECTION,
			with_key('Exit', UI.Shortcut.Exit),
		])

	def test_widgets_toolbar_layout(self) -> None:
		gui = self.make_pybin()
		self.assertEqual(toolbar_layout(gui.widgets_toolbar), [
			'Add Widget',
			'Remove Widget',
			with_key('Edit Widget', UI.Key.Return),
			SPACER,
			'Toggle Preview Settings',
			SPACER,
			'Move Widget Up',
			'Move Widget Down',
		])


class Test_PyBIN_shortcuts(PyBINTestCase):
	def make_patched(self, target: str) -> tuple[PyBIN, mock.MagicMock]:
		handler = mock.MagicMock()
		gui = self.make_window(PyBIN, extra_patches={
			'PyMS.Utilities.MPQHandler.MPQHandler.get_file': {'return_value': None},
			f'PyMS.PyBIN.PyBIN.PyBIN.{target}': {'new': handler},
		})
		return (gui, handler)

	def test_shortcut_triggers_menu_action_once(self) -> None:
		gui, export = self.make_patched('export')
		gui.new()
		self.show(gui)
		self.shortcut(gui, UI.Ctrl.e)
		export.assert_called_once_with()

	def test_disabled_item_shortcut_does_nothing(self) -> None:
		gui, export = self.make_patched('export')
		self.show(gui)
		self.shortcut(gui, UI.Ctrl.e)
		export.assert_not_called()

	def test_return_edits_selected_node_once(self) -> None:
		gui, edit = self.make_patched('edit_node_settings')
		gui.new()
		assert gui.dialog is not None
		gui.select_node(gui.dialog)
		self.show(gui)
		self.shortcut(gui, UI.Key.Return)
		edit.assert_called_once_with()

	def test_return_without_selection_does_nothing(self) -> None:
		gui, edit = self.make_patched('edit_node_settings')
		gui.new()
		self.show(gui)
		self.shortcut(gui, UI.Key.Return)
		edit.assert_not_called()


class Test_PyBIN_menu_states(PyBINTestCase):
	def test_widget_items_follow_selection(self) -> None:
		gui = self.make_pybin()
		widgets_menu = submenu(gui.menu, 'Widgets')
		def state(label: str) -> str:
			return str(widgets_menu.entrycget(label, 'state'))
		self.assertEqual(state('Add Widget'), UI.NORMAL)
		self.assertEqual(state('Edit Widget...'), UI.DISABLED)
		assert gui.dialog is not None
		gui.select_node(gui.dialog)
		self.assertEqual(state('Edit Widget...'), UI.NORMAL)
		self.assertEqual(state('Remove Widget'), UI.DISABLED)
		gui.add_new_node(DialogBIN.BINWidget.TYPE_BUTTON)
		gui.add_new_node(DialogBIN.BINWidget.TYPE_BUTTON)
		self.assertEqual(state('Remove Widget'), UI.NORMAL)
		self.assertEqual(state('Move Widget Up'), UI.DISABLED)
		self.assertEqual(state('Move Widget Down'), UI.NORMAL)
		gui.mark_edited(False)
		gui.close()
		self.assertEqual(state('Add Widget'), UI.DISABLED)
		self.assertEqual(str(submenu(gui.menu, 'File').entrycget('Save', 'state')), UI.DISABLED)

	def test_add_widget_submenu_adds_widget(self) -> None:
		gui = self.make_pybin()
		assert gui.bin is not None
		add_menu = submenu(submenu(gui.menu, 'Widgets'), 'Add Widget')
		self.invoke_menu(add_menu, menu_index(add_menu, DialogBIN.BINWidget.TYPE_NAMES[DialogBIN.BINWidget.TYPE_BUTTON]))
		self.assertEqual(len(gui.bin.widgets), 2)
		self.assertEqual(gui.bin.widgets[1].type, DialogBIN.BINWidget.TYPE_BUTTON)

	def test_move_items_reorder_siblings(self) -> None:
		gui = self.make_pybin()
		assert gui.dialog is not None
		gui.select_node(gui.dialog)
		gui.add_new_node(DialogBIN.BINWidget.TYPE_BUTTON)
		first = gui.selected_node
		gui.add_new_node(DialogBIN.BINWidget.TYPE_CHECKBOX)
		second = gui.selected_node
		assert gui.dialog.children is not None
		self.assertEqual(gui.dialog.children, [second, first])
		widgets_menu = submenu(gui.menu, 'Widgets')
		self.invoke_menu(widgets_menu, menu_index(widgets_menu, 'Move Widget Down'))
		self.assertEqual(gui.dialog.children, [first, second])
		self.invoke_menu(widgets_menu, menu_index(widgets_menu, 'Move Widget Up'))
		self.assertEqual(gui.dialog.children, [second, first])

	def test_preview_settings_checkbutton_toggles_panel(self) -> None:
		gui = self.make_pybin()
		view_menu = submenu(gui.menu, 'View')
		shown = gui.show_preview_settings.get()
		self.invoke_menu(view_menu, 0)
		self.assertEqual(gui.show_preview_settings.get(), not shown)
		self.assertEqual(bool(gui.preview_settings_frame.winfo_manager()), not shown)
		self.invoke_menu(view_menu, 0)
		self.assertEqual(gui.show_preview_settings.get(), shown)
		self.assertEqual(bool(gui.preview_settings_frame.winfo_manager()), shown)
