
from ..Config import PyTBLConfig

from ...Utilities.UIKit import *
from ...Utilities.SettingsUI.SettingsTab import SettingsTab
from ...Utilities.SettingsUI.FileSettingView import FileSettingView
from ...Utilities.EditedState import EditedState
from ...Utilities.MPQHandler import MPQHandler

class PreviewSettingsTab(SettingsTab):
	def __init__(self, notebook: Notebook, edited_state: EditedState, config: PyTBLConfig, mpq_handler: MPQHandler):
		super().__init__(notebook)

		tfontgam = FileSettingView(parent=self, edited_state=edited_state, name='tfontgam.pcx', description='The special palette which holds text colors.', setting=config.settings.files.tfontgam, mpq_handler=mpq_handler, mpq_history_config=config.settings.mpq_select_history, mpq_window_geometry_config=config.windows.settings.mpq_select)
		tfontgam.pack(side=TOP, fill=X)
		self.register_settings_view(tfontgam)

		font8 = FileSettingView(parent=self, edited_state=edited_state, name='font8.fnt', description='The font used to preview hotkeys', setting=config.settings.files.font8, mpq_handler=mpq_handler, mpq_history_config=config.settings.mpq_select_history, mpq_window_geometry_config=config.windows.settings.mpq_select)
		font8.pack(side=TOP, fill=X)
		self.register_settings_view(font8)

		font10 = FileSettingView(parent=self, edited_state=edited_state, name='font10.fnt', description='The font used to preview strings other than hotkeys', setting=config.settings.files.font10, mpq_handler=mpq_handler, mpq_history_config=config.settings.mpq_select_history, mpq_window_geometry_config=config.windows.settings.mpq_select)
		font10.pack(side=TOP, fill=X)
		self.register_settings_view(font10)

		icons = FileSettingView(parent=self, edited_state=edited_state, name='icons.grp', description='The icons used to preview hotkeys', setting=config.settings.files.icons, mpq_handler=mpq_handler, mpq_history_config=config.settings.mpq_select_history, mpq_window_geometry_config=config.windows.settings.mpq_select)
		icons.pack(side=TOP, fill=X)
		self.register_settings_view(icons)

		unit_pal = FileSettingView(parent=self, edited_state=edited_state, name='Unit Palette', description='The palette used to display icons.grp', setting=config.settings.files.unit_pal, mpq_handler=mpq_handler, mpq_history_config=config.settings.mpq_select_history, mpq_window_geometry_config=config.windows.settings.mpq_select)
		unit_pal.pack(side=TOP, fill=X)
		self.register_settings_view(unit_pal)
