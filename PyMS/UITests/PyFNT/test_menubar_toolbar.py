from .utils import PyFNTTestCase

from ...PyFNT.PyFNT import PyFNT
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


def tooltip(label: str, shortcut: UI.EventPattern | None = None) -> str:
	if shortcut is None:
		return label
	return f'{label} ({shortcut.description()})'


def toolbar_buttons(toolbar: UI.Toolbar) -> dict[str, UI.Misc]:
	row = toolbar.winfo_children()[0]
	return {getattr(child, '_tooltip_Tooltip').text: child for child in row.winfo_children() if hasattr(child, '_tooltip_Tooltip')}


def toolbar_layout(toolbar: UI.Toolbar) -> list[str]:
	# Buttons are listed by tooltip text, spacers by kind.
	row = toolbar.winfo_children()[0]
	layout: list[str] = []
	for child in row.winfo_children():
		button_tooltip = getattr(child, '_tooltip_Tooltip', None)
		if button_tooltip is not None:
			layout.append(button_tooltip.text)
		elif int(child.cget('width')) == UI.Toolbar.SECTION_SIZE:
			layout.append(SECTION)
		else:
			layout.append(GAP)
	return layout


class Test_PyFNT_menubar(PyFNTTestCase):
	def test_top_level_menus(self) -> None:
		gui = self.open_pyfnt()
		self.assertEqual(menu_labels(gui.menu), ['File', 'Settings', 'Help'])

	def test_file_menu_items(self) -> None:
		gui = self.open_pyfnt()
		self.assertEqual(menu_labels(submenu(gui.menu, 'File')), [
			'New...',
			'Open...',
			SEPARATOR,
			'Save',
			'Save As...',
			SEPARATOR,
			'Import Font from BMP...',
			'Export Font to BMP...',
			SEPARATOR,
			'Close',
			SEPARATOR,
			'Check for Updates...',
			SEPARATOR,
			'Exit',
		])

	def test_settings_menu_items(self) -> None:
		gui = self.open_pyfnt()
		self.assertEqual(menu_labels(submenu(gui.menu, 'Settings')), [
			'Manage Settings...',
			SEPARATOR,
			'Set as Default *.fnt Editor (Windows Only)',
		])

	def test_help_menu_items(self) -> None:
		gui = self.open_pyfnt()
		self.assertEqual(menu_labels(submenu(gui.menu, 'Help')), [
			'View Help',
			SEPARATOR,
			'Donate...',
			'About PyFNT',
		])

	def test_document_items_disabled_without_document(self) -> None:
		gui = self.open_pyfnt()
		file_menu = submenu(gui.menu, 'File')
		for label in ('Save', 'Save As...', 'Export Font to BMP...', 'Close'):
			self.assertEqual(item_state(file_menu, label), UI.DISABLED, label)
		self.assertEqual(item_state(file_menu, 'Import Font from BMP...'), UI.NORMAL)

	def test_document_items_enabled_with_document(self) -> None:
		gui = self.with_new_font()
		file_menu = submenu(gui.menu, 'File')
		for label in ('Save', 'Save As...', 'Export Font to BMP...', 'Close'):
			self.assertEqual(item_state(file_menu, label), UI.NORMAL, label)


class Test_PyFNT_toolbar(PyFNTTestCase):
	def test_toolbar_layout(self) -> None:
		gui = self.open_pyfnt()
		self.assertEqual(toolbar_layout(gui.toolbar), [
			tooltip('New', UI.Ctrl.n),
			tooltip('Open', UI.Ctrl.o),
			GAP,
			tooltip('Save', UI.Ctrl.s),
			tooltip('Save As', UI.Ctrl.Alt.a),
			GAP,
			tooltip('Import Font from BMP', UI.Ctrl.i),
			tooltip('Export Font to BMP', UI.Ctrl.e),
			GAP,
			tooltip('Close', UI.Ctrl.w),
			SECTION,
			tooltip('Manage Settings', UI.Ctrl.m),
			SECTION,
			tooltip('Set as Default *.fnt Editor (Windows Only)'),
			tooltip('View Help', UI.Key.F1),
			tooltip('About PyFNT'),
			tooltip('Donate'),
			tooltip('Check for Updates'),
			SECTION,
			tooltip('Exit', UI.Shortcut.Exit),
		])

	def test_import_button_enabled_without_document(self) -> None:
		gui = self.open_pyfnt()
		buttons = toolbar_buttons(gui.toolbar)
		self.assertEqual(str(buttons[tooltip('Import Font from BMP', UI.Ctrl.i)].cget('state')), UI.NORMAL)
		self.assertEqual(str(buttons[tooltip('Export Font to BMP', UI.Ctrl.e)].cget('state')), UI.DISABLED)


class Test_PyFNT_shortcuts(PyFNTTestCase):
	def test_export_shortcut_runs_once_when_font_open(self) -> None:
		with mock.patch.object(PyFNT, 'exports') as exports:
			gui = self.with_new_font()
			self.show(gui)
			self.shortcut(gui, UI.Ctrl.e)
		exports.assert_called_once_with()

	def test_disabled_export_shortcut_does_nothing(self) -> None:
		with mock.patch.object(PyFNT, 'exports') as exports:
			gui = self.open_pyfnt()
			self.show(gui)
			self.shortcut(gui, UI.Ctrl.e)
		exports.assert_not_called()

	def test_import_shortcut_works_without_document(self) -> None:
		with mock.patch.object(PyFNT, 'imports') as imports:
			gui = self.open_pyfnt()
			self.show(gui)
			self.shortcut(gui, UI.Ctrl.i)
		imports.assert_called_once_with()

	def test_save_shortcut_runs_once(self) -> None:
		gui = self.with_new_font()
		self.show(gui)
		with mock.patch.object(gui, 'save') as save:
			self.shortcut(gui, UI.Ctrl.s)
		save.assert_called_once_with()
