
from .Config import PyTILEConfig

from ..Utilities.SettingsUI.BaseSettingsDialog import BaseSettingsDialog
from ..Utilities.SettingsUI.ThemeSettingsTab import ThemeSettingsTab
from ..Utilities.UIKit import *

class SettingsDialog(BaseSettingsDialog[PyTILEConfig]):
    def __init__(self, parent: Misc, config: PyTILEConfig):
        super().__init__(parent, config)

    def widgetize(self) -> Misc | None:
        widget = super().widgetize()

        self.add_tab('Theme', ThemeSettingsTab(self.notebook, self.edited_state.sub_state(), self.config_.theme))

        return widget

    def setup_complete(self) -> None:
        self.config_.windows.settings.main.load(self)

    def dismiss(self) -> None:
        self.config_.windows.settings.main.save(self)
        super().dismiss()
