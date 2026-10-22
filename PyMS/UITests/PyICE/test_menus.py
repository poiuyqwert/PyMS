from .utils import PyICETestCase

from ...Utilities import UIKit as UI

from unittest import mock
from types import SimpleNamespace

FIND = 'PyMS.PyICE.PyICE.PyICE.find'
CODEEDIT = 'PyMS.PyICE.PyICE.PyICE.codeedit'

SEPARATOR = '----'
GAP = '<gap>'
SECTION = '<section>'


def menu_labels(menu: UI.Menu) -> list[str]:
	end = menu.index(UI.END)
	if end is None:
		return []
	labels: list[str] = []
	for index in range(end + 1):
		if menu.type(index) == 'separator':
			labels.append(SEPARATOR)
		else:
			labels.append(menu.entrycget(index, 'label'))
	return labels


def submenu(menu: UI.Menu, label: str) -> UI.Menu:
	end = menu.index(UI.END)
	assert end is not None
	for index in range(end + 1):
		if menu.type(index) == 'cascade' and menu.entrycget(index, 'label') == label:
			widget = menu.nametowidget(menu.entrycget(index, 'menu'))
			assert isinstance(widget, UI.Menu)
			return widget
	raise AssertionError(f'No cascade named {label!r}')


def toolbar_layout(toolbar: UI.Toolbar) -> list[str]:
	layout: list[str] = []
	for row in toolbar.pack_slaves():
		for widget in row.pack_slaves():
			tooltip = getattr(widget, '_tooltip_Tooltip', None)
			if tooltip is not None:
				layout.append(tooltip.text)
			elif int(widget.cget('width')) == UI.Toolbar.SECTION_SIZE:
				layout.append(SECTION)
			else:
				layout.append(GAP)
	return layout


class Test_Menubar(PyICETestCase):
	def test_top_level_menus(self) -> None:
		gui = self.make_pyice()
		self.assertEqual(menu_labels(gui.menu), ['File', 'Edit', 'Entries', 'Settings', 'Help'])

	def test_menu_items(self) -> None:
		gui = self.make_pyice()
		self.assertEqual(menu_labels(submenu(gui.menu, 'File')), [
			'New', 'Open...', 'Open Default Scripts',
			SEPARATOR,
			'Save', 'Save As...',
			SEPARATOR,
			'Close',
			SEPARATOR,
			'Exit',
		])
		self.assertEqual(menu_labels(submenu(gui.menu, 'Edit')), [
			'Select All',
			SEPARATOR,
			'Find Entries...',
		])
		self.assertEqual(menu_labels(submenu(gui.menu, 'Entries')), [
			'Edit IScript Entries...',
			SEPARATOR,
			'Import Entries...', 'Import a List of Files...', 'Export Entries...',
		])
		self.assertEqual(menu_labels(submenu(gui.menu, 'Settings')), [
			'Manage Settings...',
			SEPARATOR,
			'Set as Default *.bin Editor (Windows Only)',
		])
		self.assertEqual(menu_labels(submenu(gui.menu, 'Help')), [
			'View Help',
			SEPARATOR,
			'Donate...', 'About PyICE',
		])

	def test_file_open_items_follow_file_state(self) -> None:
		gui = self.make_pyice()
		entries = submenu(gui.menu, 'Entries')
		self.assertEqual(entries.entrycget('Edit IScript Entries...', 'state'), UI.DISABLED)
		gui.new()
		self.pump(gui)
		self.assertEqual(entries.entrycget('Edit IScript Entries...', 'state'), UI.NORMAL)
		# Export needs a selection, not just an open file
		self.assertEqual(entries.entrycget('Export Entries...', 'state'), UI.DISABLED)


class Test_Toolbar(PyICETestCase):
	def test_button_order(self) -> None:
		gui = self.make_pyice()
		self.assertEqual(toolbar_layout(gui.toolbar), [
			f'New ({UI.Ctrl.n.description()})',
			f'Open ({UI.Ctrl.o.description()})',
			f'Open Default Scripts ({UI.Ctrl.d.description()})',
			GAP,
			f'Save ({UI.Ctrl.s.description()})',
			f'Save As ({UI.Ctrl.Alt.a.description()})',
			GAP,
			f'Close ({UI.Ctrl.w.description()})',
			SECTION,
			f'Find Entries ({UI.Ctrl.f.description()})',
			SECTION,
			f'Edit IScript Entries ({UI.Ctrl.e.description()})',
			GAP,
			f'Import Entries ({UI.Ctrl.Alt.i.description()})',
			f'Import a List of Files ({UI.Ctrl.l.description()})',
			f'Export Entries ({UI.Ctrl.Alt.e.description()})',
			SECTION,
			f'Manage Settings ({UI.Ctrl.m.description()})',
			SECTION,
			'Set as Default *.bin Editor (Windows Only)',
			f'View Help ({UI.Key.F1.description()})',
			'About PyICE',
			'Donate',
			SECTION,
			f'Exit ({UI.Shortcut.Exit.description()})',
		])


class Test_Shortcuts(PyICETestCase):
	def test_shortcut_triggers_action_once(self) -> None:
		find = mock.MagicMock()
		gui = self.make_pyice(extra_patches={FIND: {'new': find}})
		gui.new()
		self.show(gui)
		self.shortcut(gui, UI.Ctrl.f)
		find.assert_called_once_with()

	def test_disabled_item_shortcut_does_nothing(self) -> None:
		codeedit = mock.MagicMock()
		gui = self.make_pyice(extra_patches={CODEEDIT: {'new': codeedit}})
		self.show(gui)
		self.shortcut(gui, UI.Ctrl.e)
		codeedit.assert_not_called()

	def test_select_all_selects_every_iscript_entry(self) -> None:
		gui = self.make_pyice()
		gui.new()
		self.show(gui)
		scripts = [SimpleNamespace(id=iscript_id) for iscript_id in (0, 1, 2)]
		with mock.patch.object(gui, '_sorted_scripts', return_value=scripts):
			gui.update_iscrips_list()
			self.shortcut(gui, UI.Ctrl.a)
			self.assertEqual(tuple(gui.iscriptlist.curselection()), (0, 1, 2))
			# Selecting entries enables the selection-gated menu item
			self.assertEqual(submenu(gui.menu, 'Entries').entrycget('Export Entries...', 'state'), UI.NORMAL)
