
from .NameDisplaySetting import NamesDisplaySetting

from ..Utilities import Config
from ..Utilities.UIKit import Size, FileType
from ..Utilities import Assets

def _migrate_1_to_2(data: dict) -> None:
	Config.migrate_fields(data, (
		(('lastpath',), ('last_path',)),
		(('settings', 'customlabels'), ('settings', 'labels', 'custom')),
		(('settings', 'simple_labels'), ('settings', 'labels', 'simple')),
		(('names', 'Units'), ('names', 'units')),
		(('names', 'Weapons'), ('names', 'weapons')),
		(('names', 'Flingy'), ('names', 'flingy')),
		(('names', 'Sprites'), ('names', 'sprites')),
		(('names', 'Images'), ('names', 'images')),
		(('names', 'Upgrades'), ('names', 'upgrades')),
		(('names', 'Techdata'), ('names', 'techdata')),
		(('names', 'Sounds'), ('names', 'sfxdata')),
		(('names', 'Portraits'), ('names', 'portdata')),
		(('names', 'Mapdata'), ('names', 'mapdata')),
		(('names', 'Orders'), ('names', 'orders')),
		(('settings', 'files', 'stat_txt'), ('settings', 'files', 'tbls', 'stat_txt')),
		(('settings', 'files', 'unitnamestbl'), ('settings', 'files', 'tbls', 'unitnames')),
		(('settings', 'files', 'imagestbl'), ('settings', 'files', 'tbls', 'images')),
		(('settings', 'files', 'sfxdatatbl'), ('settings', 'files', 'tbls', 'sfxdata')),
		(('settings', 'files', 'portdatatbl'), ('settings', 'files', 'tbls', 'portdata')),
		(('settings', 'files', 'mapdatatbl'), ('settings', 'files', 'tbls', 'mapdata')),
		(('mpqexport',), ('mpq_export',)),
	))

class PyDATConfig(Config.Config):
	_name = 'PyDAT'
	_version = 2
	_migrations = {
		1: _migrate_1_to_2
	}

	class Windows(Config.Group):
		class Settings(Config.Group):
			def __init__(self) -> None:
				self.main = Config.WindowGeometry(default_size=Size(640,600))
				self.mpq_select = Config.WindowGeometry()
				super().__init__()

		def __init__(self) -> None:
			self.main = Config.WindowGeometry()
			self.help = Config.WindowGeometry()
			self.settings = PyDATConfig.Windows.Settings()
			self.icon_select = Config.WindowGeometry()
			self.entry_name_overrides = Config.WindowGeometry()
			self.entry_count = Config.WindowGeometry()
			super().__init__()

	class LastPath(Config.Group):
		def __init__(self) -> None:
			self.dat = Config.SelectFile(name='DAT', filetypes=[FileType.dat()])
			self.mpq = Config.SelectFile(name='MPQ', filetypes=[FileType.mpq()])
			self.entry_name_overrides = Config.SelectFile(name='Name Overrides', filetypes=[FileType.txt()])
			self.dir = Config.SelectDirectory(title='Open Directory')
			self.txt = Config.SelectFile(name='TXT', filetypes=[FileType.txt()], op_type=Config.FileOpType.import_export)
			super().__init__()

	class Settings(Config.Group):
		class Labels(Config.Group):
			def __init__(self) -> None:
				self.custom = Config.Boolean(default=False)
				self.simple = Config.Boolean(default=False)
				super().__init__()

		class Files(Config.Group):
			class Palettes(Config.Group):
				def __init__(self) -> None:
					self.units = Config.File(default=Assets.palette_file_path('Units.pal'), name='Units.pal', filetypes=[FileType.pal()])
					self.bfire = Config.File(default=Assets.palette_file_path('bfire.pal'), name='bfire.pal', filetypes=[FileType.pal()])
					self.gfire = Config.File(default=Assets.palette_file_path('gfire.pal'), name='gfire.pal', filetypes=[FileType.pal()])
					self.ofire = Config.File(default=Assets.palette_file_path('ofire.pal'), name='ofire.pal', filetypes=[FileType.pal()])
					self.terrain = Config.File(default=Assets.palette_file_path('Terrain.pal'), name='Terrain.pal', filetypes=[FileType.pal()])
					self.icons = Config.File(default=Assets.palette_file_path('Icons.pal'), name='Icons.pal', filetypes=[FileType.pal()])
					super().__init__()

			class TBLs(Config.Group):
				def __init__(self) -> None:
					self.stat_txt = Config.File(default=Assets.mpq_file_ref('rez', 'stat_txt.tbl'), name='stat_txt.tbl', filetypes=[FileType.tbl()])
					self.unitnames = Config.File(default=Assets.mpq_file_ref('rez', 'unitnames.tbl'), name='unitnames.tbl', filetypes=[FileType.tbl()])
					self.images = Config.File(default=Assets.mpq_file_ref('arr', 'images.tbl'), name='images.tbl', filetypes=[FileType.tbl()])
					self.sfxdata = Config.File(default=Assets.mpq_file_ref('arr', 'sfxdata.tbl'), name='sfxdata.tbl', filetypes=[FileType.tbl()])
					self.portdata = Config.File(default=Assets.mpq_file_ref('arr', 'portdata.tbl'), name='portdata.tbl', filetypes=[FileType.tbl()])
					self.mapdata = Config.File(default=Assets.mpq_file_ref('arr', 'mapdata.tbl'), name='mapdata.tbl', filetypes=[FileType.tbl()])
					super().__init__()

			def __init__(self) -> None:
				self.palettes = PyDATConfig.Settings.Files.Palettes()
				self.tbls = PyDATConfig.Settings.Files.TBLs()
				self.iscript_bin = Config.File(default=Assets.mpq_file_ref('scripts', 'iscript.bin'), name='iscript.bin', filetypes=[FileType.bin_iscript()])
				self.cmdicons = Config.File(default=Assets.mpq_file_ref('unit', 'cmdbtns', 'cmdicons.grp'), name='cmdicons.grp', filetypes=[FileType.grp()])
				self.ticon = Config.File(default=Assets.mpq_file_ref('unit', 'cmdbtns', 'ticon.pcx'), name='ticon.pcx', filetypes=[FileType.pal_pcx()])
				super().__init__()

		class LastPath(Config.Group):
			def __init__(self) -> None:
				self.mpqs = Config.SelectFile(name='MPQ', filetypes=[FileType.mpq_all(),FileType.mpq(),FileType.exe_mpq(),FileType.scm(),FileType.scx()])
				super().__init__()

		def __init__(self) -> None:
			self.labels = PyDATConfig.Settings.Labels()
			self.files = PyDATConfig.Settings.Files()
			self.mpq_select_history = Config.List(value_type=str)
			self.mpqs = Config.List(value_type=str)
			self.last_path = PyDATConfig.Settings.LastPath()
			self.reference_limits = Config.Boolean(default=True)
			super().__init__()

	class Names(Config.Group):
		class Options(Config.Group):
			def __init__(self) -> None:
				self.display = Config.Enum(enum_type=NamesDisplaySetting, default=NamesDisplaySetting.basic)
				super().__init__()
		
		class SimpleOptions(Options):
			def __init__(self) -> None:
				self.simple = Config.Boolean(default=False)
				super().__init__()

		def __init__(self) -> None:
			self.units = PyDATConfig.Names.SimpleOptions()
			self.weapons = PyDATConfig.Names.SimpleOptions()
			self.flingy = PyDATConfig.Names.Options()
			self.sprites = PyDATConfig.Names.Options()
			self.images = PyDATConfig.Names.Options()
			self.upgrades = PyDATConfig.Names.SimpleOptions()
			self.techdata = PyDATConfig.Names.SimpleOptions()
			self.sfxdata = PyDATConfig.Names.Options()
			self.portdata = PyDATConfig.Names.Options()
			self.mapdata = PyDATConfig.Names.Options()
			self.orders = PyDATConfig.Names.SimpleOptions()
			super().__init__()

	class DontWarn(Config.Group):
		def __init__(self) -> None:
			self.expanded_dat = Config.Warning(message="This DAT file is expanded and will require a plugin like 'DatExtend'.")
			super().__init__()

	class Preview(Config.Group):
		class Options(Config.Group):
			def __init__(self) -> None:
				self.show = Config.Boolean(default=False)
				super().__init__()

		class UnitOptions(Options):
			def __init__(self) -> None:
				self.show_placement = Config.Boolean(default=False)
				self.show_dimensions = Config.Boolean(default=False)
				self.show_addon_placement = Config.Boolean(default=False)
				self.addon_parent_unit_id = Config.Int(default=106)
				super().__init__()

		def __init__(self) -> None:
			self.image = PyDATConfig.Preview.Options()
			self.sprite = PyDATConfig.Preview.Options()
			self.unit = PyDATConfig.Preview.UnitOptions()
			self.staredit = PyDATConfig.Preview.Options()
			super().__init__()

	def __init__(self) -> None:
		self.theme = Config.String()
		self.windows = PyDATConfig.Windows()
		self.last_path = PyDATConfig.LastPath()
		self.mpqs = Config.List(value_type=str)
		self.settings = PyDATConfig.Settings()
		self.names = PyDATConfig.Names()
		self.mpq_export = Config.List(value_type=str)
		self.show_listbox_options = Config.Boolean(default=True)
		self.list_size = Config.PaneSizes(defaults=[300])
		self.dont_warn = PyDATConfig.DontWarn()
		self.show_used_by = Config.Boolean(default=True)
		self.preview = PyDATConfig.Preview()
		super().__init__()
