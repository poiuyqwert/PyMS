
from ..Utilities import Config
from ..Utilities.UIKit import Size

class PyMODConfig(Config.Config):
	_name = 'PyMOD'
	_version = 1

	class Windows(Config.Group):
		class Settings(Config.Group):
			def __init__(self) -> None:
				self.main = Config.WindowGeometry(default_size=Size(550,380))
				self.mpq_select = Config.WindowGeometry()
				super().__init__()

		def __init__(self) -> None:
			self.main = Config.WindowGeometry()
			self.help = Config.WindowGeometry()
			self.settings = PyMODConfig.Windows.Settings()
			self.extract = Config.WindowGeometry()
			super().__init__()

	class LastPath(Config.Group):
		def __init__(self) -> None:
			self.project = Config.SelectDirectory(title='Open Project Directory')
			super().__init__()

	class Extract(Config.Group):
		def __init__(self) -> None:
			self.history = Config.List(value_type=str)
			super().__init__()

	def __init__(self) -> None:
		self.theme = Config.String()
		self.windows = PyMODConfig.Windows()
		self.last_path = PyMODConfig.LastPath()
		self.mpqs = Config.List(value_type=str)
		self.extract = PyMODConfig.Extract()
		super().__init__()
