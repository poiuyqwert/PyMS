
from ..Config import PyTRGConfig

from ...Utilities.UIKit import *
from ...Utilities.SettingsUI.SettingsTab import SettingsTab
from ...Utilities.SettingsUI.FileSettingView import FileSettingView
from ...Utilities.EditedState import EditedState
from ...Utilities.MPQHandler import MPQHandler

class FilesSettingsTab(SettingsTab):
	def __init__(self, notebook: Notebook, edited_state: EditedState, config: PyTRGConfig, mpq_handler: MPQHandler):
		super().__init__(notebook)

		stat_txt = FileSettingView(parent=self, edited_state=edited_state, name='stat_txt.tbl', description='Contains Unit and AI Script names', setting=config.settings.files.stat_txt, mpq_handler=mpq_handler, mpq_history_config=config.settings.mpq_select_history, mpq_window_geometry_config=config.windows.settings.mpq_select)
		stat_txt.pack(side=TOP, fill=X)
		self.register_settings_view(stat_txt)

		aiscript = FileSettingView(parent=self, edited_state=edited_state, name='aiscript.bin', description="Contains AI ID's and references to names in stat_txt.tbl", setting=config.settings.files.aiscript, mpq_handler=mpq_handler, mpq_history_config=config.settings.mpq_select_history, mpq_window_geometry_config=config.windows.settings.mpq_select)
		aiscript.pack(side=TOP, fill=X)
		self.register_settings_view(aiscript)

		bwscript = FileSettingView(parent=self, edited_state=edited_state, name='bwscript.bin', description="Contains AI ID's and references to names in stat_txt.tbl", setting=config.settings.files.bwscript, mpq_handler=mpq_handler, mpq_history_config=config.settings.mpq_select_history, mpq_window_geometry_config=config.windows.settings.mpq_select)
		bwscript.pack(side=TOP, fill=X)
		self.register_settings_view(bwscript)
