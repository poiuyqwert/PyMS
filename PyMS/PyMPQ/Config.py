
from .CompressionSetting import CompressionOption

from ..Utilities import Config
from ..Utilities import Assets
from ..Utilities.UIKit import FileType, Size

def _migrate_2_to_3(data: dict) -> None:
	Config.migrate_fields(data, (
		(('filters',), ('filter', 'history')),
		(('regex',), ('filter', 'regex')),
		(('lastpath',), ('last_path',)),
		(('lastpath','files','import'), ('last_path','import','files','import')),
		(('lastpath','files','export'), ('last_path','import','files','export')),
		(('lastpath','files','import_dir'), ('last_path','import','folder')),
		(('import','add_folder'), ('import','folder_prefix'))
	))

class PyMPQConfig(Config.Config):
	_name = 'PyMPQ'
	_version = 3
	_migrations = {
		2: _migrate_2_to_3
	}

	class Windows(Config.Group):
		class Settings(Config.Group):
			def __init__(self) -> None:
				super().__init__()
				self.main = Config.WindowGeometry(default_size=Size(550,380))

		def __init__(self) -> None:
			super().__init__()
			self.main = Config.WindowGeometry(default_size=Size(700,500))
			self.help = Config.WindowGeometry()
			self.settings = PyMPQConfig.Windows.Settings()

	class Sort(Config.Group):
		def __init__(self) -> None:
			super().__init__()
			self.ascending = Config.Boolean(default=False)
			self.column = Config.Int(default=0, limits=(0,6))

	class Settings(Config.Group):
		class Defaults(Config.Group):
			def __init__(self) -> None:
				super().__init__()
				self.maxfiles = Config.Int(default=1024, limits=(1,65535))
				self.blocksize = Config.Int(default=3, limits=(1,23))

		class LastPath(Config.Group):
			def __init__(self) -> None:
				super().__init__()
				self.listfiles = Config.SelectFiles(title='Add Listfiles', filetypes=[FileType.txt()])

		def __init__(self) -> None:
			super().__init__()
			self.defaults = PyMPQConfig.Settings.Defaults()
			self.autocompression = Config.Dictionary(str, {
				'Default': str(CompressionOption.Standard.setting()),
				'.smk': str(CompressionOption.NoCompression.setting()),
				'.mpq': str(CompressionOption.NoCompression.setting()),
				'.wav': str(CompressionOption.Audio.setting(level=1))
			})
			self.listfiles = Config.List(str, [Assets.data_file_path('Listfile.txt')])
			self.last_path = PyMPQConfig.Settings.LastPath()

	class Filter(Config.Group):
		def __init__(self) -> None:
			super().__init__()
			self.history = Config.List(str)
			self.regex = Config.Boolean(default=False)

	class LastPath(Config.Group):
		class Import(Config.Group):
			def __init__(self) -> None:
				super().__init__()
				self.files = Config.SelectFiles(title='Add files...', filetypes=[FileType.all_files()])
				self.folder = Config.SelectDirectory(title='Add files from folder...')

		def __init__(self) -> None:
			super().__init__()
			self.import_ = PyMPQConfig.LastPath.Import()
			self.export = Config.SelectDirectory(title='Extract files...')
			self.mpq = Config.SelectFile(name='MPQ', filetypes=[FileType.mpq_all(),FileType.mpq(),FileType.exe_mpq(),FileType.scm(),FileType.scx()])

	class Import(Config.Group):
		def __init__(self) -> None:
			super().__init__()
			self.files_prefix = Config.String()
			self.folder_prefix = Config.String()

	def __init__(self):
		super().__init__()
		self.compression = Config.String(default=str(CompressionOption.Auto.setting()))
		self.encrypt = Config.Boolean(default=False)
		self.locale = Config.Int(default=0, limits=(0,65535))
		self.sort = PyMPQConfig.Sort()
		self.settings = PyMPQConfig.Settings()
		self.list_sizes = Config.PaneSizes(defaults=(317,74,45,67,52,64))
		self.filter = PyMPQConfig.Filter()
		self.theme = Config.String()
		self.windows = PyMPQConfig.Windows()
		self.last_path = PyMPQConfig.LastPath()
		self.import_ = PyMPQConfig.Import()
