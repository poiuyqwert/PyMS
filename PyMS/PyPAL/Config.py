
from ..FileFormats.Palette import Palette

from ..Utilities import Config
from ..Utilities.UIKit import Size

def _migrate_1_to_2(data: dict) -> None:
	Config.migrate_fields(data, (
		(('lastpath',), ('last_path',)),
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
				self.main = Config.WindowGeometry(default_size=Size(550,380))
				super().__init__()

		def __init__(self) -> None:
			self.main = Config.WindowGeometry()
			self.help = Config.WindowGeometry()
			self.settings = PyPALConfig.Windows.Settings()
			super().__init__()

	class LastPath(Config.Group):
		def __init__(self) -> None:
			self.pal = Config.SelectFile(name='Palette', filetypes=list(Palette.FileType.load_types()))
			super().__init__()

	def __init__(self) -> None:
		self.theme = Config.String()
		self.windows = PyPALConfig.Windows()
		self.last_path = PyPALConfig.LastPath()
		super().__init__()
