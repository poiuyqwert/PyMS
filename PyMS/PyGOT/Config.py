
from ..Utilities import Config
from ..Utilities.UIKit import Size, FileType

def _migrate_1_to_2(data: dict) -> None:
	Config.migrate_fields(data, (
		(('lastpath',), ('last_path',)),
	))

class PyGOTConfig(Config.Config):
	_name = 'PyGOT'
	_version = 2
	_migrations = {
		1: _migrate_1_to_2
	}

	class Windows(Config.Group):
		class Settings(Config.Group):
			def __init__(self) -> None:
				self.main = Config.WindowGeometry(default_size=Size(550,380))
				super().__init__()

		def __init__(self) -> None:
			self.main = Config.WindowGeometry()
			self.help = Config.WindowGeometry()
			self.settings = PyGOTConfig.Windows.Settings()
			super().__init__()

	class LastPath(Config.Group):
		def __init__(self) -> None:
			self.got = Config.SelectFile(name='GOT', filetypes=[FileType.got()])
			self.txt = Config.SelectFile(name='TXT', filetypes=[FileType.txt()], op_type=Config.FileOpType.import_export)
			self.trg = Config.SelectFile(name='TRG', filetypes=[FileType.trg()])
			super().__init__()

	def __init__(self) -> None:
		self.theme = Config.String()
		self.windows = PyGOTConfig.Windows()
		self.last_path = PyGOTConfig.LastPath()
		super().__init__()
