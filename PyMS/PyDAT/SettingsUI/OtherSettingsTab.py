
from ..Config import PyDATConfig

from ...Utilities.UIKit import *
from ...Utilities.SettingsUI.SettingsTab import SettingsTab
from ...Utilities.SettingsUI.FileSettingView import FileSettingView
from ...Utilities.EditedState import EditedState
from ...Utilities.MPQHandler import MPQHandler

class OtherSettingsTab(SettingsTab):
	def __init__(self, notebook: Notebook, edited_state: EditedState, config: PyDATConfig, mpq_handler: MPQHandler):
		super().__init__(notebook)

		cmdicons = FileSettingView(self, edited_state, 'cmdicons.grp', 'Contains icon images', config.settings.files.cmdicons, mpq_handler, config.settings.mpq_select_history, config.windows.settings.mpq_select)
		cmdicons.pack(side=TOP, fill=X)
		self.register_settings_view(cmdicons)

		iscript_bin = FileSettingView(self, edited_state, 'iscript.bin', 'Contains iscript entries for images.dat', config.settings.files.iscript_bin, mpq_handler, config.settings.mpq_select_history, config.windows.settings.mpq_select)
		iscript_bin.pack(side=TOP, fill=X)
		self.register_settings_view(iscript_bin)
