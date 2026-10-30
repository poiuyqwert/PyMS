from .utils import PyLOTestCase

from ...PyLO.PyLO import PyLO
from ...Utilities import UIKit as UI

from unittest import mock


def menu_entries(menu: UI.Menu) -> list[str]:
	# Separators are reported as '-' so their positions are checked along with the labels.
	entries: list[str] = []
	end = menu.index(UI.END)
	if end is None:
		return entries
	for index in range(end + 1):
		if menu.type(index) == 'separator':
			entries.append('-')
		else:
			entries.append(str(menu.entrycget(index, 'label')))
	return entries


def cascade(gui: PyLO, label: str) -> UI.Menu:
	menu = gui.menu.nametowidget(gui.menu.entrycget(label, 'menu'))
	assert isinstance(menu, UI.Menu)
	return menu


def toolbar_layout(gui: PyLO) -> list[str]:
	# Buttons are reported by tooltip; spacers as '|' (gap) or '||' (section).
	layout: list[str] = []
	row = gui.toolbar.winfo_children()[0]
	for child in row.winfo_children():
		if isinstance(child, UI.Button):
			layout.append(getattr(child, '_tooltip_Tooltip').text)
		else:
			layout.append('||' if int(child['width']) == UI.Toolbar.SECTION_SIZE else '|')
	return layout


class Test_PyLO_menubar(PyLOTestCase):
	def test_top_level_menus(self) -> None:
		gui = self.make_pylo()
		self.assertEqual(menu_entries(gui.menu), ['File', 'Edit', 'View', 'Settings', 'Help'])

	def test_menu_items(self) -> None:
		gui = self.make_pylo()
		self.assertEqual(menu_entries(cascade(gui, 'File')), [
			'New', 'Open...', '-',
			'Save', 'Save As...', '-',
			'Import Text...', 'Export Text...', '-',
			'Close', '-',
			'Check for Updates...',
			'-',
			'Exit',
		])
		self.assertEqual(menu_entries(cascade(gui, 'Edit')), ['Find/Replace...', 'Find Next', '-', 'Test Code'])
		self.assertEqual(menu_entries(cascade(gui, 'View')), ['Use Base GRP', 'Use Overlay GRP'])
		self.assertEqual(menu_entries(cascade(gui, 'Settings')), [
			'Manage Settings...', 'Syntax Highlighting...', '-',
			'Set as Default *.lo? Editor (Windows Only)',
		])
		self.assertEqual(menu_entries(cascade(gui, 'Help')), ['View Help', '-', 'Donate...', 'About PyLO'])

	def test_file_open_items_follow_file_state(self) -> None:
		gui = self.make_pylo()
		gui.action_states()
		edit_menu = cascade(gui, 'Edit')
		self.assertEqual(str(edit_menu.entrycget('Test Code', 'state')), UI.DISABLED)
		gui.new()
		self.assertEqual(str(edit_menu.entrycget('Test Code', 'state')), UI.NORMAL)
		self.assertEqual(str(cascade(gui, 'File').entrycget('Save', 'state')), UI.NORMAL)

	def test_view_checks_share_the_preview_checkbox_variables(self) -> None:
		# The menu items share the checkboxes' commands, which load the GRP; stub them so no file is read.
		with mock.patch.object(PyLO, 'updateusebase') as updateusebase:
			gui = self.make_pylo()
			view_menu = cascade(gui, 'View')
			self.assertEqual(str(view_menu.entrycget('Use Base GRP', 'variable')), str(gui.usebasegrp))
			self.assertEqual(str(view_menu.entrycget('Use Overlay GRP', 'variable')), str(gui.useoverlaygrp))
			gui.usebasegrp.set(False)
			self.invoke_menu(view_menu, 0)
		self.assertTrue(gui.usebasegrp.get())
		updateusebase.assert_called_once()


class Test_PyLO_toolbar(PyLOTestCase):
	def test_toolbar_layout(self) -> None:
		gui = self.make_pylo()
		def key(pattern: UI.EventPattern) -> str:
			return f' ({pattern.description()})'
		self.assertEqual(toolbar_layout(gui), [
			'New' + key(UI.Ctrl.n), 'Open' + key(UI.Ctrl.o), '|',
			'Save' + key(UI.Ctrl.s), 'Save As' + key(UI.Ctrl.Alt.a), '|',
			'Import Text' + key(UI.Ctrl.i), 'Export Text' + key(UI.Ctrl.e), '|',
			'Close' + key(UI.Ctrl.w), '||',
			'Find/Replace' + key(UI.Ctrl.f), '|', 'Test Code' + key(UI.Ctrl.t), '||',
			'Manage Settings' + key(UI.Ctrl.m), 'Syntax Highlighting' + key(UI.Ctrl.Alt.c), '||',
			'Set as Default *.lo? Editor (Windows Only)', 'View Help' + key(UI.Key.F1), 'About PyLO', 'Donate', 'Check for Updates', '||',
			'Exit' + key(UI.Shortcut.Exit),
		])


class Test_PyLO_shortcuts(PyLOTestCase):
	def test_shortcut_runs_its_action_once(self) -> None:
		with mock.patch.object(PyLO, 'test') as test:
			gui = self.make_pylo()
			gui.new()
			self.show(gui)
			self.shortcut(gui, UI.Ctrl.t)
		test.assert_called_once()

	def test_disabled_item_shortcut_does_nothing(self) -> None:
		with mock.patch.object(PyLO, 'test') as test:
			gui = self.make_pylo()
			gui.action_states()
			self.show(gui)
			self.shortcut(gui, UI.Ctrl.t)
		test.assert_not_called()

	def test_find_next_creates_the_find_dialog_when_missing(self) -> None:
		gui = self.make_pylo()
		gui.new()
		self.show(gui)
		self.assertIsNone(gui.findwindow)
		with mock.patch('PyMS.PyLO.PyLO.FindReplaceDialog') as dialog:
			self.shortcut(gui, UI.Key.F3)
		dialog.assert_called_once()
		dialog.return_value.findnext.assert_not_called()
		with mock.patch.object(gui, 'findwindow') as findwindow:
			self.shortcut(gui, UI.Key.F3)
		findwindow.findnext.assert_called_once()
