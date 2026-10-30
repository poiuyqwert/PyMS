from .utils import PyDATTestCase

from ...PyDAT.PyDAT import PyDAT
from ...Utilities import UIKit as UI

from unittest import mock

SEPARATOR = '---'
GAP = '- gap -'
SECTION = '= section ='


def menu_labels(menu: UI.Menu) -> list[str]:
	end = menu.index(UI.END)
	if end is None:
		return []
	labels: list[str] = []
	for index in range(end + 1):
		if menu.type(index) == 'separator':
			labels.append(SEPARATOR)
		else:
			labels.append(str(menu.entrycget(index, 'label')))
	return labels


def submenu(menu: UI.Menu, label: str) -> UI.Menu:
	end = menu.index(UI.END) or 0
	for index in range(end + 1):
		if menu.type(index) == 'cascade' and menu.entrycget(index, 'label') == label:
			return menu.nametowidget(menu.entrycget(index, 'menu'))
	raise AssertionError(f'No {label!r} menu')


def item_state(menu: UI.Menu, label: str) -> str:
	return str(menu.entrycget(menu_labels(menu).index(label), 'state'))


def item_accelerator(menu: UI.Menu, label: str) -> str:
	return str(menu.entrycget(menu_labels(menu).index(label), 'accelerator'))


def toolbar_layout(toolbar: UI.Toolbar) -> list[str]:
	# Buttons are listed by tooltip text (without the shortcut suffix), spacers by kind.
	row = toolbar.winfo_children()[0]
	layout: list[str] = []
	for child in row.winfo_children():
		tooltip = getattr(child, '_tooltip_Tooltip', None)
		if tooltip is not None:
			layout.append(tooltip.text.split(' (')[0] if tooltip.text.endswith(')') and not tooltip.text.endswith('Only)') else tooltip.text)
		elif int(child.cget('width')) == UI.Toolbar.SECTION_SIZE:
			layout.append(SECTION)
		else:
			layout.append(GAP)
	return layout


class Test_PyDAT_menubar(PyDATTestCase):
	def test_top_level_menus(self) -> None:
		gui = self.make_pydat()
		self.assertEqual(menu_labels(gui.menu), ['File', 'Entry', 'Settings', 'Help'])

	def test_file_menu_items(self) -> None:
		gui = self.make_pydat()
		self.assertEqual(menu_labels(submenu(gui.menu, 'File')), [
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
			SEPARATOR,
			'Check for Updates...',
			SEPARATOR,
			'Exit',
		])

	def test_entry_menu_items(self) -> None:
		gui = self.make_pydat()
		self.assertEqual(menu_labels(submenu(gui.menu, 'Entry')), [
			'Add Entry (DatExtend)',
			'Set Entry Count (DatExtend)...',
			SEPARATOR,
			'Name Overrides...',
			'Reload Entry',
			SEPARATOR,
			'Copy Entry to Clipboard',
			'Copy Sub-Tab to Clipboard',
			'Paste from Clipboard',
		])

	def test_settings_menu_items(self) -> None:
		gui = self.make_pydat()
		self.assertEqual(menu_labels(submenu(gui.menu, 'Settings')), [
			'Manage Settings...',
			'Reload Data Files',
			SEPARATOR,
			'Set as Default *.dat Editor (Windows Only)',
		])

	def test_help_menu_items(self) -> None:
		gui = self.make_pydat()
		self.assertEqual(menu_labels(submenu(gui.menu, 'Help')), [
			'View Help',
			SEPARATOR,
			'Donate...',
			'About PyDAT',
		])

	def test_ctrl_r_accelerator_only_on_reload_entry(self) -> None:
		gui = self.make_pydat()
		self.assertEqual(item_accelerator(submenu(gui.menu, 'Entry'), 'Reload Entry'), UI.Ctrl.r.name())
		self.assertEqual(item_accelerator(submenu(gui.menu, 'Settings'), 'Reload Data Files'), '')

	def test_context_menu_items(self) -> None:
		gui = self.make_pydat()
		self.assertEqual(menu_labels(gui.listmenu), [
			'Copy Entry to Clipboard',
			'Copy Sub-Tab to Clipboard',
			'Paste from Clipboard',
			SEPARATOR,
			'Reload Entry',
			SEPARATOR,
			'Add Entry (DatExtend)',
			'Set Entry Count (DatExtend)',
			SEPARATOR,
			'Name Overrides...',
		])


class Test_PyDAT_toolbar(PyDATTestCase):
	def test_toolbar_layout(self) -> None:
		gui = self.make_pydat()
		self.assertEqual(toolbar_layout(gui.toolbar), [
			'New',
			'Open',
			'Open Directory',
			'Open MPQ',
			GAP,
			'Save',
			'Save As',
			'Save MPQ',
			GAP,
			'Import from TXT',
			'Export to TXT',
			SECTION,
			'Name Overrides',
			SECTION,
			'Manage Settings',
			'Reload Data Files',
			SECTION,
			'Set as Default *.dat Editor (Windows Only)',
			'View Help',
			'About PyDAT',
			'Donate',
			'Check for Updates',
			SECTION,
			'Exit',
		])


class Test_PyDAT_menu_states(PyDATTestCase):
	def test_copy_sub_tab_follows_active_tab(self) -> None:
		gui = self.with_new_dat('Units')
		entry_menu = submenu(gui.menu, 'Entry')
		self.assertEqual(item_state(entry_menu, 'Copy Sub-Tab to Clipboard'), UI.NORMAL)
		gui.dattabs.display('Weapons')
		self.pump(gui)
		self.assertEqual(item_state(entry_menu, 'Copy Sub-Tab to Clipboard'), UI.DISABLED)
		self.assertEqual(item_state(gui.listmenu, 'Copy Sub-Tab to Clipboard'), UI.DISABLED)
		gui.dattabs.display('Units')
		self.pump(gui)
		self.assertEqual(item_state(entry_menu, 'Copy Sub-Tab to Clipboard'), UI.NORMAL)
		self.assertEqual(item_state(gui.listmenu, 'Copy Sub-Tab to Clipboard'), UI.NORMAL)

	def test_expand_items_disabled_without_dat(self) -> None:
		gui = self.make_pydat()
		entry_menu = submenu(gui.menu, 'Entry')
		self.assertEqual(item_state(entry_menu, 'Add Entry (DatExtend)'), UI.DISABLED)
		self.assertEqual(item_state(entry_menu, 'Set Entry Count (DatExtend)...'), UI.DISABLED)

	def test_expand_items_follow_loaded_dat(self) -> None:
		gui = self.with_new_dat('Weapons')
		dat = gui.active_tab().get_dat_data().dat
		assert dat is not None
		expected = UI.NORMAL if dat.can_expand() else UI.DISABLED
		entry_menu = submenu(gui.menu, 'Entry')
		self.assertEqual(item_state(entry_menu, 'Add Entry (DatExtend)'), expected)
		self.assertEqual(item_state(gui.listmenu, 'Add Entry (DatExtend)'), expected)


class Test_PyDAT_shortcuts(PyDATTestCase):
	def test_copy_entry_shortcut_runs_once(self) -> None:
		with mock.patch.object(PyDAT, 'copy') as copy:
			gui = self.with_new_dat('Units')
			self.show(gui)
			self.shortcut(gui, UI.Shift.Ctrl.c)
		copy.assert_called_once_with()

	def test_ctrl_r_reloads_entry_not_data_files(self) -> None:
		with mock.patch.object(PyDAT, 'reload') as reload, mock.patch.object(PyDAT, 'open_files') as open_files:
			gui = self.with_new_dat('Units')
			self.show(gui)
			self.shortcut(gui, UI.Ctrl.r)
		reload.assert_called_once_with()
		open_files.assert_not_called()

	def test_copy_sub_tab_shortcut_runs_once_on_units_tab(self) -> None:
		with mock.patch.object(PyDAT, 'copy_subtab') as copy_subtab:
			gui = self.with_new_dat('Units')
			self.show(gui)
			self.shortcut(gui, UI.Ctrl.y)
		copy_subtab.assert_called_once_with()

	def test_disabled_copy_sub_tab_shortcut_does_nothing(self) -> None:
		with mock.patch.object(PyDAT, 'copy_subtab') as copy_subtab:
			gui = self.with_new_dat('Weapons')
			self.show(gui)
			self.shortcut(gui, UI.Ctrl.y)
		copy_subtab.assert_not_called()

	def test_disabled_add_entry_shortcut_does_nothing(self) -> None:
		with mock.patch.object(PyDAT, 'add_entry') as add_entry:
			gui = self.make_pydat()
			self.show(gui)
			self.shortcut(gui, UI.Shift.Ctrl.a)
		add_entry.assert_not_called()
