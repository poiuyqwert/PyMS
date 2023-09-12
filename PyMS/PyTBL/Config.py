
from ..Utilities import Config
from ..Utilities.UIKit import Size, FileType
from ..Utilities import Assets

def _migrate_1_to_2(data: dict) -> None:
	Config.migrate_fields(data, (
		(('lastpath',), ('last_path',)),
		(('windows', 'mpqselect'), ('windows', 'mpq_select')),
		(('settings', 'mpqselecthistory',), ('settings', 'mpq_select_history',)),
		(('settings', 'files', 'unitpal'), ('settings', 'files', 'unit_pal')),
		(('panes', 'stringlist'), ('panes', 'string_list')),
		(('panes', 'colorlist'), ('panes', 'color_list')),
		(('preview', 'endatnull'), ('preview', 'end_at_null'))
	))

class PyTBLConfig(Config.Config):
	_name = 'PyTBL'
	_version = 2
	_migrations = {
		1: _migrate_1_to_2
	}

	class Windows(Config.Group):
		class Settings(Config.Group):
			def __init__(self) -> None:
				super().__init__()
				self.main = Config.WindowGeometry(default_size=Size(550,380))
				self.mpq_select = Config.WindowGeometry()

		def __init__(self) -> None:
			super().__init__()
			self.main = Config.WindowGeometry(default_size=Size(740, 400))
			self.find = Config.WindowGeometry()
			self.help = Config.WindowGeometry()
			self.settings = PyTBLConfig.Windows.Settings()
			self.goto = Config.WindowGeometry()

	class LastPath(Config.Group):
		def __init__(self) -> None:
			super().__init__()
			self.tbl = Config.SelectFile(name='TBL', filetypes=[FileType.tbl()])
			self.txt = Config.SelectFile(name='TXT', filetypes=[FileType.txt()], op_type=Config.FileOpType.import_export)

	class Settings(Config.Group):
		class Files(Config.Group):
			def __init__(self) -> None:
				super().__init__()
				self.tfontgam = Config.File(default='MPQ:game\\tfontgam.pcx', name='tfontgam.pcx', filetypes=[FileType.pcx()])
				self.font8 = Config.File(default='MPQ:font\\font8.fnt', name='font8.fnt', filetypes=[FileType.fnt()])
				self.font10 = Config.File(default='MPQ:font\\font10.fnt', name='font10.fnt', filetypes=[FileType.fnt()])
				self.icons = Config.File(default='MPQ:game\\icons.grp', name='icons.grp', filetypes=[FileType.grp()])
				self.unit_pal = Config.File(default=Assets.palette_file_path('Units.pal'), name='Unit Palette', filetypes=[FileType.pal()])
		
		class LastPath(Config.Group):
			def __init__(self) -> None:
				super().__init__()
				self.mpqs = Config.SelectFiles(title="Add MPQ's", filetypes=[FileType.mpq_all(),FileType.mpq(),FileType.exe_mpq(),FileType.scm(),FileType.scx()])

		def __init__(self) -> None:
			super().__init__()
			self.files = PyTBLConfig.Settings.Files()
			self.mpq_select_history = Config.List(value_type=str)
			self.mpqs = Config.List(value_type=str)
			self.last_path = PyTBLConfig.Settings.LastPath()

	class Panes(Config.Group):
		def __init__(self) -> None:
			super().__init__()
			self.string_list = Config.PaneSizes()
			self.color_list = Config.PaneSizes()

	class Preview(Config.Group):
		def __init__(self) -> None:
			super().__init__()
			self.hotkey = Config.Boolean(default=True)
			self.end_at_null = Config.Boolean(default=True)

	def __init__(self) -> None:
		super().__init__()
		self.theme = Config.String()
		self.windows = PyTBLConfig.Windows()
		self.last_path = PyTBLConfig.LastPath()
		self.mpqs = Config.List(value_type=str)
		self.settings = PyTBLConfig.Settings()
		self.panes = PyTBLConfig.Panes()
		self.preview = PyTBLConfig.Preview()
