
from ..Config import PyMODConfig

from ...Utilities.SettingsUI.BaseSettingsDialog import BaseSettingsDialog
from ...Utilities.SettingsUI.ThemeSettingsTab import ThemeSettingsTab
from ...Utilities.SettingsUI.MPQSettingsTab import MPQSettingsTab
from ...Utilities.MPQHandler import MPQHandler
from ...Utilities import UIKit as UI

class SettingsDialog(BaseSettingsDialog[PyMODConfig]):
	def __init__(self, parent: UI.Misc, config: PyMODConfig, mpq_handler: MPQHandler) -> None:
		self.mpq_handler = mpq_handler
		super().__init__(parent, config)

	def widgetize(self) -> UI.Misc | None:
		widget = super().widgetize()

		self.add_tab('MPQ Settings', MPQSettingsTab(parent=self.notebook, edited_state=self.edited_state.sub_state(), mpq_hander=self.mpq_handler, mpqs_config=self.config_.settings.mpqs, mpqs_select_config=self.config_.settings.last_path.mpqs))
		self.add_tab('Theme', ThemeSettingsTab(self.notebook, self.edited_state.sub_state(), self.config_.theme))

		return widget

	def setup_complete(self) -> None:
		self.config_.windows.settings.main.load_size(self)
		super().setup_complete()

	def dismiss(self) -> None:
		self.config_.windows.settings.main.save_size(self)
		super().dismiss()
