
from ..Config import PyDATConfig

from ...Utilities import UIKit as UI
from ...Utilities.SettingsUI.SettingsTab import SettingsTab
from ...Utilities.SettingsUI.FileSettingView import FileSettingView
from ...Utilities.SettingsUI.CheckboxSettingView import CheckboxSettingView
from ...Utilities.EditedState import EditedState
from ...Utilities.MPQHandler import MPQHandler

class TBLSettingsTab(SettingsTab):
	def __init__(self, notebook: UI.Notebook, edited_state: EditedState, config: PyDATConfig, mpq_handler: MPQHandler):
		super().__init__(notebook)

		stat_txt = FileSettingView(parent=self, edited_state=edited_state, name='stat_txt.tbl', description='Contains Unit, Weapon, Upgrade, Tech, and Order names', setting=config.settings.files.tbls.stat_txt, mpq_handler=mpq_handler, mpq_history_config=config.settings.mpq_select_history, mpq_window_geometry_config=config.windows.settings.mpq_select)
		stat_txt.pack(side=UI.TOP, fill=UI.X)
		self.register_settings_view(stat_txt)

		unitnames = FileSettingView(parent=self, edited_state=edited_state, name='unitnames.tbl', description='Contains Unit names for expanded dat files', setting=config.settings.files.tbls.unitnames, mpq_handler=mpq_handler, mpq_history_config=config.settings.mpq_select_history, mpq_window_geometry_config=config.windows.settings.mpq_select)
		unitnames.pack(side=UI.TOP, fill=UI.X)
		self.register_settings_view(unitnames)

		images = FileSettingView(parent=self, edited_state=edited_state, name='images.tbl', description='Contains GPR mpq file paths', setting=config.settings.files.tbls.images, mpq_handler=mpq_handler, mpq_history_config=config.settings.mpq_select_history, mpq_window_geometry_config=config.windows.settings.mpq_select)
		images.pack(side=UI.TOP, fill=UI.X)
		self.register_settings_view(images)

		sfxdata = FileSettingView(parent=self, edited_state=edited_state, name='sfxdata.tbl', description='Contains Sound mpq file paths', setting=config.settings.files.tbls.sfxdata, mpq_handler=mpq_handler, mpq_history_config=config.settings.mpq_select_history, mpq_window_geometry_config=config.windows.settings.mpq_select)
		sfxdata.pack(side=UI.TOP, fill=UI.X)
		self.register_settings_view(sfxdata)

		portdata = FileSettingView(parent=self, edited_state=edited_state, name='portdata.tbl', description='Contains Portrait mpq file paths', setting=config.settings.files.tbls.portdata, mpq_handler=mpq_handler, mpq_history_config=config.settings.mpq_select_history, mpq_window_geometry_config=config.windows.settings.mpq_select)
		portdata.pack(side=UI.TOP, fill=UI.X)
		self.register_settings_view(portdata)

		mapdata = FileSettingView(parent=self, edited_state=edited_state, name='mapdata.tbl', description='Contains Campign map mpq file paths', setting=config.settings.files.tbls.mapdata, mpq_handler=mpq_handler, mpq_history_config=config.settings.mpq_select_history, mpq_window_geometry_config=config.windows.settings.mpq_select)
		mapdata.pack(side=UI.TOP, fill=UI.X)
		self.register_settings_view(mapdata)

		custom_labels = CheckboxSettingView(self, edited_state, 'Use custom labels', config.settings.labels.custom)
		custom_labels.pack(side=UI.BOTTOM)
		self.register_settings_view(custom_labels)
