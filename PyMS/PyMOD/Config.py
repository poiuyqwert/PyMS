
from ..Utilities import Config
from ..Utilities import UIKit as UI

def _migrate_1_to_2(data: dict) -> None:
	Config.migrate_fields(data, (
		(('mpqs',), ('settings', 'mpqs')),
	))

class PyMODConfig(Config.Config):
	_name = 'PyMOD'
	_version = 2
	_migrations = {
		1: _migrate_1_to_2
	}

	class Windows(Config.Group):
		class Extractors(Config.Group):
			def __init__(self) -> None:
				self.default = Config.WindowGeometry()
				super().__init__()

		class Settings(Config.Group):
			def __init__(self) -> None:
				self.main = Config.WindowGeometry(default_size=UI.Size(550,380))
				self.mpq_select = Config.WindowGeometry()
				super().__init__()

		def __init__(self) -> None:
			self.main = Config.WindowGeometry()
			self.help = Config.WindowGeometry()
			self.settings = PyMODConfig.Windows.Settings()
			self.extract = Config.WindowGeometry()
			self.extractors = PyMODConfig.Windows.Extractors()
			self.name = Config.WindowGeometry()
			super().__init__()

	class LastPath(Config.Group):
		def __init__(self) -> None:
			self.project = Config.SelectDirectory(title='Open Project Directory')
			super().__init__()

	class Extract(Config.Group):
		def __init__(self) -> None:
			self.history = Config.List(value_type=str)
			super().__init__()

	class Settings(Config.Group):
		class LastPath(Config.Group):
			def __init__(self) -> None:
				self.mpqs = Config.SelectFile(name='MPQ', filetypes=[UI.FileType.mpq_all(),UI.FileType.mpq(),UI.FileType.exe_mpq(),UI.FileType.scm(),UI.FileType.scx()])
				super().__init__()

		def __init__(self) -> None:
			self.mpqs = Config.List(value_type=str)
			self.last_path = PyMODConfig.Settings.LastPath()
			super().__init__()

	def __init__(self) -> None:
		self.theme = Config.String()
		self.windows = PyMODConfig.Windows()
		self.last_path = PyMODConfig.LastPath()
		self.settings = PyMODConfig.Settings()
		self.extract = PyMODConfig.Extract()
		super().__init__()
