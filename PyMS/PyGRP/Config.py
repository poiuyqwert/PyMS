
from .utils import BMPStyle

from ..Utilities import Config
from ..Utilities.UIKit import Size, FileType

def _migrate_1_to_2(data: dict) -> None:
	Config.migrate_fields(data, (
		(('lastpath',), ('last_path',)),
		(('transid',), ('transparent_index',)),
		(('window',), ('windows',)),
		(('preview', 'bgcolor'), ('preview', 'bg_color')),
		(('preview', 'grpoutline'), ('preview', 'outline', 'grp')),
		(('preview', 'frameoutline'), ('preview', 'outline', 'frame')),
		(('preview', 'bmpstyle'), ('preview', 'bmp_style')),
	))

class PyGRPConfig(Config.Config):
	_name = 'PyGRP'
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
			self.settings = PyGRPConfig.Windows.Settings()
			self.frames = Config.WindowGeometry()
			super().__init__()

	class LastPath(Config.Group):
		def __init__(self) -> None:
			self.grp = Config.SelectFile(name='GRP', filetypes=[FileType.grp()])
			self.bmp = Config.SelectFile(name='BMP', filetypes=[FileType.bmp()], op_type=Config.FileOpType.import_export)
			super().__init__()

	class Preview(Config.Group):
		class Outline(Config.Group):
			def __init__(self) -> None:
				self.grp = Config.Boolean(default=True)
				self.frame = Config.Boolean(default=True)
				super().__init__()

		def __init__(self) -> None:
			self.palette = Config.String(default='Units.pal')
			self.bg_color = Config.Color(default='#000000')
			self.speed = Config.Int(default=150, limits=(1, 5000))
			self.show = Config.Boolean(default=True)
			self.loop = Config.Boolean(default=True)
			self.outline = PyGRPConfig.Preview.Outline()
			super().__init__()

	def __init__(self) -> None:
		self.theme = Config.String()
		self.windows = PyGRPConfig.Windows()
		self.last_path = PyGRPConfig.LastPath()
		self.hex = Config.Boolean(default=False)
		self.preview = PyGRPConfig.Preview()
		self.transparent_index = Config.Int(default=0, limits=(0, 255))
		self.bmp_style = Config.Enum(enum_type=BMPStyle, default=BMPStyle.single_bmp_framesets)
		self.uncompressed = Config.Boolean(default=False)
		super().__init__()
