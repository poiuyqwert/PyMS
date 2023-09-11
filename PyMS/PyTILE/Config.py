
from .MegaEditorMode import MegaEditorMode
from .RepeaterID import RepeaterID

from ..Utilities import Config
from ..Utilities import Assets
from ..Utilities.UIKit import Size, FileType

def _migrate_1_to_2(data: dict) -> None:
	Config.migrate_fields(data, (
		(('lastpath',), ('last_path',)),
	))

class PyTILEConfig(Config.Config):
	_name = 'PyTILE'
	_version = 2
	_migrations = {
		1: _migrate_1_to_2
	}

	class Windows(Config.Group):
		class Settings(Config.Group):
			def __init__(self) -> None:
				super().__init__()
				self.main = Config.WindowGeometry(default_size=Size(550,380))
				self.mpq_select = Config.WindowGeometry()

		class Import(Config.Group):
			class Graphics(Config.Group):
				def __init__(self) -> None:
					super().__init__()
					self.group = Config.WindowGeometry()
					self.mega = Config.WindowGeometry()
					self.mini = Config.WindowGeometry()
			def __init__(self) -> None:
				super().__init__() 
				self.graphics = PyTILEConfig.Windows.Import.Graphics()

		class Palette(Config.Group):
			def __init__(self) -> None:
				super().__init__()
				self.group = Config.WindowGeometry()
				self.mega = Config.WindowGeometry()
				self.mini = Config.WindowGeometry()

		def __init__(self) -> None:
			super().__init__()
			self.main = Config.WindowGeometry()
			self.help = Config.WindowGeometry()
			self.settings = PyTILEConfig.Windows.Settings()
			self.import_ = PyTILEConfig.Windows.Import()
			self.palette = PyTILEConfig.Windows.Palette()

	class LastPath(Config.Group):
		def __init__(self) -> None:
			super().__init__()
			self.tbl = Config.SelectFile(name='TBL', filetypes=[FileType.tbl()], op_type=Config.FileOpType.import_export)
			self.tileset = Config.SelectFile(name='Complete Tileset', filetypes=[FileType.cv5()])
			self.graphics = Config.SelectFile(name='Graphics', filetypes=[FileType.bmp()])
			self.settings = Config.SelectFile(name='Settings', filetypes=[FileType.txt()], op_type=Config.FileOpType.import_export)

	class Settings(Config.Group):
		class Files(Config.Group):
			def __init__(self) -> None:
				super().__init__()
				self.stat_txt = Config.File(default=Assets.mpq_file_path('rez', 'stat_txt.tbl'), name='TBL', filetypes=[FileType.tbl()])

		class LastPath(Config.Group):
			def __init__(self) -> None:
				super().__init__()
				self.mpqs = Config.SelectFiles(title="Add MPQ's", filetypes=[FileType.mpq_all(),FileType.mpq(),FileType.exe_mpq(),FileType.scm(),FileType.scx()])

		def __init__(self) -> None:
			super().__init__()
			self.files = PyTILEConfig.Settings.Files()
			self.mpq_select_history = Config.List(value_type=str)
			self.mpqs = Config.List(value_type=str)
			self.last_path = PyTILEConfig.Settings.LastPath()

	class MegaEdit(Config.Group):
		def __init__(self) -> None:
			super().__init__()
			self.apply_all_exclude_nulls = Config.Boolean(default=True)
			self.mode = Config.Enum(enum_type=MegaEditorMode, default=MegaEditorMode.mini)
			self.height = Config.Int(default=1, limits=(0,2))

	class Copy(Config.Group):
		class Mega(Config.Group):
			def __init__(self) -> None:
				super().__init__()
				self.height = Config.Boolean(default=True)
				self.walkable = Config.Boolean(default=True)
				self.sight = Config.Boolean(default=True)
				self.ramp = Config.Boolean(default=True)
		class TileGroup(Config.Group):
			def __init__(self) -> None:
				super().__init__()
				self.walkability = Config.Boolean(default=True)
				self.buildability = Config.Boolean(default=True)
				self.creep = Config.Boolean(default=True)
				self.height = Config.Boolean(default=True)
				self.misc = Config.Boolean(default=True)
				self.unknown = Config.Boolean(default=True)
				self.edge_types = Config.Boolean(default=True)
				self.piece_types = Config.Boolean(default=True)
				self.group_type = Config.Boolean(default=True)
		class DoodadGroup(Config.Group):
			def __init__(self) -> None:
				super().__init__()
				self.doodad = Config.Boolean(default=True)
				self.overlay = Config.Boolean(default=True)
				self.walkability = Config.Boolean(default=True)
				self.buildability = Config.Boolean(default=True)
				self.creep = Config.Boolean(default=True)
				self.height = Config.Boolean(default=True)
				self.misc = Config.Boolean(default=True)
				self.unknown = Config.Boolean(default=True)
				self.scr = Config.Boolean(default=True)
				self.name = Config.Boolean(default=True)

		def __init__(self) -> None:
			super().__init__()
			self.mega = PyTILEConfig.Copy.Mega()
			self.tilegroup = PyTILEConfig.Copy.TileGroup()
			self.doodadgroup = PyTILEConfig.Copy.DoodadGroup()

	class DontWarn(Config.Group):
		def __init__(self) -> None:
			super().__init__()
			self.expanded_vx4 = Config.Warning(message="This tileset is using an expanded vx4 file (vx4ex). This could be a Remastered tileset, and/or will require a 'VX4 Expander Plugin' for pre-Remastered.")

	class Import(Config.Group):
		class Graphics(Config.Group):
			class MiniSettings(Config.Group):
				def __init__(self) -> None:
					super().__init__()
					self.minitiles_reuse_duplicates_old = Config.Boolean(default=True)
					self.minitiles_reuse_duplicates_new = Config.Boolean(default=True)
					self.minitiles_reuse_null = Config.Boolean(default=True)
					self.minitiles_null_id = Config.Int(default=0)
					self.replace_selections = Config.Boolean(default=True)
					self.auto_close = Config.Boolean(default=True)
			
			class MegaSettings(MiniSettings):
				def __init__(self) -> None:
					super().__init__()
					self.megatiles_reuse_duplicates_old = Config.Boolean(default=False)
					self.megatiles_reuse_duplicates_new = Config.Boolean(default=False)
					self.megatiles_reuse_null = Config.Boolean(default=True)
					self.megatiles_null_id = Config.Int(default=0)

			def __init__(self) -> None:
				super().__init__()
				self.group = PyTILEConfig.Import.Graphics.MegaSettings()
				self.mega = PyTILEConfig.Import.Graphics.MegaSettings()
				self.mini = PyTILEConfig.Import.Graphics.MiniSettings()

		class Settings(Config.Group):
			def __init__(self) -> None:
				super().__init__()
				self.repeater = Config.Enum(enum_type=RepeaterID, default=RepeaterID.repeat_all)
				self.auto_close = Config.Boolean(default=True)

		def __init__(self) -> None:
			super().__init__()
			self.graphics = PyTILEConfig.Import.Graphics()
			self.settings = PyTILEConfig.Import.Settings()

	class Export(Config.Group):
		class MegaTiles(Config.Group):
			def __init__(self) -> None:
				super().__init__()
				self.height = Config.Boolean(default=True)
				self.walkability = Config.Boolean(default=True)
				self.block_sight = Config.Boolean(default=True)
				self.ramp = Config.Boolean(default=True)
		
		def __init__(self) -> None:
			super().__init__()
			self.megatiles = PyTILEConfig.Export.MegaTiles()

	def __init__(self) -> None:
		super().__init__()
		self.theme = Config.String()
		self.windows = PyTILEConfig.Windows()
		self.last_path = PyTILEConfig.LastPath()
		self.mpqs = Config.List(value_type=str)
		self.settings = PyTILEConfig.Settings()
		self.mega_edit = PyTILEConfig.MegaEdit()
		self.copy = PyTILEConfig.Copy()
		self.dont_warn = PyTILEConfig.DontWarn()
		self.import_ = PyTILEConfig.Import()
		self.export = PyTILEConfig.Export()
