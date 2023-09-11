
from ..Utilities import Config
from ..Utilities.UIKit import Size, FileType

def _migrate_1_to_2(data: dict) -> None:
	Config.migrate_fields(data, (
		(('lastpath',), ('last_path',)),
		(('windows', 'findreplace'), ('windows', 'find_replace')),
		(('windows', 'mpqselect'), ('windows', 'mpq_select')),
		(('mpqselecthistory',), ('mpq_select_history',)),
		(('settings', 'lastpath'), ('settings', 'last_path'))
	))

class PyTRGConfig(Config.Config):
	_name = 'PyTRG'
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
			self.find_replace = Config.WindowGeometry()
			self.colors = Config.WindowGeometry()
			self.help = Config.WindowGeometry()
			self.settings = PyTRGConfig.Windows.Settings()

	class LastPath(Config.Group):
		def __init__(self) -> None:
			super().__init__()
			self.trg = Config.SelectFile(name='TRG', filetypes=[FileType.trg()])
			self.txt = Config.SelectFile(name='TXT', filetypes=[FileType.txt()], op_type=Config.FileOpType.import_export)
			# self.pal = Config.SelectFile(name='Palette', filetypes=list(Palette.FileType.load_types()))

	class Settings(Config.Group):
		class Files(Config.Group):
			def __init__(self) -> None:
				super().__init__()
				self.stat_txt = Config.File(default='MPQ:rez\\stat_txt.tbl', name='TBL', filetypes=[FileType.tbl()])
				self.aiscript = Config.File(default='MPQ:scripts\\aiscript.bin', name='aiscript.bin', filetypes=[FileType.bin_ai()])
		
		class LastPath(Config.Group):
			def __init__(self) -> None:
				super().__init__()
				self.mpqs = Config.SelectFiles(title="Add MPQ's", filetypes=[FileType.mpq_all(),FileType.mpq(),FileType.exe_mpq(),FileType.scm(),FileType.scx()])

		def __init__(self) -> None:
			super().__init__()
			self.files = PyTRGConfig.Settings.Files()
			self.mpq_select_history = Config.List(value_type=str)
			self.mpqs = Config.List(value_type=str)
			self.last_path = PyTRGConfig.Settings.LastPath()

	def __init__(self) -> None:
		super().__init__()
		self.theme = Config.String()
		self.windows = PyTRGConfig.Windows()
		self.last_path = PyTRGConfig.LastPath()
		self.highlights = Config.Dictionary(value_type=dict)
		self.mpqs = Config.List(value_type=str)
		self.settings = PyTRGConfig.Settings()
