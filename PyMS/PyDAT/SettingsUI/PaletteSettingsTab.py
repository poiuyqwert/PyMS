
from ..Config import PyDATConfig

from ...Utilities import UIKit as UI
from ...Utilities.SettingsUI.SettingsTab import SettingsTab
from ...Utilities.SettingsUI.FileSettingView import FileSettingView
from ...Utilities.EditedState import EditedState
from ...Utilities.MPQHandler import MPQHandler

class PaletteSettingsTab(SettingsTab):
	def __init__(self, notebook: UI.Notebook, edited_state: EditedState, config: PyDATConfig, mpq_handler: MPQHandler):
		super().__init__(notebook)

		unit_pal = FileSettingView(parent=self, edited_state=edited_state, name='Units.pal', description='Used to display normal graphics previews', setting=config.settings.files.palettes.units, mpq_handler=mpq_handler, mpq_history_config=config.settings.mpq_select_history, mpq_window_geometry_config=config.windows.settings.mpq_select)
		unit_pal.pack(side=UI.TOP, fill=UI.X)
		self.register_settings_view(unit_pal)

		bfire_pal = FileSettingView(parent=self, edited_state=edited_state, name='bfire.pal', description='Used to display graphics previews with bfire remapping', setting=config.settings.files.palettes.bfire, mpq_handler=mpq_handler, mpq_history_config=config.settings.mpq_select_history, mpq_window_geometry_config=config.windows.settings.mpq_select)
		bfire_pal.pack(side=UI.TOP, fill=UI.X)
		self.register_settings_view(bfire_pal)

		gfire_pal = FileSettingView(parent=self, edited_state=edited_state, name='gfire.pal', description='Used to display graphics previews with gfire remapping', setting=config.settings.files.palettes.gfire, mpq_handler=mpq_handler, mpq_history_config=config.settings.mpq_select_history, mpq_window_geometry_config=config.windows.settings.mpq_select)
		gfire_pal.pack(side=UI.TOP, fill=UI.X)
		self.register_settings_view(gfire_pal)

		ofire_pal = FileSettingView(parent=self, edited_state=edited_state, name='ofire.pal', description='Used to display graphics previews with ofire remapping', setting=config.settings.files.palettes.ofire, mpq_handler=mpq_handler, mpq_history_config=config.settings.mpq_select_history, mpq_window_geometry_config=config.windows.settings.mpq_select)
		ofire_pal.pack(side=UI.TOP, fill=UI.X)
		self.register_settings_view(ofire_pal)

		terrain_pal = FileSettingView(parent=self, edited_state=edited_state, name='Terrain.pal', description='Used to display terrain based graphics previews', setting=config.settings.files.palettes.terrain, mpq_handler=mpq_handler, mpq_history_config=config.settings.mpq_select_history, mpq_window_geometry_config=config.windows.settings.mpq_select)
		terrain_pal.pack(side=UI.TOP, fill=UI.X)
		self.register_settings_view(terrain_pal)

		icons_pal = FileSettingView(parent=self, edited_state=edited_state, name='Icons.pal', description='Used to display icon previews', setting=config.settings.files.palettes.icons, mpq_handler=mpq_handler, mpq_history_config=config.settings.mpq_select_history, mpq_window_geometry_config=config.windows.settings.mpq_select)
		icons_pal.pack(side=UI.TOP, fill=UI.X)
		self.register_settings_view(icons_pal)
