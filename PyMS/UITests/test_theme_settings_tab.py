
from .harness import UITestCase

from ..Utilities import UIKit as UI
from ..Utilities import Config
from ..Utilities.EditedState import EditedState
from ..Utilities.SettingsUI.ThemeSettingsTab import ThemeSettingsTab
from ..Utilities.PyMSConfig import PYMS_CONFIG


class TestThemeSettingsTab(UITestCase):
	# `ThemeSettingsTab` saves to two places depending on the 'Default' checkbox:
	# with it checked the selection is the global default (and the per-program
	# override is cleared); unchecked, the selection is the per-program override.
	# `check_edited()` must compare against whichever target a save would touch.

	def make_tab(self, *, setting_value: str | None, default_value: str | None) -> tuple[ThemeSettingsTab, EditedState]:
		# Build a real tab inside a throwaway window. A single root per test is
		# safe; the macOS segfault only comes from extra throwaway roots.
		window = self.make_window(UI.MainWindow)
		notebook = UI.Notebook(window)
		notebook.pack()
		setting = Config.String()
		setting.value = setting_value
		edited_state = EditedState()
		# `current_default()` reads the live global config; stub its value so the
		# test controls the "already saved" global default deterministically.
		self.addCleanup(setattr, PYMS_CONFIG.theme, 'value', PYMS_CONFIG.theme.value)
		PYMS_CONFIG.theme.value = default_value
		tab = ThemeSettingsTab(notebook, edited_state, setting)
		self.pump(window)
		return tab, edited_state

	def select(self, tab: ThemeSettingsTab, theme: str | None) -> None:
		index = tab.theme_index(theme)
		tab.listbox.select_clear(0, UI.END)
		tab.listbox.select_set(index)
		tab.selection_updated()

	def test_switch_global_default_back_to_none_is_edited(self) -> None:
		# Reproduces the report: a prior save set the global default to 'Dark' and
		# cleared the per-program override, so the tab opens with 'Default' checked
		# and 'Dark' selected. Selecting 'None' would save a different global
		# default, so it must register as edited (OK button enabled).
		tab, edited_state = self.make_tab(setting_value=None, default_value='Dark')
		self.assertTrue(tab.default.get())
		self.assertFalse(edited_state.is_edited)

		self.select(tab, None)
		self.assertTrue(edited_state.is_edited)

	def test_no_change_is_not_edited(self) -> None:
		tab, edited_state = self.make_tab(setting_value=None, default_value='Dark')
		self.select(tab, 'Dark')
		self.assertFalse(edited_state.is_edited)

	def test_changing_per_program_override_is_edited(self) -> None:
		tab, edited_state = self.make_tab(setting_value=None, default_value=None)
		tab.default.set(False)
		self.select(tab, 'Dark')
		self.assertTrue(edited_state.is_edited)
