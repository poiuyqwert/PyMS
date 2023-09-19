
from .Config import PyGRPConfig

from ..Utilities.SettingsUI.BaseSettingsDialog import BaseSettingsDialog
from ..Utilities.SettingsUI.ThemeSettingsTab import ThemeSettingsTab
from ..Utilities.UIKit import *

class SettingsDialog(BaseSettingsDialog[PyGRPConfig]):
	def widgetize(self) -> Misc | None:
		widget = super().widgetize()

		self.add_tab('Theme', ThemeSettingsTab(self.notebook, self.edited_state.sub_state(), self.config_.theme))

		return widget

	def setup_complete(self) -> None:
		self.config_.windows.settings.main.load(self)

	def dismiss(self) -> None:
		self.config_.windows.settings.main.save(self)
		super().dismiss()
