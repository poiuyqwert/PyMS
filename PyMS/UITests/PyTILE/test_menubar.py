from .utils import PyTILETestCase, menu_entries, menubar_cascades

from ...PyTILE.PyTILE import PyTILE
from ...PyTILE.MegaEditorMode import MegaEditorMode
from ...FileFormats.Tileset.Tileset import TileType
from ...Utilities import UIKit as UI

from unittest import mock


class Test_Menubar_Layout(PyTILETestCase):
	def test_top_level_menus(self) -> None:
		gui = self.open_pytile()
		self.assertEqual(list(menubar_cascades(gui)), ['File', 'View', 'Group', 'MegaTile', 'Settings', 'Help'])

	def test_menu_items(self) -> None:
		gui = self.open_pytile()
		menus = {label: menu_entries(menu) for label, menu in menubar_cascades(gui).items()}
		self.assertEqual(menus, {
			'File': ['Open...', '-', 'Save', 'Save As...', '-', 'Close', '-', 'Exit'],
			'View': ['MegaTile Group Palette...', '-', 'Scroll Group Palette Up', 'Scroll Group Palette Down'],
			'Group': ['Copy Group Settings', 'Paste Group Settings'],
			'MegaTile': [
				'Copy MegaTile Flags', 'Paste MegaTile Flags', '-',
				'Apply Height Flags to Group', 'Apply Walkability Flags to Group', 'Apply Blocks View Flags to Group', 'Apply Ramp Flags to Group', 'Apply All Flags to Group', '-',
				'Exclude Null Tiles',
			],
			'Settings': ['Manage Settings...', '-', 'Set as Default *.cv5 Editor (Windows Only)'],
			'Help': ['View Help', '-', 'Donate...', 'About PyTILE'],
		})

	def test_exclude_null_tiles_is_a_checkbutton(self) -> None:
		gui = self.open_pytile()
		megatile_menu = menubar_cascades(gui)['MegaTile']
		self.assertEqual(megatile_menu.type(megatile_menu.index(UI.END) or 0), 'checkbutton')


class Test_Toolbar_Layout(PyTILETestCase):
	def _toolbar_layout(self, gui: PyTILE) -> list[str]:
		# Buttons as their tooltip text, gaps as '|', and sections as '||'.
		row = gui.toolbar.winfo_children()[0]
		layout: list[str] = []
		for child in row.winfo_children():
			if isinstance(child, UI.Button):
				layout.append(getattr(child, '_tooltip_Tooltip').text)
			else:
				layout.append('|' if int(child.cget('width')) == UI.Toolbar.GAP_SIZE else '||')
		return layout

	def test_button_order(self) -> None:
		gui = self.open_pytile()
		self.assertEqual(self._toolbar_layout(gui), [
			f'Open ({UI.Ctrl.o.description()})',
			'|',
			f'Save ({UI.Ctrl.s.description()})',
			f'Save As ({UI.Ctrl.Alt.a.description()})',
			'|',
			f'Close ({UI.Ctrl.w.description()})',
			'||',
			f'MegaTile Group Palette ({UI.Ctrl.p.description()})',
			'||',
			f'Manage Settings ({UI.Ctrl.m.description()})',
			'||',
			'Set as Default *.cv5 Editor (Windows Only)',
			f'View Help ({UI.Key.F1.description()})',
			'About PyTILE',
			'Donate',
			'||',
			f'Exit ({UI.Shortcut.Exit.description()})',
		])


class Test_Shortcuts(PyTILETestCase):
	def test_palette_shortcut_opens_group_palette_once(self) -> None:
		gui = self.with_open_tileset()
		self.show(gui)
		with mock.patch.object(PyTILE, 'choose') as choose:
			self.shortcut(gui, UI.Ctrl.p)
		choose.assert_called_once_with(TileType.group)

	def test_disabled_item_shortcut_does_nothing(self) -> None:
		# With no tileset open the palette item is disabled, so its shortcut must not reach the handler.
		gui = self.open_pytile()
		self.show(gui)
		with mock.patch.object(PyTILE, 'choose') as choose:
			self.shortcut(gui, UI.Ctrl.p)
		choose.assert_not_called()

	def test_apply_flags_shortcut_applies_once(self) -> None:
		gui = self.with_open_tileset()
		self.show(gui)
		with mock.patch.object(gui, 'megatile_apply_all') as apply_all, mock.patch.object(gui, 'close') as close:
			self.shortcut(gui, UI.Shift.Ctrl.w)
		apply_all.assert_called_once_with(MegaEditorMode.walkability)
		close.assert_not_called()

	def test_exclude_null_tiles_shortcut_toggles_once(self) -> None:
		gui = self.open_pytile()
		self.show(gui)
		before = gui.apply_all_exclude_nulls.get()
		self.shortcut(gui, UI.Shift.Ctrl.n)
		self.assertEqual(gui.apply_all_exclude_nulls.get(), 0 if before else 1)

	def test_page_down_scrolls_group_palette_once(self) -> None:
		gui = self.with_open_tileset()
		self.show(gui)
		with mock.patch.object(gui.palette, 'scroll_page') as scroll_page:
			self.shortcut(gui, UI.Key.Next)
		scroll_page.assert_called_once_with(1)


class Test_Copy_Item_States(PyTILETestCase):
	def _copy_group_state(self, gui: PyTILE) -> str:
		group_menu = menubar_cascades(gui)['Group']
		return str(group_menu.entrycget(0, 'state'))

	def test_copy_megatile_flags_follows_copy_options(self) -> None:
		gui = self.with_open_tileset()
		megatile_menu = menubar_cascades(gui)['MegaTile']
		for var in (gui.copy_mega_height, gui.copy_mega_walkable, gui.copy_mega_sight, gui.copy_mega_ramp):
			var.set(False)
		self.assertEqual(str(megatile_menu.entrycget(0, 'state')), UI.DISABLED)
		gui.copy_mega_ramp.set(True)
		self.assertEqual(str(megatile_menu.entrycget(0, 'state')), UI.NORMAL)

	def test_copy_group_settings_follows_the_shown_panel(self) -> None:
		# One Group item covers both the normal and the doodad panel, so its state follows the options of
		# whichever panel the copy will read from.
		gui = self.with_open_tileset()
		for _, var in gui.options_copy_tilegroup.options + gui.options_copy_doodadgroup.options:
			var.set(False)
		gui.copy_doodadgroup_name.set(True)
		self.assertEqual(self._copy_group_state(gui), UI.DISABLED)
		gui.doodad.set(True)
		self.assertEqual(self._copy_group_state(gui), UI.NORMAL)
		gui.copy_doodadgroup_name.set(False)
		self.assertEqual(self._copy_group_state(gui), UI.DISABLED)

	def test_copy_items_disabled_without_tileset(self) -> None:
		gui = self.open_pytile()
		self.assertEqual(self._copy_group_state(gui), UI.DISABLED)
