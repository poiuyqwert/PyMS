
from ..Config import PyTBLConfig

from ...Utilities.UIKit import *
from ...Utilities.SettingsUI.SettingsTab import SettingsTab
from ...Utilities.SettingsUI.FileSettingView import FileSettingView
from ...Utilities.EditedState import EditedState
from ...Utilities.MPQHandler import MPQHandler

class PreviewSettingsTab(SettingsTab):
	def __init__(self, notebook: Notebook, edited_state: EditedState, config: PyTBLConfig, mpq_handler: MPQHandler):
		super().__init__(notebook)

		tfontgam = FileSettingView(self, edited_state, 'tfontgam.pcx', 'The special palette which holds text colors.', config.settings.files.tfontgam, mpq_handler, config.settings.mpq_select_history, config.windows.settings.mpq_select)
		tfontgam.pack(side=TOP, fill=X)
		self.register_settings_view(tfontgam)

		font8 = FileSettingView(self, edited_state, 'font8.fnt', 'The font used to preview hotkeys', config.settings.files.font8, mpq_handler, config.settings.mpq_select_history, config.windows.settings.mpq_select)
		font8.pack(side=TOP, fill=X)
		self.register_settings_view(font8)

		font10 = FileSettingView(self, edited_state, 'font10.fnt', 'The font used to preview strings other than hotkeys', config.settings.files.font10, mpq_handler, config.settings.mpq_select_history, config.windows.settings.mpq_select)
		font10.pack(side=TOP, fill=X)
		self.register_settings_view(font10)

		icons = FileSettingView(self, edited_state, 'icons.grp', 'The icons used to preview hotkeys', config.settings.files.icons, mpq_handler, config.settings.mpq_select_history, config.windows.settings.mpq_select)
		icons.pack(side=TOP, fill=X)
		self.register_settings_view(icons)

		unit_pal = FileSettingView(self, edited_state, 'Unit Palette', 'The palette used to display icons.grp', config.settings.files.unit_pal, mpq_handler, config.settings.mpq_select_history, config.windows.settings.mpq_select)
		unit_pal.pack(side=TOP, fill=X)
		self.register_settings_view(unit_pal)
