
from ..FileFormats.Palette import Palette

from ..Utilities import Config
from ..Utilities.UIKit import Size

def _migrate_1_to_2(data: dict) -> None:
	Config.migrate_fields(data, (
		(('lastpath','open'), ('last_path','pal','open')),
		(('lastpath','save'), ('last_path','pal','save')),
	))

class PyPALConfig(Config.Config):
	_name = 'PyPAL'
	_version = 2
	_migrations = {
		1: _migrate_1_to_2
	}

	class Windows(Config.Group):
		class Settings(Config.Group):
			def __init__(self) -> None:
				super().__init__()
				self.main = Config.WindowGeometry(default_size=Size(550,380))

		def __init__(self) -> None:
			super().__init__()
			self.main = Config.WindowGeometry()
			self.help = Config.WindowGeometry()
			self.settings = PyPALConfig.Windows.Settings()

	class LastPath(Config.Group):
		def __init__(self) -> None:
			super().__init__()
			self.pal = Config.SelectFile(name='Palette', filetypes=list(Palette.FileType.load_types()))

	def __init__(self) -> None:
		super().__init__()
		self.theme = Config.String()
		self.windows = PyPALConfig.Windows()
		self.last_path = PyPALConfig.LastPath()
