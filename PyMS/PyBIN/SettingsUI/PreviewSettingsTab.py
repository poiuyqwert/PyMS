
from ..Config import PyBINConfig

from ...Utilities.UIKit import *
from ...Utilities.SettingsUI.SettingsTab import SettingsTab
from ...Utilities.SettingsUI.FileSettingView import FileSettingView
from ...Utilities.EditedState import EditedState
from ...Utilities.MPQHandler import MPQHandler

class PreviewSettingsTab(SettingsTab):
	def __init__(self, notebook: Notebook, edited_state: EditedState, config: PyBINConfig, mpq_handler: MPQHandler):
		super().__init__(notebook)

		tfontgam = FileSettingView(self, edited_state, 'tfontgam.pcx', 'The special palette which holds text colors.', config.settings.files.tfontgam, mpq_handler, config.settings.mpq_select_history, config.windows.settings.mpq_select)
		tfontgam.pack(side=TOP, fill=X)
		self.register_settings_view(tfontgam)

		font10 = FileSettingView(self, edited_state, 'font10.fnt', 'The 10 point font used to preview strings', config.settings.files.font10, mpq_handler, config.settings.mpq_select_history, config.windows.settings.mpq_select)
		font10.pack(side=TOP, fill=X)
		self.register_settings_view(font10)

		font14 = FileSettingView(self, edited_state, 'font14.fnt', 'The 14 point font used to preview strings', config.settings.files.font14, mpq_handler, config.settings.mpq_select_history, config.windows.settings.mpq_select)
		font14.pack(side=TOP, fill=X)
		self.register_settings_view(font14)

		font16 = FileSettingView(self, edited_state, 'font16.fnt', 'The 16 point font used to preview strings', config.settings.files.font16, mpq_handler, config.settings.mpq_select_history, config.windows.settings.mpq_select)
		font16.pack(side=TOP, fill=X)
		self.register_settings_view(font16)

		font16x = FileSettingView(self, edited_state, 'font16x.fnt', 'The 16x point font used to preview strings', config.settings.files.font16x, mpq_handler, config.settings.mpq_select_history, config.windows.settings.mpq_select)
		font16x.pack(side=TOP, fill=X)
		self.register_settings_view(font16x)
