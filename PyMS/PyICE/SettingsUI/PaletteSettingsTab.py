
from ..Config import PyICEConfig

from ...Utilities.UIKit import *
from ...Utilities.SettingsUI.SettingsTab import SettingsTab
from ...Utilities.SettingsUI.FileSettingView import FileSettingView
from ...Utilities.EditedState import EditedState
from ...Utilities.MPQHandler import MPQHandler

class PaletteSettingsTab(SettingsTab):
	def __init__(self, notebook: Notebook, edited_state: EditedState, config: PyICEConfig, mpq_handler: MPQHandler):
		super().__init__(notebook)

		unit_pal = FileSettingView(self, edited_state, 'Units.pal', 'Used to display normal graphics previews', config.settings.files.palettes.units, mpq_handler, config.settings.mpq_select_history, config.windows.settings.mpq_select)
		unit_pal.pack(side=TOP, fill=X)
		self.register_settings_view(unit_pal)

		bfire_pal = FileSettingView(self, edited_state, 'bfire.pal', 'Used to display graphics previews with bfire remapping', config.settings.files.palettes.bfire, mpq_handler, config.settings.mpq_select_history, config.windows.settings.mpq_select)
		bfire_pal.pack(side=TOP, fill=X)
		self.register_settings_view(bfire_pal)

		gfire_pal = FileSettingView(self, edited_state, 'gfire.pal', 'Used to display graphics previews with gfire remapping', config.settings.files.palettes.gfire, mpq_handler, config.settings.mpq_select_history, config.windows.settings.mpq_select)
		gfire_pal.pack(side=TOP, fill=X)
		self.register_settings_view(gfire_pal)

		ofire_pal = FileSettingView(self, edited_state, 'ofire.pal', 'Used to display graphics previews with ofire remapping', config.settings.files.palettes.ofire, mpq_handler, config.settings.mpq_select_history, config.windows.settings.mpq_select)
		ofire_pal.pack(side=TOP, fill=X)
		self.register_settings_view(ofire_pal)

		terrain_pal = FileSettingView(self, edited_state, 'Terrain.pal', 'Used to display terrain based graphics previews', config.settings.files.palettes.terrain, mpq_handler, config.settings.mpq_select_history, config.windows.settings.mpq_select)
		terrain_pal.pack(side=TOP, fill=X)
		self.register_settings_view(terrain_pal)

		icons_pal = FileSettingView(self, edited_state, 'Icons.pal', 'Used to display icon previews', config.settings.files.palettes.icons, mpq_handler, config.settings.mpq_select_history, config.windows.settings.mpq_select)
		icons_pal.pack(side=TOP, fill=X)
		self.register_settings_view(icons_pal)
