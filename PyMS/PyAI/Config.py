
from .Sort import SortBy
from .DecompilingFormat import BlockFormat, CommandFormat, CommentFormat

from ..Utilities import Config
from ..Utilities.UIKit import Size, FileType
from ..Utilities import Assets

def _migrate_1_to_2(data: dict) -> None:
	Config.migrate_fields(data, (
		(('lastpath',), ('last_path',)),
		(('lastpath', 'ai_txt'), ('last_path', 'txt', 'ai')),
		(('lastpath', 'set_txt'), ('last_path', 'txt', 'settings')),
		(('lastpath', 'def_txt'), ('last_path', 'txt', 'extdefs')),
		(('settings', 'files', 'unitsdat'), ('settings', 'files', 'dat', 'units')),
		(('settings', 'files', 'upgradesdat'), ('settings', 'files', 'dat', 'upgrades')),
		(('settings', 'files', 'techdatadat'), ('settings', 'files', 'dat', 'techdata')),
		(('undohistory',), ('max_undos',)),
		(('redohistory',), ('max_redos',)),
		(('windows', 'external_def'), ('windows', 'extdefs')),
		(('stat_txt',), ('settings', 'files', 'stat_txt')),
		(('highlights',), ('code', 'highlights')),
	))

class PyAIConfig(Config.Config):
	_name = 'PyAI'
	_version = 2
	_migrations = {
		1: _migrate_1_to_2
	}

	class Windows(Config.Group):
		class Settings(Config.Group):
			def __init__(self) -> None:
				self.main = Config.WindowGeometry(default_size=Size(550,430))
				self.mpq_select = Config.WindowGeometry()
				super().__init__()

		def __init__(self) -> None:
			self.main = Config.WindowGeometry()
			self.help = Config.WindowGeometry()
			self.settings = PyAIConfig.Windows.Settings()
			self.code_edit = Config.WindowGeometry()
			self.script_edit = Config.WindowGeometry()
			self.extdefs = Config.WindowGeometry()
			super().__init__()

	class LastPath(Config.Group):
		class TXT(Config.Group):
			def __init__(self) -> None:
				self.ai = Config.SelectFile(name='AI TXT', filetypes=[FileType.txt()], op_type=Config.FileOpType.import_export)
				self.settings = Config.SelectFile(name='Settings TXT', filetypes=[FileType.txt()])
				self.extdefs = Config.SelectFile(name='External Definitions TXT', filetypes=[FileType.txt()], op_type=Config.FileOpType.import_export)
				super().__init__()

		def __init__(self) -> None:
			self.bin = Config.SelectFile(name='AI .bin', filetypes=[FileType.bin_ai()])
			self.tbl = Config.SelectFile(name='stat_txt.tbl', filetypes=[FileType.tbl()])
			self.mpq = Config.SelectFile(name='MPQ', filetypes=[FileType.mpq(),FileType.exe_mpq()])
			self.txt = PyAIConfig.LastPath.TXT()
			super().__init__()

	class Settings(Config.Group):
		class Files(Config.Group):
			class DAT(Config.Group):
				def __init__(self) -> None:
					self.units = Config.File(default=Assets.mpq_file_path('arr', 'units.dat'), name='units.dat', filetypes=[FileType.dat()])
					self.upgrades = Config.File(default=Assets.mpq_file_path('arr', 'upgrades.dat'), name='upgrades.dat', filetypes=[FileType.dat()])
					self.techdata = Config.File(default=Assets.mpq_file_path('arr', 'techdata.dat'), name='techdata.dat', filetypes=[FileType.dat()])
					super().__init__()

			def __init__(self) -> None:
				self.dat = PyAIConfig.Settings.Files.DAT()
				self.stat_txt = Config.File(default=Assets.mpq_file_path('rez', 'stat_txt.tbl'), name='stat_txt.tbl', filetypes=[FileType.tbl()])
				super().__init__()

		class LastPath(Config.Group):
			def __init__(self) -> None:
				self.mpqs = Config.SelectFile(name='MPQ', filetypes=[FileType.mpq_all(),FileType.mpq(),FileType.exe_mpq(),FileType.scm(),FileType.scx()])
				super().__init__()

		def __init__(self) -> None:
			self.files = PyAIConfig.Settings.Files()
			self.mpq_select_history = Config.List(value_type=str)
			self.mpqs = Config.List(value_type=str)
			self.last_path = PyAIConfig.Settings.LastPath()
			super().__init__()

	class Code(Config.Group):
		class DecompFormat(Config.Group):
			def __init__(self) -> None:
				self.block = Config.Enum(enum_type=BlockFormat, default=BlockFormat.hyphens)
				self.command = Config.Enum(enum_type=CommandFormat, default=CommandFormat.parens)
				self.comment = Config.Enum(enum_type=CommentFormat, default=CommentFormat.hash)
				super().__init__()

		def __init__(self) -> None:
			self.decomp_format = PyAIConfig.Code.DecompFormat()
			self.highlights = Config.Highlights()
			super().__init__()

	def __init__(self) -> None:
		self.theme = Config.String()
		self.windows = PyAIConfig.Windows()
		self.last_path = PyAIConfig.LastPath()
		self.mpqs = Config.List(value_type=str)
		self.settings = PyAIConfig.Settings()
		self.imports = Config.List(value_type=str)
		self.extdefs = Config.List(value_type=str)
		self.reference = Config.Boolean(default=False)
		self.max_undos = Config.Int(default=10)
		self.max_redos = Config.Int(default=10)
		self.sort = Config.Enum(enum_type=SortBy, default=SortBy.file_order)
		self.code = PyAIConfig.Code()
		super().__init__()
