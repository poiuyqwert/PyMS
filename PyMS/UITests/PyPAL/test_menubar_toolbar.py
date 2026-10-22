
from .utils import PyPALTestCase, ASKCOLOR

from ...PyPAL.PyPAL import PyPAL
from ...FileFormats.Palette import Palette
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


class Test_PyPAL_menubar(PyPALTestCase):
	def test_top_level_menus(self) -> None:
		gui = self.open_pypal()
		self.assertEqual(menu_labels(gui.menu), ['File', 'Edit', 'Settings', 'Help'])

	def test_file_menu_items(self) -> None:
		gui = self.open_pypal()
		self.assertEqual(menu_labels(submenu(gui.menu, 'File')), [
			'New',
			'Open...',
			SEPARATOR,
			'Save',
			'Save As...',
			'Save as RIFF *.pal...',
			'Save as JASC *.pal...',
			'Save as StarCraft *.pal...',
			'Save as StarCraft Terrain *.wpe...',
			'Save as Adobe Color Table *.act...',
			SEPARATOR,
			'Close',
			SEPARATOR,
			'Exit',
		])

	def test_edit_menu_items(self) -> None:
		gui = self.open_pypal()
		self.assertEqual(menu_labels(submenu(gui.menu, 'Edit')), [
			'Copy',
			'Paste',
			SEPARATOR,
			'Edit Color...',
		])

	def test_settings_menu_items(self) -> None:
		gui = self.open_pypal()
		self.assertEqual(menu_labels(submenu(gui.menu, 'Settings')), [
			'Manage Settings...',
			SEPARATOR,
			'Set as Default *.pal and *.wpe Editor (Windows Only)',
		])

	def test_help_menu_items(self) -> None:
		gui = self.open_pypal()
		self.assertEqual(menu_labels(submenu(gui.menu, 'Help')), [
			'View Help',
			SEPARATOR,
			'Donate...',
			'About PyPAL',
		])

	def test_document_items_follow_document_state(self) -> None:
		document_items = {
			'File': ('Save As...', 'Save as RIFF *.pal...', 'Save as JASC *.pal...', 'Save as StarCraft *.pal...', 'Save as StarCraft Terrain *.wpe...', 'Save as Adobe Color Table *.act...', 'Close'),
			'Edit': ('Copy', 'Paste', 'Edit Color...'),
		}
		gui = self.open_pypal()
		for menu_label, labels in document_items.items():
			for label in labels:
				self.assertEqual(item_state(submenu(gui.menu, menu_label), label), UI.DISABLED, label)
		self.assertEqual(item_state(submenu(gui.menu, 'File'), 'Save'), UI.DISABLED)
		gui.new()
		for menu_label, labels in document_items.items():
			for label in labels:
				self.assertEqual(item_state(submenu(gui.menu, menu_label), label), UI.NORMAL, label)
		# A new palette has no format yet, so Save stays disabled until it's saved once.
		self.assertEqual(item_state(submenu(gui.menu, 'File'), 'Save'), UI.DISABLED)

	def test_save_enabled_for_loaded_palette(self) -> None:
		gui = self.with_loaded_palette()
		self.assertEqual(item_state(submenu(gui.menu, 'File'), 'Save'), UI.NORMAL)

	def test_edit_color_edits_selected_swatch(self) -> None:
		gui = self.with_new_palette()
		gui.select(None, 5)
		edit_menu = submenu(gui.menu, 'Edit')
		with mock.patch(ASKCOLOR, return_value=((10, 20, 30), '#0A141E')) as askcolor:
			self.invoke_menu(edit_menu, menu_labels(edit_menu).index('Edit Color...'))
		askcolor.assert_called_once()
		assert gui.palette is not None
		self.assertEqual(gui.palette.palette[5], (10, 20, 30))
		self.assertTrue(gui.edited)


class Test_PyPAL_save_as(PyPALTestCase):
	def test_save_as_new_palette_uses_starcraft_pal(self) -> None:
		gui = self.with_new_palette()
		with mock.patch.object(gui, 'saveas') as saveas:
			gui.saveas_current()
		saveas.assert_called_once_with(file_format=None, file_type=Palette.FileType.sc_pal)

	def test_save_as_keeps_current_format(self) -> None:
		gui = self.with_new_palette()
		cases = (
			(Palette.Format.riff, 'a.pal', Palette.FileType.riff),
			(Palette.Format.jasc, 'a.pal', Palette.FileType.jasc),
			(Palette.Format.raw_rgb, 'a.pal', Palette.FileType.sc_pal),
			(Palette.Format.raw_rgb, 'a.ACT', Palette.FileType.act),
			(Palette.Format.raw_rgba, 'a.wpe', Palette.FileType.wpe),
		)
		for pal_format, file, file_type in cases:
			gui.format = pal_format
			gui.file = file
			with mock.patch.object(gui, 'saveas') as saveas:
				gui.saveas_current()
			saveas.assert_called_once_with(file_format=pal_format, file_type=file_type)


class Test_PyPAL_toolbar(PyPALTestCase):
	def test_toolbar_layout(self) -> None:
		gui = self.open_pypal()
		self.assertEqual(toolbar_layout(gui.toolbar), [
			'New',
			'Open',
			GAP,
			'Save',
			'Save As',
			'Save as RIFF *.pal',
			'Save as JASC *.pal',
			'Save as StarCraft *.pal',
			'Save as StarCraft Terrain *.wpe',
			'Save as Adobe Color Table *.act',
			GAP,
			'Close',
			SECTION,
			'Manage Settings',
			SECTION,
			'Set as Default *.pal and *.wpe Editor (Windows Only)',
			'View Help',
			'About PyPAL',
			'Donate',
			SECTION,
			'Exit',
		])


class Test_PyPAL_menubar_shortcuts(PyPALTestCase):
	def test_close_shortcut_runs_once(self) -> None:
		with mock.patch.object(PyPAL, 'close') as close:
			gui = self.with_new_palette()
			self.show(gui)
			self.shortcut(gui, UI.Ctrl.w)
		close.assert_called_once_with()

	def test_disabled_close_shortcut_does_nothing(self) -> None:
		with mock.patch.object(PyPAL, 'close') as close:
			gui = self.open_pypal()
			self.show(gui)
			self.shortcut(gui, UI.Ctrl.w)
		close.assert_not_called()

	def test_copy_shortcut_runs_once(self) -> None:
		with mock.patch.object(PyPAL, 'copy') as copy:
			gui = self.with_new_palette()
			self.show(gui)
			self.shortcut(gui, UI.Ctrl.c)
		copy.assert_called_once_with()

	def test_paste_shortcut_runs_once(self) -> None:
		with mock.patch.object(PyPAL, 'paste') as paste:
			gui = self.with_new_palette()
			self.show(gui)
			self.shortcut(gui, UI.Ctrl.p)
		paste.assert_called_once_with()

	def test_disabled_paste_shortcut_does_nothing(self) -> None:
		with mock.patch.object(PyPAL, 'paste') as paste:
			gui = self.open_pypal()
			self.show(gui)
			self.shortcut(gui, UI.Ctrl.p)
		paste.assert_not_called()
