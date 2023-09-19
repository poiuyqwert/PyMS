
from ..Utilities import Config
from ..Utilities.UIKit import Size, FileType

def _migrate_1_to_2(data: dict) -> None:
	Config.migrate_fields(data, (
		(('lastpath',), ('last_path',)),
	))

class PyFNTConfig(Config.Config):
	_name = 'PyFNT'
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
			self.main = Config.WindowGeometry()
			self.help = Config.WindowGeometry()
			self.settings = PyFNTConfig.Windows.Settings()
			super().__init__()

	class LastPath(Config.Group):
		def __init__(self) -> None:
			self.fnt = Config.SelectFile(name='FNT', filetypes=[FileType.fnt()])
			self.bmp = Config.SelectFile(name='BMP', filetypes=[FileType.bmp()], op_type=Config.FileOpType.import_export)
			super().__init__()

	class Settings(Config.Group):
		class Files(Config.Group):
			def __init__(self) -> None:
				self.tfontgam = Config.File(default='MPQ:game\\tfontgam.pcx', name='tfontgam.pcx', filetypes=[FileType.pcx()])
				super().__init__()

		class LastPath(Config.Group):
			def __init__(self) -> None:
				self.mpqs = Config.SelectFile(name='MPQ', filetypes=[FileType.mpq_all(),FileType.mpq(),FileType.exe_mpq(),FileType.scm(),FileType.scx()])
				super().__init__()

		def __init__(self) -> None:
			self.files = PyFNTConfig.Settings.Files()
			self.mpq_select_history = Config.List(value_type=str)
			self.mpqs = Config.List(value_type=str)
			self.last_path = PyFNTConfig.Settings.LastPath()
			super().__init__()

	def __init__(self) -> None:
		self.theme = Config.String()
		self.windows = PyFNTConfig.Windows()
		self.last_path = PyFNTConfig.LastPath()
		self.mpqs = Config.List(value_type=str)
		self.settings = PyFNTConfig.Settings()
		super().__init__()
