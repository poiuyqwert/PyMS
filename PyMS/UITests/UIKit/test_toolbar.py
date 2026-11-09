from ..harness import UITestCase

from ...Utilities import UIKit as UI
from ...Utilities import Assets


class _Host(UI.MainWindow):
	def __init__(self) -> None:
		UI.MainWindow.__init__(self)
		self.calls: list[str] = []
		self.flag = UI.BooleanVar(value=False)
		self.choice = UI.StringVar(value='a')

		self.text = UI.Text(self, width=20, height=2)
		self.text.insert(UI.END, 'abc')
		self.text_toolbar = UI.Toolbar(self, bind_target=self.text)
		self.test_button = self.text_toolbar.add_button(Assets.get_image('test'), lambda: self.calls.append('test'), 'Test', UI.Ctrl.t)
		self.text_toolbar.add_checkbutton(Assets.get_image('test'), self.flag, 'Flag', UI.Ctrl.g)
		self.text_toolbar.add_radiobutton(Assets.get_image('test'), self.choice, 'b', 'Choice B', UI.Ctrl.b)
		self.text_toolbar.pack(side=UI.TOP, fill=UI.X)

		self.window_toolbar = UI.Toolbar(self)
		self.window_toolbar.add_button(Assets.get_image('save'), lambda: self.calls.append('save'), 'Save', UI.Ctrl.s)
		self.window_toolbar.pack(side=UI.TOP, fill=UI.X)

		self.text.pack(fill=UI.BOTH, expand=1)


class Test_Toolbar(UITestCase):
	def focus_text(self, window: _Host) -> None:
		self.show(window)
		window.text.focus_force()
		self.pump(window)

	def text_content(self, window: _Host) -> str:
		return window.text.get('1.0', UI.END + '-1c')

	def test_shortcuts_are_bound_on_the_bind_target(self) -> None:
		window = self.make_window(_Host)
		for shortcut in (UI.Ctrl.t, UI.Ctrl.g, UI.Ctrl.b):
			self.assertTrue(window.text.bind(shortcut()))
			self.assertFalse(window.bind(shortcut()))

	def test_shortcuts_default_to_the_master(self) -> None:
		window = self.make_window(_Host)
		self.assertTrue(window.bind(UI.Ctrl.s()))
		self.assertFalse(window.text.bind(UI.Ctrl.s()))

	def test_bind_target_shortcuts_trigger_while_the_target_has_focus(self) -> None:
		window = self.make_window(_Host)
		self.focus_text(window)
		self.shortcut(window.text, UI.Ctrl.t)
		self.shortcut(window.text, UI.Ctrl.g)
		self.shortcut(window.text, UI.Ctrl.b)
		self.assertEqual(window.calls, ['test'])
		self.assertTrue(window.flag.get())
		self.assertEqual(window.choice.get(), 'b')

	def test_bind_target_shortcuts_dont_run_the_target_class_bindings(self) -> None:
		# Ctrl+T transposes characters in a Text
		window = self.make_window(_Host)
		window.text.mark_set(UI.INSERT, '1.1')
		self.focus_text(window)
		self.shortcut(window.text, UI.Ctrl.t)
		self.assertEqual(window.calls, ['test'])
		self.assertEqual(self.text_content(window), 'abc')

	def test_disabled_bind_target_shortcut_doesnt_run_the_target_class_bindings(self) -> None:
		window = self.make_window(_Host)
		window.test_button['state'] = UI.DISABLED
		window.text.mark_set(UI.INSERT, '1.1')
		self.focus_text(window)
		self.shortcut(window.text, UI.Ctrl.t)
		self.assertEqual(window.calls, [])
		self.assertEqual(self.text_content(window), 'abc')

	def test_window_shortcuts_still_trigger_from_the_bind_target(self) -> None:
		window = self.make_window(_Host)
		self.focus_text(window)
		self.shortcut(window.text, UI.Ctrl.s)
		self.assertEqual(window.calls, ['save'])
