from .utils import PyJSONTestCase, OBJECTS

from ...Utilities import UIKit as UI

from unittest import mock

SEPARATOR = '----'
GAP = 'gap'
SECTION = 'section'

SAVE = 'PyMS.PyJSON.PyJSON.PyJSON.save'
SETTINGS = 'PyMS.PyJSON.PyJSON.PyJSON.settings'


def menu_labels(menu: UI.Menu) -> list[str]:
	# The entries of `menu` in order, with separators as `SEPARATOR` (tearoff entries skipped).
	labels: list[str] = []
	end = menu.index(UI.END)
	if end is None:
		return labels
	for index in range(end + 1):
		entry_type = menu.type(index)
		if entry_type == 'tearoff':
			continue
		if entry_type == 'separator':
			labels.append(SEPARATOR)
		else:
			labels.append(str(menu.entrycget(index, 'label')))
	return labels


def cascade(menu: UI.Menu, label: str) -> UI.Menu:
	submenu = menu.nametowidget(menu.entrycget(label, 'menu'))
	assert isinstance(submenu, UI.Menu)
	return submenu


def toolbar_layout(toolbar: UI.Toolbar) -> list[str]:
	# The toolbar's buttons as their tooltips, with spacers as `GAP`/`SECTION`, in packing order.
	layout: list[str] = []
	for row in toolbar.pack_slaves():
		for widget in row.pack_slaves():
			if isinstance(widget, UI.Button):
				layout.append(getattr(widget, '_tooltip_Tooltip').text)
			else:
				width = int(widget.cget('width'))
				layout.append(GAP if width == UI.Toolbar.GAP_SIZE else SECTION)
	return layout


class Test_PyJSON_menubar(PyJSONTestCase):
	def test_top_level_menus(self) -> None:
		gui = self.open_pyjson()
		self.assertEqual(menu_labels(gui.menu), ['File', 'Objects', 'Settings', 'Help'])

	def test_file_menu(self) -> None:
		gui = self.open_pyjson()
		self.assertEqual(menu_labels(cascade(gui.menu, 'File')), [
			'New', 'Open...',
			SEPARATOR,
			'Save', 'Save As...',
			SEPARATOR,
			'Close',
			SEPARATOR,
			'Check for Updates...',
			SEPARATOR,
			'Exit',
		])

	def test_objects_menu(self) -> None:
		gui = self.open_pyjson()
		self.assertEqual(menu_labels(cascade(gui.menu, 'Objects')), ['Add Object', 'Insert Object', 'Remove Object'])

	def test_settings_menu(self) -> None:
		gui = self.open_pyjson()
		self.assertEqual(menu_labels(cascade(gui.menu, 'Settings')), [
			'Manage Settings...',
			SEPARATOR,
			'Set as Default *.json Editor (Windows Only)',
		])

	def test_help_menu(self) -> None:
		gui = self.open_pyjson()
		self.assertEqual(menu_labels(cascade(gui.menu, 'Help')), ['View Help', SEPARATOR, 'Donate...', 'About PyJSON'])

	def test_file_menu_items_follow_file_open_state(self) -> None:
		gui = self.open_pyjson()
		file_menu = cascade(gui.menu, 'File')
		gui.close()
		self.pump(gui)
		self.assertEqual(str(file_menu.entrycget('Save', 'state')), UI.DISABLED)
		gui.data_source.set_data([{'id': 'only'}])
		gui.action_states()
		self.assertEqual(str(file_menu.entrycget('Save', 'state')), UI.NORMAL)


class Test_PyJSON_toolbar(PyJSONTestCase):
	def test_button_order(self) -> None:
		gui = self.open_pyjson()
		self.assertEqual(toolbar_layout(gui.toolbar), [
			f'New ({UI.Ctrl.n.description()})',
			f'Open ({UI.Ctrl.o.description()})',
			GAP,
			f'Save ({UI.Ctrl.s.description()})',
			f'Save As ({UI.Ctrl.Alt.a.description()})',
			GAP,
			f'Close ({UI.Ctrl.w.description()})',
			SECTION,
			f'Add Object ({UI.Key.Insert.description()})',
			f'Insert Object ({UI.Shift.Insert.description()})',
			f'Remove Object ({UI.Shift.Delete.description()})',
			SECTION,
			f'Manage Settings ({UI.Ctrl.m.description()})',
			SECTION,
			'Set as Default *.json Editor (Windows Only)',
			f'View Help ({UI.Key.F1.description()})',
			'About PyJSON',
			'Donate',
			'Check for Updates',
			SECTION,
			f'Exit ({UI.Shortcut.Exit.description()})',
		])


class Test_PyJSON_shortcuts(PyJSONTestCase):
	def test_shortcut_triggers_menu_action_once(self) -> None:
		settings = mock.MagicMock()
		gui = self.open_pyjson(extra_patches={SETTINGS: {'new': settings}})
		self.show(gui)
		self.shortcut(gui, UI.Ctrl.m)
		settings.assert_called_once_with()

	def test_shortcut_is_bound_by_menubar_item(self) -> None:
		# The toolbar button stays enabled; only the menu item is disabled. If the shortcut
		# were bound by the toolbar it would still fire.
		settings = mock.MagicMock()
		gui = self.open_pyjson(extra_patches={SETTINGS: {'new': settings}})
		cascade(gui.menu, 'Settings').entryconfig('Manage Settings...', state=UI.DISABLED)
		self.show(gui)
		self.shortcut(gui, UI.Ctrl.m)
		settings.assert_not_called()

	def test_enabled_item_shortcut_triggers_once(self) -> None:
		save = mock.MagicMock()
		gui = self.open_pyjson(extra_patches={SAVE: {'new': save}})
		gui.action_states()
		self.show(gui)
		self.shortcut(gui, UI.Ctrl.s)
		save.assert_called_once_with()

	def test_disabled_item_shortcut_does_nothing(self) -> None:
		save = mock.MagicMock()
		gui = self.open_pyjson(extra_patches={SAVE: {'new': save}})
		self.show(gui)
		self.assertEqual(str(cascade(gui.menu, 'File').entrycget('Save', 'state')), UI.DISABLED)
		self.shortcut(gui, UI.Ctrl.s)
		save.assert_not_called()


class Test_PyJSON_startup(PyJSONTestCase):
	def test_window_builds_with_title_and_objects_listed(self) -> None:
		gui = self.open_pyjson()
		self.assertIn('PyJSON', gui.title())
		self.assertEqual(len(gui.tree.treeview.get_children()), len(OBJECTS))
