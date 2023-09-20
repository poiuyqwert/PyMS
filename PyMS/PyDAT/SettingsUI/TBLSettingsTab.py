
from ..Config import PyDATConfig

from ...Utilities.UIKit import *
from ...Utilities.SettingsUI.SettingsTab import SettingsTab
from ...Utilities.SettingsUI.FileSettingView import FileSettingView
from ...Utilities.SettingsUI.CheckboxSettingView import CheckboxSettingView
from ...Utilities.EditedState import EditedState
from ...Utilities.MPQHandler import MPQHandler

class TBLSettingsTab(SettingsTab):
	def __init__(self, notebook: Notebook, edited_state: EditedState, config: PyDATConfig, mpq_handler: MPQHandler):
		super().__init__(notebook)

		stat_txt = FileSettingView(self, edited_state, 'stat_txt.tbl', 'Contains Unit, Weapon, Upgrade, Tech, and Order names', config.settings.files.tbls.stat_txt, mpq_handler, config.settings.mpq_select_history, config.windows.settings.mpq_select)
		stat_txt.pack(side=TOP, fill=X)
		self.register_settings_view(stat_txt)

		unitnames = FileSettingView(self, edited_state, 'unitnames.tbl', 'Contains Unit names for expanded dat files', config.settings.files.tbls.unitnames, mpq_handler, config.settings.mpq_select_history, config.windows.settings.mpq_select)
		unitnames.pack(side=TOP, fill=X)
		self.register_settings_view(unitnames)

		images = FileSettingView(self, edited_state, 'images.tbl', 'Contains GPR mpq file paths', config.settings.files.tbls.images, mpq_handler, config.settings.mpq_select_history, config.windows.settings.mpq_select)
		images.pack(side=TOP, fill=X)
		self.register_settings_view(images)

		sfxdata = FileSettingView(self, edited_state, 'sfxdata.tbl', 'Contains Sound mpq file paths', config.settings.files.tbls.sfxdata, mpq_handler, config.settings.mpq_select_history, config.windows.settings.mpq_select)
		sfxdata.pack(side=TOP, fill=X)
		self.register_settings_view(sfxdata)

		portdata = FileSettingView(self, edited_state, 'portdata.tbl', 'Contains Portrait mpq file paths', config.settings.files.tbls.portdata, mpq_handler, config.settings.mpq_select_history, config.windows.settings.mpq_select)
		portdata.pack(side=TOP, fill=X)
		self.register_settings_view(portdata)

		mapdata = FileSettingView(self, edited_state, 'mapdata.tbl', 'Contains Campign map mpq file paths', config.settings.files.tbls.mapdata, mpq_handler, config.settings.mpq_select_history, config.windows.settings.mpq_select)
		mapdata.pack(side=TOP, fill=X)
		self.register_settings_view(mapdata)

		custom_labels = CheckboxSettingView(self, edited_state, 'Use custom labels', config.settings.labels.custom)
		custom_labels.pack(side=BOTTOM)
		self.register_settings_view(custom_labels)
