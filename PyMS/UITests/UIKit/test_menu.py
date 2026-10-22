from ..harness import UITestCase

from ...Utilities import UIKit as UI


class _Host(UI.MainWindow):
	def __init__(self) -> None:
		UI.MainWindow.__init__(self)
		self.calls: list[str] = []
		self.flag = UI.BooleanVar(value=False)
		self.choice = UI.StringVar(value='a')
		self.menu = UI.Menu(self)
		self.config(menu=self.menu)
		self.file_menu = self.menu.add_cascade('File')
		self.save_item = self.file_menu.add_command('Save', lambda: self.calls.append('save'), UI.Ctrl.s, enabled=False, tags='file_open')
		self.sub_menu = self.file_menu.add_cascade('Recent')
		self.sub_menu.add_command('Reopen', lambda: self.calls.append('reopen'), UI.Ctrl.r)
		self.view_menu = self.menu.add_cascade('View')
		self.view_menu.add_checkbutton('Flag', self.flag, shortcut=UI.Ctrl.g)
		self.view_menu.add_radiobutton('Choice B', self.choice, 'b', shortcut=UI.Ctrl.b)


class Test_Menu(UITestCase):
	def test_cascade_shortcuts_are_bound_on_the_window(self) -> None:
		# Items in a menubar cascade must respond to their shortcut while the window has focus,
		# so the binding has to live on the window rather than on the menu widgets.
		window = self.make_window(_Host)
		self.show(window)
		window.menu.tag_enabled('file_open', True)
		self.shortcut(window, UI.Ctrl.s)
		self.assertEqual(window.calls, ['save'])

	def test_nested_cascade_shortcuts_are_bound_on_the_window(self) -> None:
		window = self.make_window(_Host)
		self.show(window)
		self.shortcut(window, UI.Ctrl.r)
		self.assertEqual(window.calls, ['reopen'])

	def test_disabled_item_shortcut_does_nothing(self) -> None:
		window = self.make_window(_Host)
		self.show(window)
		self.shortcut(window, UI.Ctrl.s)
		self.assertEqual(window.calls, [])

	def test_cascade_check_and_radio_shortcuts_are_bound_on_the_window(self) -> None:
		window = self.make_window(_Host)
		self.show(window)
		self.shortcut(window, UI.Ctrl.g)
		self.shortcut(window, UI.Ctrl.b)
		self.assertTrue(window.flag.get())
		self.assertEqual(window.choice.get(), 'b')
