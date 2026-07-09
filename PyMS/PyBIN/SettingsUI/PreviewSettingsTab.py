
from ..Config import PyBINConfig

from ...Utilities import UIKit as UI
from ...Utilities.SettingsUI.SettingsTab import SettingsTab
from ...Utilities.SettingsUI.FileSettingView import FileSettingView
from ...Utilities.EditedState import EditedState
from ...Utilities.MPQHandler import MPQHandler

class PreviewSettingsTab(SettingsTab):
	def __init__(self, notebook: UI.Notebook, edited_state: EditedState, config: PyBINConfig, mpq_handler: MPQHandler):
		super().__init__(notebook)

		tfontgam = FileSettingView(parent=self, edited_state=edited_state, name='tfontgam.pcx', description='The special palette which holds text colors.', setting=config.settings.files.tfontgam, mpq_handler=mpq_handler, mpq_history_config=config.settings.mpq_select_history, mpq_window_geometry_config=config.windows.settings.mpq_select)
		tfontgam.pack(side=UI.TOP, fill=UI.X)
		self.register_settings_view(tfontgam)

		font10 = FileSettingView(parent=self, edited_state=edited_state, name='font10.fnt', description='The 10 point font used to preview strings', setting=config.settings.files.font10, mpq_handler=mpq_handler, mpq_history_config=config.settings.mpq_select_history, mpq_window_geometry_config=config.windows.settings.mpq_select)
		font10.pack(side=UI.TOP, fill=UI.X)
		self.register_settings_view(font10)

		font14 = FileSettingView(parent=self, edited_state=edited_state, name='font14.fnt', description='The 14 point font used to preview strings', setting=config.settings.files.font14, mpq_handler=mpq_handler, mpq_history_config=config.settings.mpq_select_history, mpq_window_geometry_config=config.windows.settings.mpq_select)
		font14.pack(side=UI.TOP, fill=UI.X)
		self.register_settings_view(font14)

		font16 = FileSettingView(parent=self, edited_state=edited_state, name='font16.fnt', description='The 16 point font used to preview strings', setting=config.settings.files.font16, mpq_handler=mpq_handler, mpq_history_config=config.settings.mpq_select_history, mpq_window_geometry_config=config.windows.settings.mpq_select)
		font16.pack(side=UI.TOP, fill=UI.X)
		self.register_settings_view(font16)

		font16x = FileSettingView(parent=self, edited_state=edited_state, name='font16x.fnt', description='The 16x point font used to preview strings', setting=config.settings.files.font16x, mpq_handler=mpq_handler, mpq_history_config=config.settings.mpq_select_history, mpq_window_geometry_config=config.windows.settings.mpq_select)
		font16x.pack(side=UI.TOP, fill=UI.X)
		self.register_settings_view(font16x)
