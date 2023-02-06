
from .DATData import NamesDisplaySetting

from ..Utilities import SettingsFile
from ..Utilities.UIKit.FileType import FileType
from ..Utilities import Assets

def migrate_from_v1(data):
	try:
		data['windows']['entry_count'] = data['window']['entry_count']
	except:
		pass
	data['listbox'] = {}
	try:
		data['listbox']['size'] = data['list_size']
	except:
		pass
	try:
		data['listbox']['show_options'] = data['show_listbox_options']
	except:
		pass
	try:
		data.update(data['settings'])
	except:
		pass
	try:
		data['lastpath']['txt']['save'] = data['lastpath']['txt']['export']
		data['lastpath']['txt']['open'] = data['lastpath']['txt']['import']
	except:
		pass
	try:
		data['lastpath']['dat']['save'] = data['lastpath']['dat']['save'][data['lastpath']['dat']['save'].keys()[0]]
	except:
		pass
	try:
		for key in data['names'].keys():
			data['names'][key.lower()] = data['names'][key]
	except:
		pass
	try:
		for key in data['files'].keys():
			data['files'][key.lower()] = data['files'][key]
	except:
		pass
	return data

class Settings(SettingsFile.SettingsFile):
	_name = 'PyDAT'
	_version = 2
	_migrations = [migrate_from_v1]

	class DontWarn(SettingsFile.Group):
		def __init__(self):
			self.expanded_dat = SettingsFile.Warning("This .dat file is expanded and will require a plugin like 'DatExtend'.")
			SettingsFile.Group.__init__(self)

	class LastPath(SettingsFile.Group):
		def __init__(self):
			self.dat = SettingsFile.SelectFile('DAT', [FileType.dat()])
			self.entry_name_overrides = SettingsFile.SelectFile('Name Overrides', [FileType.txt()])
			self.mpq = SettingsFile.SelectFile('MPQ', [FileType.mpq(),FileType.exe_mpq()])
			self.txt = SettingsFile.SelectFile('TXT', [FileType.txt()])
			self.dir = SettingsFile.SelectDirectory('Open Directory')
			SettingsFile.Group.__init__(self)

	class Windows(SettingsFile.Group):
		class Settings(SettingsFile.Group):
			def __init__(self):
				self.main = SettingsFile.WindowGeometry()
				self.mpqselect = SettingsFile.WindowGeometry()
				SettingsFile.Group.__init__(self)

		def __init__(self):
			self.main = SettingsFile.WindowGeometry()
			self.entry_count = SettingsFile.WindowGeometry()
			self.entry_name_overrides = SettingsFile.WindowGeometry()
			self.help = SettingsFile.WindowGeometry()
			self.icon_select = SettingsFile.WindowGeometry()
			self.settings = Settings.Windows.Settings()
			SettingsFile.Group.__init__(self)

	class Listbox(SettingsFile.Group):
		def __init__(self):
			self.size = SettingsFile.PaneSizes(default_sizes=300)
			self.show_options = SettingsFile.Boolean(default=True)
			SettingsFile.Group.__init__(self)

	class Names(SettingsFile.Group):
		class NameDisplay(SettingsFile.Group):
			def __init__(self):
				self.display = SettingsFile.Enum(options=[NamesDisplaySetting.basic, NamesDisplaySetting.tbl, NamesDisplaySetting.combine], default_option=NamesDisplaySetting.basic)
				self.simple = SettingsFile.Boolean(default=True)
				SettingsFile.Group.__init__(self)
		def __init__(self):
			self.flingy = Settings.Names.NameDisplay()
			self.images = Settings.Names.NameDisplay()
			self.mapdata = Settings.Names.NameDisplay()
			self.orders = Settings.Names.NameDisplay()
			self.portdata = Settings.Names.NameDisplay()
			self.sfxdata = Settings.Names.NameDisplay()
			self.sprites = Settings.Names.NameDisplay()
			self.techdata = Settings.Names.NameDisplay()
			self.units = Settings.Names.NameDisplay()
			self.upgrades = Settings.Names.NameDisplay()
			self.weapons = Settings.Names.NameDisplay()
			SettingsFile.Group.__init__(self)

	class Preview(SettingsFile.Group):
		class Image(SettingsFile.Group):
			def __init__(self):
				self.show = SettingsFile.Boolean(default=False)
				SettingsFile.Group.__init__(self)
		class Sprite(SettingsFile.Group):
			def __init__(self):
				self.show = SettingsFile.Boolean(default=False)
				SettingsFile.Group.__init__(self)
		class StarEdit(SettingsFile.Group):
			def __init__(self):
				self.show = SettingsFile.Boolean(default=False)
				SettingsFile.Group.__init__(self)
		class Unit(SettingsFile.Group):
			def __init__(self):
				self.show = SettingsFile.Boolean(default=False)
				self.show_addon_placement = SettingsFile.Boolean(default=False)
				self.show_dimensions = SettingsFile.Boolean(default=False)
				self.show_placement = SettingsFile.Boolean(default=False)
				self.addon_parent_unit_id = SettingsFile.Int(default=106)
				SettingsFile.Group.__init__(self)
		def __init__(self):
			self.image = Settings.Preview.Image()
			self.sprite = Settings.Preview.Sprite()
			self.staredit = Settings.Preview.StarEdit()
			self.unit = Settings.Preview.Unit()
			SettingsFile.Group.__init__(self)

	class Files(SettingsFile.Group):
		class Palettes(SettingsFile.Group):
			def __init__(self):
				self.icons = SettingsFile.File(default=Assets.palette_file_path('Icons.pal'))
				self.terrain = SettingsFile.File(default=Assets.palette_file_path('Terrain.pal'))
				self.units = SettingsFile.File(default=Assets.palette_file_path('Units.pal'))
				self.bfire = SettingsFile.File(default=Assets.palette_file_path('bfire.pal'))
				self.gfire = SettingsFile.File(default=Assets.palette_file_path('gfire.pal'))
				self.ofire = SettingsFile.File(default=Assets.palette_file_path('ofire.pal'))
				self.ticon = SettingsFile.File(default=Assets.mpq_file_ref('unit', 'cmdbtns', 'ticon.pcx'))
				SettingsFile.Group.__init__(self)
		class TBLs(SettingsFile.Group):
			def __init__(self):
				self.images = SettingsFile.File(default=Assets.mpq_file_ref('arr', 'images.tbl'))
				self.mapdata = SettingsFile.File(default=Assets.mpq_file_ref('arr', 'mapdata.tbl'))
				self.portdata = SettingsFile.File(default=Assets.mpq_file_ref('arr', 'portdata.tbl'))
				self.sfxdata = SettingsFile.File(default=Assets.mpq_file_ref('arr', 'sfxdata.tbl'))
				self.stat_txt = SettingsFile.File(default=Assets.mpq_file_ref('rez', 'stat_txt.tbl'))
				self.unitnames = SettingsFile.File()
				SettingsFile.Group.__init__(self)
		def __init__(self):
			self.palettes = Settings.Files.Palettes()
			self.tbls = Settings.Files.TBLs()
			self.cmdicons_grp = SettingsFile.File(default=Assets.mpq_file_ref('unit', 'cmdbtns', 'cmdicons.grp'))
			self.iscript_bin = SettingsFile.File(default=Assets.mpq_file_ref('scripts', 'iscript.bin'))
			SettingsFile.Group.__init__(self)

	def __init__(self):
		self.dont_warn = Settings.DontWarn()
		self.windows = Settings.Windows()
		self.lastpath = Settings.LastPath()
		self.listbox = Settings.Listbox()
		self.theme = SettingsFile.String(optional=True)
		self.show_used_by = SettingsFile.Boolean(default=True)
		self.mpqexport = SettingsFile.StringList()
		self.names = Settings.Names()
		self.preview = Settings.Preview()
		self.sempq = SettingsFile.Boolean(default=False)
		self.customlabels = SettingsFile.Boolean(default=False) # TODO: Deprecated in favour of `names`?
		self.mpqs = SettingsFile.StringList()
		self.mpqselecthistory = SettingsFile.StringList()
		self.reference_limits = SettingsFile.Boolean(default=True)
		self.files = Settings.Files()
		SettingsFile.SettingsFile.__init__(self)
