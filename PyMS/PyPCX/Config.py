
from ..FileFormats.Palette import Palette

from ..Utilities import Config
from ..Utilities.UIKit import Size, FileType

def _migrate_1_to_2(data: dict) -> None:
	Config.migrate_fields(data, (
		(('lastpath',), ('last_path',)),
		(('lastpath',), ('last_path',)),
	))

class PyPCXConfig(Config.Config):
	_name = 'PyPCX'
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
			self.main = Config.WindowGeometry(default_size=Size(600, 400))
			self.help = Config.WindowGeometry()
			self.settings = PyPCXConfig.Windows.Settings()
			super().__init__()

	class LastPath(Config.Group):
		def __init__(self) -> None:
			self.pcx = Config.SelectFile(name='PCX', filetypes=[FileType.pcx()])
			self.pal = Config.SelectFile(name='Palette', filetypes=list(Palette.FileType.load_types()), op_type=Config.FileOpType.import_export)
			self.bmp = Config.SelectFile(name='BMP', filetypes=[FileType.bmp()], op_type=Config.FileOpType.import_export)
			super().__init__()

	def __init__(self) -> None:
		self.theme = Config.String()
		self.windows = PyPCXConfig.Windows()
		self.last_path = PyPCXConfig.LastPath()
		super().__init__()
