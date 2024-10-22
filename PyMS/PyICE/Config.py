
from .CodeGenerators import GeneratorPreset

from ..Utilities import Config
from ..Utilities.UIKit import Size, FileType
from ..Utilities import Assets

def _migrate_1_to_2(data: dict) -> None:
	Config.migrate_fields(data, (
		(('lastpath',), ('last_path',)),
		(('windows', 'codeedit'), ('windows', 'code_edit')),
		(('windows', 'listimport'), ('windows', 'list_import')),
		(('settings', 'files', 'unitsdat'), ('settings', 'files', 'dat', 'units')),
		(('settings', 'files', 'weaponsdat'), ('settings', 'files', 'dat', 'weapons')),
		(('settings', 'files', 'spritesdat'), ('settings', 'files', 'dat', 'sprites')),
		(('settings', 'files', 'flingydat'), ('settings', 'files', 'dat', 'flingy')),
		(('settings', 'files', 'imagesdat'), ('settings', 'files', 'dat', 'images')),
		(('settings', 'files', 'sfxdatadat'), ('settings', 'files', 'dat', 'sfxdata')),
		(('settings', 'files', 'stat_txt'), ('settings', 'files', 'tbl', 'stat_txt')),
		(('settings', 'files', 'imagestbl'), ('settings', 'files', 'tbl', 'images')),
		(('settings', 'files', 'unitnamestbl'), ('settings', 'files', 'tbl', 'unitnames')),
		(('findhistory',), ('find_history',)),
		(('generator', 'variables_list'), ('generator', 'pane', 'variables_list')),
		(('generator', 'code_box'), ('generator', 'pane', 'code_box')),
		(('sounds', 'closeafter'), ('sounds', 'close_after')),
		(('previewer', 'closeafter'), ('previewer', 'close_after')),
		(('previewer', 'showpreview'), ('previewer', 'show_preview')),
		(('previewer', 'looppreview'), ('previewer', 'loop_preview')),
		(('previewer', 'previewspeed'), ('previewer', 'preview_speed')),
	))

class PyICEConfig(Config.Config):
	_name = 'PyICE'
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

		class Generator(Config.Group):
			def __init__(self) -> None:
				self.main = Config.WindowGeometry()
				self.name = Config.WindowGeometry()
				self.presets = Config.WindowGeometry()
				super().__init__()

		def __init__(self) -> None:
			self.main = Config.WindowGeometry()
			self.help = Config.WindowGeometry()
			self.settings = PyICEConfig.Windows.Settings()
			self.code_edit = Config.WindowGeometry()
			self.list_import = Config.WindowGeometry()
			self.find_replace = Config.WindowGeometry()
			self.find = Config.WindowGeometry()
			self.generator = PyICEConfig.Windows.Generator()
			super().__init__()

	class LastPath(Config.Group):
		class Generators(Config.Group):
			def __init__(self) -> None:
				self.txt = Config.SelectFile(name='Preset', op_type=Config.FileOpType.import_export, filetypes=[FileType.txt()])
				super().__init__()

		def __init__(self) -> None:
			self.bin = Config.SelectFile(name='IScript .bin', filetypes=[FileType.bin_iscript()])
			self.txt = Config.SelectFile(name='TXT', op_type=Config.FileOpType.import_export, filetypes=[FileType.txt()])
			self.generators = PyICEConfig.LastPath.Generators()
			super().__init__()

	class Settings(Config.Group):
		class Files(Config.Group):
			class DAT(Config.Group):
				def __init__(self) -> None:
					self.units = Config.File(default=Assets.mpq_file_path('arr', 'units.dat'), name='units.dat', filetypes=[FileType.dat()])
					self.weapons = Config.File(default=Assets.mpq_file_path('arr', 'weapons.dat'), name='weapons.dat', filetypes=[FileType.dat()])
					self.sprites = Config.File(default=Assets.mpq_file_path('arr', 'sprites.dat'), name='sprites.dat', filetypes=[FileType.dat()])
					self.flingy = Config.File(default=Assets.mpq_file_path('arr', 'flingy.dat'), name='flingy.dat', filetypes=[FileType.dat()])
					self.images = Config.File(default=Assets.mpq_file_path('arr', 'images.dat'), name='images.dat', filetypes=[FileType.dat()])
					self.sfxdata = Config.File(default=Assets.mpq_file_path('arr', 'sfxdata.dat'), name='sfxdata.dat', filetypes=[FileType.dat()])
					super().__init__()
	
			class TBL(Config.Group):
				def __init__(self) -> None:
					self.stat_txt = Config.File(default=Assets.mpq_file_path('rez', 'stat_txt.tbl'), name='stat_txt.tbl', filetypes=[FileType.tbl()])
					self.images = Config.File(default=Assets.mpq_file_path('arr', 'images.tbl'), name='images.tbl', filetypes=[FileType.tbl()])
					self.sfxdata = Config.File(default=Assets.mpq_file_path('arr', 'sfxdata.tbl'), name='sfxdata.tbl', filetypes=[FileType.tbl()])
					self.unitnames = Config.File(default=Assets.mpq_file_path('rez', 'unitnames.tbl'), name='unitnames.tbl', filetypes=[FileType.tbl()])
					super().__init__()

			class Palettes(Config.Group):
				def __init__(self) -> None:
					self.units = Config.File(default=Assets.palette_file_path('Units.pal'), name='Units.pal', filetypes=[FileType.pal()])
					self.bfire = Config.File(default=Assets.palette_file_path('bfire.pal'), name='bfire.pal', filetypes=[FileType.pal()])
					self.gfire = Config.File(default=Assets.palette_file_path('gfire.pal'), name='gfire.pal', filetypes=[FileType.pal()])
					self.ofire = Config.File(default=Assets.palette_file_path('ofire.pal'), name='ofire.pal', filetypes=[FileType.pal()])
					self.terrain = Config.File(default=Assets.palette_file_path('Terrain.pal'), name='Terrain.pal', filetypes=[FileType.pal()])
					self.icons = Config.File(default=Assets.palette_file_path('Icons.pal'), name='Icons.pal', filetypes=[FileType.pal()])
					super().__init__()

			def __init__(self) -> None:
				self.dat = PyICEConfig.Settings.Files.DAT()
				self.tbl = PyICEConfig.Settings.Files.TBL()
				self.palettes = PyICEConfig.Settings.Files.Palettes()
				super().__init__()

		class LastPath(Config.Group):
			def __init__(self) -> None:
				self.mpqs = Config.SelectFile(name='MPQ', filetypes=[FileType.mpq_all(),FileType.mpq(),FileType.exe_mpq(),FileType.scm(),FileType.scx()])
				super().__init__()

		def __init__(self) -> None:
			self.files = PyICEConfig.Settings.Files()
			self.mpq_select_history = Config.List(value_type=str)
			self.mpqs = Config.List(value_type=str)
			self.last_path = PyICEConfig.Settings.LastPath()
			super().__init__()

	class Code(Config.Group):
		class Highlights(Config.Group):
			def __init__(self) -> None:
				self.comment = Config.HighlightStyle(default=Config.Style(foreground='#008000'))
				self.keyword = Config.HighlightStyle(default=Config.Style(foreground='#0000FF', bold=True))
				self.block = Config.HighlightStyle(default=Config.Style(foreground='#FF00FF'))
				self.command = Config.HighlightStyle(default=Config.Style(foreground='#0000AA'))
				self.header_command = Config.HighlightStyle(default=Config.Style(foreground='#0000AA'))
				self.number = Config.HighlightStyle(default=Config.Style(foreground='#FF0000'))
				self.operator = Config.HighlightStyle(default=Config.Style(foreground='#0000FF', bold=True))
				self.header = Config.HighlightStyle(default=Config.Style(foreground='#0000FF', bold=True))
				self.newline = Config.HighlightStyle(default=Config.Style())
				self.selection = Config.HighlightStyle(default=Config.Style(background='#C0C0C0'))
				self.error = Config.HighlightStyle(default=Config.Style(background='#FF8C8C'))
				self.warning = Config.HighlightStyle(default=Config.Style(background='#FFC8C8'))
				super().__init__()

		def __init__(self) -> None:
			self.highlights = PyICEConfig.Code.Highlights()
			super().__init__()

	class Generator(Config.Group):
		class Pane(Config.Group):
			def __init__(self) -> None:
				self.variables_list = Config.PaneSizes()
				self.code_box = Config.PaneSizes()
				super().__init__()

		def __init__(self) -> None:
			self.presets = Config.JSONList(value_type=GeneratorPreset.GeneratorPreset, defaults=GeneratorPreset.DEFAULT_PRESETS)
			self.pane = PyICEConfig.Generator.Pane()
			super().__init__()

	class Sounds(Config.Group):
		def __init__(self) -> None:
			self.overwrite = Config.Boolean(default=False)
			self.close_after = Config.Boolean(default=False)
			super().__init__()

	class Previewer(Config.Group):
		def __init__(self) -> None:
			self.overwrite = Config.Boolean(default=False)
			self.close_after = Config.Boolean(default=False)
			self.show_preview = Config.Boolean(default=True)
			self.loop_preview = Config.Boolean(default=True)
			self.preview_speed = Config.Int(default=150, limits=(1, 5000))
			super().__init__()

	def __init__(self) -> None:
		self.theme = Config.String()
		self.windows = PyICEConfig.Windows()
		self.last_path = PyICEConfig.LastPath()
		self.mpqs = Config.List(value_type=str)
		self.settings = PyICEConfig.Settings()
		self.find_history = Config.List(value_type=str)
		self.code = PyICEConfig.Code()
		self.generator = PyICEConfig.Generator()
		self.sounds = PyICEConfig.Sounds()
		self.previewer = PyICEConfig.Previewer()
		super().__init__()
