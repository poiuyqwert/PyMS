
from .Config import PyLOConfig

from ..Utilities.SettingsUI.BaseSettingsDialog import BaseSettingsDialog
from ..Utilities.SettingsUI.ThemeSettingsTab import ThemeSettingsTab
from ..Utilities.SettingsUI.MPQSettingsTab import MPQSettingsTab
from ..Utilities.UIKit import *
from ..Utilities.MPQHandler import MPQHandler

class SettingsDialog(BaseSettingsDialog[PyLOConfig]):
	def __init__(self, parent: Misc, config: PyLOConfig, mpq_handler: MPQHandler):
		self.mpq_handler = mpq_handler
		super().__init__(parent, config)

	def widgetize(self) -> Misc | None:
		widget = super().widgetize()

		self.add_tab('MPQ Settings', MPQSettingsTab(self.notebook, self.edited_state.sub_state(), self.mpq_handler, self.config_.settings.mpqs, self.config_.settings.last_path.mpqs))
		self.add_tab('Theme', ThemeSettingsTab(self.notebook, self.edited_state.sub_state(), self.config_.theme))

		return widget

	def setup_complete(self) -> None:
		self.config_.windows.settings.main.load(self)

	def dismiss(self) -> None:
		self.config_.windows.settings.main.save(self)
		super().dismiss()
