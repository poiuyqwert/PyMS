
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
		
		class Find(Config.Group):
			def __init__(self) -> None:
				self.script = Config.WindowGeometry()
				self.string = Config.WindowGeometry()
				super().__init__()

		def __init__(self) -> None:
			self.main = Config.WindowGeometry()
			self.help = Config.WindowGeometry()
			self.settings = PyAIConfig.Windows.Settings()
			self.code_edit = Config.WindowGeometry()
			self.script_edit = Config.WindowGeometry()
			self.extdefs = Config.WindowGeometry()
			self.find = PyAIConfig.Windows.Find()
			self.list_import = Config.WindowGeometry()
			super().__init__()

	class DontWarn(Config.Group):
		def __init__(self) -> None:
			self.plugins = Config.Warning(message='These files use features that require a plugin.')
			super().__init__()

	class LastPath(Config.Group):
		class TXT(Config.Group):
			def __init__(self) -> None:
				self.ai = Config.SelectFile(name='AI TXT', filetypes=[FileType.txt()], op_type=Config.FileOpType.import_export)
				self.settings = Config.SelectFile(name='Settings TXT', filetypes=[FileType.txt()])
				self.extdefs = Config.SelectFile(name='External Definitions TXT', filetypes=[FileType.txt()], op_type=Config.FileOpType.import_export)
				self.import_ = Config.SelectFile(name='Imports', filetypes=[FileType.txt()])
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

		class Highlights(Config.Group):
			def __init__(self) -> None:
				self.comment = Config.HighlightStyle(default=Config.Style(foreground='#008000'))
				self.header = Config.HighlightStyle(default=Config.Style(foreground='#0000FF', bold=True))
				self.ai_id = Config.HighlightStyle(default=Config.Style(foreground='#FF00FF', bold=True))
				self.block = Config.HighlightStyle(default=Config.Style(foreground='#FF00FF'))
				self.command = Config.HighlightStyle(default=Config.Style(foreground='#0000AA'))
				self.aise_command = Config.HighlightStyle(default=Config.Style(foreground='#008080'))
				self.type = Config.HighlightStyle(default=Config.Style(foreground='#0000FF', bold=True))
				self.directive = Config.HighlightStyle(default=Config.Style(foreground='#FF6600'))
				self.number = Config.HighlightStyle(default=Config.Style(foreground='#FF0000'))
				self.tbl_format = Config.HighlightStyle(default=Config.Style(background='#E6E6E6'))
				self.operator = Config.HighlightStyle(default=Config.Style(foreground='#0000FF', bold=True))
				self.keyword = Config.HighlightStyle(default=Config.Style(foreground='#0000FF', bold=True))
				self.aise_keyword = Config.HighlightStyle(default=Config.Style(foreground='#0000FF', bold=True))
				self.newline = Config.HighlightStyle(default=Config.Style())
				self.selection = Config.HighlightStyle(default=Config.Style(background='#C0C0C0'))
				self.error = Config.HighlightStyle(default=Config.Style(background='#FF8C8C'))
				self.warning = Config.HighlightStyle(default=Config.Style(background='#FFC8C8'))
				super().__init__()

		def __init__(self) -> None:
			self.decomp_format = PyAIConfig.Code.DecompFormat()
			self.highlights = PyAIConfig.Code.Highlights()
			super().__init__()

	def __init__(self) -> None:
		self.theme = Config.String()
		self.windows = PyAIConfig.Windows()
		self.dont_warn = PyAIConfig.DontWarn()
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
