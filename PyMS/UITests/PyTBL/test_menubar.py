from .utils import PyTBLTestCase

from ...PyTBL.PyTBL import PyTBL
from ...Utilities import UIKit as UI

from unittest import mock

SEPARATOR = '----'

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

def submenu(gui: PyTBL, label: str) -> UI.Menu:
	return gui.nametowidget(gui.menu.entrycget(label, 'menu'))

GAP = '-'
SECTION = '='

# The toolbar's buttons as tooltips without their shortcut suffix, with gaps and sections marked
def toolbar_layout(gui: PyTBL) -> list[str]:
	layout: list[str] = []
	for row in gui.toolbar.winfo_children():
		for widget in row.winfo_children():
			tooltip = getattr(widget, '_tooltip_Tooltip', None)
			if tooltip is not None:
				text: str = tooltip.text
				if not text.endswith('(Windows Only)'):
					text = text.split(' (')[0]
				layout.append(text)
			else:
				layout.append(SECTION if int(widget.cget('width')) == UI.Toolbar.SECTION_SIZE else GAP)
	return layout


class Test_PyTBL_menubar(PyTBLTestCase):
	def test_menubar_top_level_labels(self) -> None:
		gui = self.make_pytbl()
		self.assertEqual(menu_labels(gui.menu), ['File', 'Edit', 'Strings', 'Settings', 'Help'])

	def test_menu_items_in_order(self) -> None:
		gui = self.make_pytbl()
		expected = {
			'File': ['New', 'Open...', 'Open Default TBL', SEPARATOR, 'Save', 'Save As...', SEPARATOR, 'Import Strings...', 'Export Strings...', SEPARATOR, 'Close', SEPARATOR, 'Exit'],
			'Edit': ['Find Strings...', 'Find Next', 'Go To...'],
			'Strings': ['Add String', 'Insert String', 'Remove String', SEPARATOR, 'Move String Up', 'Move String Down', SEPARATOR, 'Test String...'],
			'Settings': ['Manage Settings...', SEPARATOR, 'Set as Default *.tbl Editor (Windows Only)'],
			'Help': ['View Help', SEPARATOR, 'Donate...', 'About PyTBL'],
		}
		for label, items in expected.items():
			with self.subTest(menu=label):
				self.assertEqual(menu_labels(submenu(gui, label)), items)

	def test_toolbar_button_order(self) -> None:
		gui = self.make_pytbl()
		self.assertEqual(toolbar_layout(gui), [
			'New', 'Open', 'Open Default TBL', GAP,
			'Save', 'Save As', GAP,
			'Import Strings', 'Export Strings', GAP,
			'Close', SECTION,
			'Find Strings', GAP, 'Go To', SECTION,
			'Add String', 'Insert String', 'Remove String', GAP,
			'Move String Up', 'Move String Down', GAP,
			'Test String', SECTION,
			'Manage Settings', SECTION,
			'Set as Default *.tbl Editor (Windows Only)', 'View Help', 'About PyTBL', 'Donate', SECTION,
			'Exit',
		])

	def test_shortcut_triggers_action_once(self) -> None:
		with mock.patch.object(PyTBL, 'goto') as goto:
			gui = self.make_pytbl(['alpha'])
			self.show(gui)
			self.shortcut(gui, UI.Ctrl.g)
		goto.assert_called_once_with()

	def test_disabled_item_shortcut_does_nothing(self) -> None:
		with mock.patch.object(PyTBL, 'goto') as goto:
			gui = self.make_pytbl()
			self.show(gui)
			self.shortcut(gui, UI.Ctrl.g)
		goto.assert_not_called()

	def test_move_string_shortcut_moves_once(self) -> None:
		gui = self.make_pytbl(['alpha', 'beta', 'gamma'])
		self.show(gui)
		gui.listbox.select_clear(0, UI.END)
		gui.listbox.select_set(1)
		gui.action_states()
		self.shortcut(gui, UI.Shift.Down)
		assert gui.tbl is not None
		self.assertEqual(gui.tbl.strings, ['alpha', 'gamma', 'beta'])
		self.assertEqual(self.selected_index(gui), 2)

	# Insert has no key on macOS, so these use Remove String's Shift+Delete, which shares the same text box guard
	def test_remove_string_shortcut_ignored_in_text_box(self) -> None:
		gui = self.make_pytbl(['alpha', 'beta'])
		self.show(gui)
		gui.text.focus_force()
		self.pump(gui)
		gui.text.event_generate(UI.Shift.Delete.event())
		self.pump(gui)
		assert gui.tbl is not None
		self.assertEqual(len(gui.tbl.strings), 2)

	def test_remove_string_shortcut_outside_text_box(self) -> None:
		gui = self.make_pytbl(['alpha', 'beta'])
		self.show(gui)
		gui.listbox.listbox.focus_force()
		self.pump(gui)
		gui.listbox.listbox.event_generate(UI.Shift.Delete.event())
		self.pump(gui)
		assert gui.tbl is not None
		self.assertEqual(gui.tbl.strings, ['beta'])

	def test_find_next_opens_find_dialog_when_missing(self) -> None:
		gui = self.make_pytbl(['alpha'])
		self.assertIsNone(gui.findwindow)
		gui.find_next()
		self.pump(gui)
		self.assertIsNotNone(gui.findwindow)

	def test_find_next_shortcut_searches_with_existing_dialog(self) -> None:
		gui = self.make_pytbl(['alpha', 'beta'])
		gui.find()
		self.pump(gui)
		assert gui.findwindow is not None
		gui.findwindow.find.set('beta')
		gui.findwindow.ok()
		self.show(gui)
		self.shortcut(gui, UI.Key.F3)
		self.assertEqual(self.selected_index(gui), 1)
