
from ..Utilities import Config
from ..Utilities.UIKit import Size, FileType

def _migrate_1_to_2(data: dict) -> None:
	Config.migrate_fields(data, (
		(('lastpath',), ('last_path',)),
		(('windows', 'edit', 'smk'), ('windows', 'edit', 'smk', 'main'))
	))

class PyBINConfig(Config.Config):
	_name = 'PyBIN'
	_version = 2
	_migrations = {
		1: _migrate_1_to_2
	}

	class Windows(Config.Group):
		class Settings(Config.Group):
			def __init__(self) -> None:
				self.main = Config.WindowGeometry(default_size=Size(550,430))
				self.mpq_select = Config.WindowGeometry()
				super().__init__()

		class Edit(Config.Group):
			class SMK(Config.Group):
				def __init__(self) -> None:
					self.main = Config.WindowGeometry()
					self.mpq_select = Config.WindowGeometry()
					super().__init__()

			def __init__(self) -> None:
				self.widget = Config.WindowGeometry()
				self.smk = PyBINConfig.Windows.Edit.SMK()
				super().__init__()

		def __init__(self) -> None:
			self.main = Config.WindowGeometry()
			self.help = Config.WindowGeometry()
			self.settings = PyBINConfig.Windows.Settings()
			self.edit = PyBINConfig.Windows.Edit()
			super().__init__()

	class LastPath(Config.Group):
		def __init__(self) -> None:
			self.bin = Config.SelectFile(name='Dialog BIN', filetypes=[FileType.bin_dialog()])
			self.txt = Config.SelectFile(name='TXT', filetypes=[FileType.txt()], op_type=Config.FileOpType.import_export)
			super().__init__()

	class Settings(Config.Group):
		class Files(Config.Group):
			def __init__(self) -> None:
				self.tfontgam = Config.File(default='MPQ:game\\tfontgam.pcx', name='tfontgam.pcx', filetypes=[FileType.pcx()])
				self.font10 = Config.File(default='MPQ:font\\font10.fnt', name='font10.fnt', filetypes=[FileType.fnt()])
				self.font14 = Config.File(default='MPQ:font\\font14.fnt', name='font14.fnt', filetypes=[FileType.fnt()])
				self.font16 = Config.File(default='MPQ:font\\font16.fnt', name='font16.fnt', filetypes=[FileType.fnt()])
				self.font16x = Config.File(default='MPQ:font\\font16x.fnt', name='font16x.fnt', filetypes=[FileType.fnt()])
				super().__init__()

		class LastPath(Config.Group):
			def __init__(self) -> None:
				self.mpqs = Config.SelectFile(name='MPQ', filetypes=[FileType.mpq_all(),FileType.mpq(),FileType.exe_mpq(),FileType.scm(),FileType.scx()])
				super().__init__()

		def __init__(self) -> None:
			self.files = PyBINConfig.Settings.Files()
			self.mpq_select_history = Config.List(value_type=str)
			self.mpqs = Config.List(value_type=str)
			self.last_path = PyBINConfig.Settings.LastPath()
			super().__init__()

	class Preview(Config.Group):
		def __init__(self) -> None:
			self.theme_id = Config.Int(default=-1)
			self.show_settings = Config.Boolean(default=True)
			self.show_images = Config.Boolean(default=True)
			self.show_text = Config.Boolean(default=True)
			self.show_smks = Config.Boolean(default=True)
			self.show_hidden = Config.Boolean(default=True)
			self.show_dialog = Config.Boolean(default=False)
			self.show_animated = Config.Boolean(default=False)
			self.show_hover_smks = Config.Boolean(default=False)
			self.show_background = Config.Boolean(default=False)
			self.show_bounds_widget = Config.Boolean(default=True)
			self.show_bounds_group = Config.Boolean(default=True)
			self.show_bounds_text = Config.Boolean(default=True)
			self.show_bounds_responsive = Config.Boolean(default=True)
			super().__init__()

	class Edit(Config.Group):
		class Widget(Config.Group):
			def __init__(self) -> None:
				self.advanced = Config.Boolean(default=False)
				super().__init__()

		class SMK(Config.Group):
			def __init__(self) -> None:
				self.mpq_select_history = Config.List(value_type=str)
				super().__init__()
		
		def __init__(self) -> None:
			self.widget = PyBINConfig.Edit.Widget()
			self.smk = PyBINConfig.Edit.SMK()
			super().__init__()

	def __init__(self) -> None:
		self.theme = Config.String()
		self.windows = PyBINConfig.Windows()
		self.last_path = PyBINConfig.LastPath()
		self.mpqs = Config.List(value_type=str)
		self.settings = PyBINConfig.Settings()
		self.preview = PyBINConfig.Preview()
		self.edit = PyBINConfig.Edit()
		super().__init__()
