
from ..Utilities import Config
from ..Utilities.UIKit import Size, FileType
from ..Utilities import Assets

def _migrate_1_to_2(data: dict) -> None:
	Config.migrate_fields(data, (
		(('lastpath',), ('last_path',)),
		(('windows', 'mpqselect'), ('windows', 'mpq_select')),
		(('settings', 'mpqselecthistory',), ('settings', 'mpq_select_history',)),
		(('settings', 'files', 'basegrp'), ('settings', 'files', 'base_grp')),
		(('settings', 'files', 'overlaygrp'), ('settings', 'files', 'overlay_grp')),
		(('usebasegrp',), ('preview', 'use_base_grp')),
		(('useoverlaygrp',), ('preview', 'use_overlay_grp')),
	))

class PyLOConfig(Config.Config):
	_name = 'PyLO'
	_version = 2
	_migrations = {
		1: _migrate_1_to_2
	}

	class Windows(Config.Group):
		class Settings(Config.Group):
			def __init__(self) -> None:
				self.main = Config.WindowGeometry(default_size=Size(550,380))
				self.mpq_select = Config.WindowGeometry()
				super().__init__()

		def __init__(self) -> None:
			self.main = Config.WindowGeometry(default_size=Size(740, 400))
			self.find = Config.WindowGeometry()
			self.help = Config.WindowGeometry()
			self.settings = PyLOConfig.Windows.Settings()
			super().__init__()

	class LastPath(Config.Group):
		def __init__(self) -> None:
			self.lo = Config.SelectFile(name='LO', filetypes=[FileType.lo(),FileType.loa(),FileType.lob(),FileType.lod(),FileType.lof(),FileType.loo(),FileType.los(),FileType.lou(),FileType.log(),FileType.lol(),FileType.lox()])
			self.txt = Config.SelectFile(name='TXT', filetypes=[FileType.txt()], op_type=Config.FileOpType.import_export)
			super().__init__()

	class Settings(Config.Group):
		class Files(Config.Group):
			def __init__(self) -> None:
				self.base_grp = Config.File(default='MPQ:unit\\terran\\wessel.grp', name='Base GRP', filetypes=[FileType.grp()])
				self.overlay_grp = Config.File(default='MPQ:unit\\terran\\wesselt.grp', name='Overlay GRP', filetypes=[FileType.grp()])
				super().__init__()
		
		class LastPath(Config.Group):
			def __init__(self) -> None:
				self.mpqs = Config.SelectFile(name='MPQ', filetypes=[FileType.mpq_all(),FileType.mpq(),FileType.exe_mpq(),FileType.scm(),FileType.scx()])
				super().__init__()

		def __init__(self) -> None:
			self.files = PyLOConfig.Settings.Files()
			self.mpq_select_history = Config.List(value_type=str)
			self.mpqs = Config.List(value_type=str)
			self.last_path = PyLOConfig.Settings.LastPath()
			super().__init__()

	class Preview(Config.Group):
		def __init__(self) -> None:
			self.use_base_grp = Config.Boolean(default=True)
			self.use_overlay_grp = Config.Boolean(default=True)
			super().__init__()

	def __init__(self) -> None:
		self.theme = Config.String()
		self.windows = PyLOConfig.Windows()
		self.last_path = PyLOConfig.LastPath()
		self.highlights = Config.Highlights()
		self.mpqs = Config.List(value_type=str)
		self.settings = PyLOConfig.Settings()
		self.preview = PyLOConfig.Preview()
		super().__init__()
