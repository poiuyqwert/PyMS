
from .Config import PyJSONConfig

from ..Utilities.SettingsUI.BaseSettingsDialog import BaseSettingsDialog
from ..Utilities.SettingsUI.ThemeSettingsTab import ThemeSettingsTab
from ..Utilities.SettingsUI.MPQSettingsTab import MPQSettingsTab
from ..Utilities.UIKit import *
from ..Utilities.MPQHandler import MPQHandler

class SettingsDialog(BaseSettingsDialog[PyJSONConfig]):
	def __init__(self, parent: Misc, config: PyJSONConfig):
		super().__init__(parent, config)

	def widgetize(self) -> Misc | None:
		widget = super().widgetize()

		self.add_tab('Theme', ThemeSettingsTab(self.notebook, self.edited_state.sub_state(), self.config_.theme))

		return widget

	def setup_complete(self) -> None:
		self.config_.windows.settings.main.load_size(self)

	def dismiss(self) -> None:
		self.config_.windows.settings.main.save_size(self)
		super().dismiss()
