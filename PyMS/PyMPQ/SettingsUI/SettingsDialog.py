
from .GeneralSettingsTab import GeneralSettingsTab
from .ListfileSettingsTab import ListfileSettingsTab
from .CompressionSettingsTab import CompressionSettingsTab

from ..Config import PyMPQConfig

from ...Utilities.SettingsUI.BaseSettingsDialog import BaseSettingsDialog
from ...Utilities.SettingsUI.ThemeSettingsTab import ThemeSettingsTab
from ...Utilities.UIKit import *

class SettingsDialog(BaseSettingsDialog[PyMPQConfig]):
    def widgetize(self) -> Misc | None:
        widget = super().widgetize()

        self.add_tab('General', GeneralSettingsTab(self.notebook, self.edited_state.sub_state(), self.config_))
        self.add_tab('List Files', ListfileSettingsTab(self.notebook, self.edited_state.sub_state(), self.config_))
        self.add_tab('Compression Auto-Selection', CompressionSettingsTab(self.notebook, self.edited_state.sub_state(), self.config_.settings.autocompression))
        self.add_tab('Theme', ThemeSettingsTab(self.notebook, self.edited_state.sub_state(), self.config_.theme))

        return widget

    def setup_complete(self) -> None:
        self.config_.windows.settings.main.load_size(self)
        super().setup_complete()

    def dismiss(self) -> None:
        self.config_.windows.settings.main.save_size(self)
        super().dismiss()
