
from ..Utilities import Config
from ..Utilities.UIKit import Size, FileType
from ..Utilities import Assets

def _migrate_1_to_2(data: dict) -> None:
	Config.migrate_fields(data, (
		(('lastpath',), ('last_path',)),
		(('windows', 'mpqselect'), ('windows', 'mpq_select')),
		(('settings', 'mpqselecthistory',), ('settings', 'mpq_select_history',)),
		(('settings', 'files', 'platformwpe'), ('settings', 'files', 'platform_wpe')),
	))

class PySPKConfig(Config.Config):
	_name = 'PySPK'
	_version = 2
	_migrations = {
		1: _migrate_1_to_2
	}

	class Windows(Config.Group):
		class Settings(Config.Group):
			def __init__(self) -> None:
				super().__init__()
				self.main = Config.WindowGeometry(default_size=Size(550,430))
				self.mpq_select = Config.WindowGeometry()

		def __init__(self) -> None:
			super().__init__()
			self.main = Config.WindowGeometry(default_size=Size(740, 400))
			self.preview = Config.WindowGeometry()
			self.help = Config.WindowGeometry()
			self.settings = PySPKConfig.Windows.Settings()

	class LastPath(Config.Group):
		def __init__(self) -> None:
			super().__init__()
			self.spk = Config.SelectFile(name='Parallax SPK', filetypes=[FileType.spk()])
			self.bmp = Config.SelectFile(name='BMP', filetypes=[FileType.bmp()], op_type=Config.FileOpType.import_export)

	class Settings(Config.Group):
		class Files(Config.Group):
			def __init__(self) -> None:
				super().__init__()
				self.platform_wpe = Config.File(default='MPQ:tileset\\platform.wpe', name='platform.wpe', filetypes=[FileType.wpe()])

		class LastPath(Config.Group):
			def __init__(self) -> None:
				super().__init__()
				self.mpqs = Config.SelectFiles(title="Add MPQ's", filetypes=[FileType.mpq_all(),FileType.mpq(),FileType.exe_mpq(),FileType.scm(),FileType.scx()])

		def __init__(self) -> None:
			super().__init__()
			self.files = PySPKConfig.Settings.Files()
			self.mpq_select_history = Config.List(value_type=str)
			self.mpqs = Config.List(value_type=str)
			self.last_path = PySPKConfig.Settings.LastPath()

	class Auto(Config.Group):
		def __init__(self) -> None:
			super().__init__()
			self.visibility = Config.Boolean(default=False)
			self.lock = Config.Boolean(default=True)

	def __init__(self) -> None:
		super().__init__()
		self.theme = Config.String()
		self.windows = PySPKConfig.Windows()
		self.last_path = PySPKConfig.LastPath()
		self.mpqs = Config.List(value_type=str)
		self.settings = PySPKConfig.Settings()
		self.auto = PySPKConfig.Auto()
