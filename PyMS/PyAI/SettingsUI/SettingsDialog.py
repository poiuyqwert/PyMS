
from .FileSettingsTab import FileSettingsTab
from ..Config import PyAIConfig

from ...Utilities.SettingsUI.BaseSettingsDialog import BaseErrorableSettingsDialog, ErrorableSettingsDialogDelegate
from ...Utilities.SettingsUI.ThemeSettingsTab import ThemeSettingsTab
from ...Utilities.SettingsUI.MPQSettingsTab import MPQSettingsTab
from ...Utilities import UIKit as UI
from ...Utilities.PyMSError import PyMSError
from ...Utilities.MPQHandler import MPQHandler

class SettingsDialog(BaseErrorableSettingsDialog[PyAIConfig]):
	def __init__(self, parent: UI.Misc, *, config: PyAIConfig, delegate: ErrorableSettingsDialogDelegate, err: PyMSError | None, mpq_handler: MPQHandler):
		self.mpq_handler = mpq_handler
		super().__init__(parent, config, delegate, err)

	def widgetize(self) -> UI.Misc | None:
		widget = super().widgetize()

		self.add_tab('MPQ Settings', MPQSettingsTab(parent=self.notebook, edited_state=self.edited_state.sub_state(), mpq_hander=self.mpq_handler, mpqs_config=self.config_.settings.mpqs, mpqs_select_config=self.config_.settings.last_path.mpqs))
		self.add_tab('File Settings', FileSettingsTab(self.notebook, self.edited_state.sub_state(), self.config_, self.mpq_handler))
		self.add_tab('Theme', ThemeSettingsTab(self.notebook, self.edited_state.sub_state(), self.config_.theme))

		return widget

	def setup_complete(self) -> None:
		self.config_.windows.settings.main.load_size(self)
		super().setup_complete()

	def dismiss(self) -> None:
		self.config_.windows.settings.main.save_size(self)
		super().dismiss()
