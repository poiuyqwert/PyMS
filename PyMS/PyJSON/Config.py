
from ..Utilities import Config
from ..Utilities.UIKit import Size, FileType

class PyJSONConfig(Config.Config):
	_name = 'PyJSON'
	_version = 1

	class Windows(Config.Group):
		class Settings(Config.Group):
			def __init__(self) -> None:
				self.main = Config.WindowGeometry(default_size=Size(550,380))
				super().__init__()

		def __init__(self) -> None:
			self.main = Config.WindowGeometry(default_size=Size(740, 400))
			self.help = Config.WindowGeometry()
			self.settings = PyJSONConfig.Windows.Settings()
			super().__init__()

	class LastPath(Config.Group):
		def __init__(self) -> None:
			self.json = Config.SelectFile(name='JSON', filetypes=[FileType.json()])
			super().__init__()

	class Panes(Config.Group):
		def __init__(self) -> None:
			self.list = Config.PaneSizes()
			super().__init__()

	def __init__(self) -> None:
		self.theme = Config.String()
		self.windows = PyJSONConfig.Windows()
		self.last_path = PyJSONConfig.LastPath()
		self.panes = PyJSONConfig.Panes()
		super().__init__()
