
from ..Config import PyDATConfig

from ...Utilities.UIKit import *
from ...Utilities.SettingsUI.SettingsTab import SettingsTab
from ...Utilities.SettingsUI.FileSettingView import FileSettingView
from ...Utilities.EditedState import EditedState
from ...Utilities.MPQHandler import MPQHandler

class OtherSettingsTab(SettingsTab):
	def __init__(self, notebook: Notebook, edited_state: EditedState, config: PyDATConfig, mpq_handler: MPQHandler):
		super().__init__(notebook)

		cmdicons = FileSettingView(parent=self, edited_state=edited_state, name='cmdicons.grp', description='Contains icon images', setting=config.settings.files.cmdicons, mpq_handler=mpq_handler, mpq_history_config=config.settings.mpq_select_history, mpq_window_geometry_config=config.windows.settings.mpq_select)
		cmdicons.pack(side=TOP, fill=X)
		self.register_settings_view(cmdicons)

		iscript_bin = FileSettingView(parent=self, edited_state=edited_state, name='iscript.bin', description='Contains iscript entries for images.dat', setting=config.settings.files.iscript_bin, mpq_handler=mpq_handler, mpq_history_config=config.settings.mpq_select_history, mpq_window_geometry_config=config.windows.settings.mpq_select)
		iscript_bin.pack(side=TOP, fill=X)
		self.register_settings_view(iscript_bin)
