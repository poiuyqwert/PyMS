
from ..Utilities import Config
from ..Utilities import UIKit as UI
from ..Utilities import Assets

class PyGRAFTConfig(Config.Config):
	_name = 'PyGRAFT'
	_version = 1

	class Windows(Config.Group):
		class Settings(Config.Group):
			def __init__(self) -> None:
				self.main = Config.WindowGeometry(default_size=UI.Size(550,430))
				self.mpq_select = Config.WindowGeometry()
				super().__init__()

		def __init__(self) -> None:
			self.main = Config.WindowGeometry()
			self.help = Config.WindowGeometry()
			self.find_replace = Config.WindowGeometry()
			self.icon_select = Config.WindowGeometry()
			self.settings = PyGRAFTConfig.Windows.Settings()
			super().__init__()

	class LastPath(Config.Group):
		def __init__(self) -> None:
			self.graft = Config.SelectFile(name='Graft', filetypes=[UI.FileType.graft()])
			self.txt = Config.SelectFile(name='TXT', filetypes=[UI.FileType.txt()], op_type=Config.FileOpType.import_export)
			self.fgp = Config.SelectFile(name='FireGraft Project', filetypes=[UI.FileType.fgp()], op_type=Config.FileOpType.import_export)
			self.mpq = Config.SelectFile(name='MPQ', filetypes=[UI.FileType.mpq(),UI.FileType.exe_mpq()])
			self.dir = Config.SelectDirectory(title='Open Directory')
			self.highlights = Config.SelectFile(name='Syntax Highlighting', filetypes=[UI.FileType.json()], op_type=Config.FileOpType.import_export)
			super().__init__()

	class Settings(Config.Group):
		class Files(Config.Group):
			class DAT(Config.Group):
				def __init__(self) -> None:
					self.units = Config.File(default=Assets.mpq_file_ref('arr', 'units.dat'), name='units.dat', filetypes=[UI.FileType.dat()])
					self.upgrades = Config.File(default=Assets.mpq_file_ref('arr', 'upgrades.dat'), name='upgrades.dat', filetypes=[UI.FileType.dat()])
					self.techdata = Config.File(default=Assets.mpq_file_ref('arr', 'techdata.dat'), name='techdata.dat', filetypes=[UI.FileType.dat()])
					self.orders = Config.File(default=Assets.mpq_file_ref('arr', 'orders.dat'), name='orders.dat', filetypes=[UI.FileType.dat()])
					super().__init__()

			def __init__(self) -> None:
				self.dat = PyGRAFTConfig.Settings.Files.DAT()
				self.stat_txt = Config.File(default=Assets.mpq_file_ref('rez', 'stat_txt.tbl'), name='stat_txt.tbl', filetypes=[UI.FileType.tbl()])
				self.unitnames = Config.File(default=Assets.mpq_file_ref('rez', 'unitnames.tbl'), name='unitnames.tbl', filetypes=[UI.FileType.tbl()])
				self.cmdicons = Config.File(default=Assets.mpq_file_ref('unit', 'cmdbtns', 'cmdicons.grp'), name='cmdicons.grp', filetypes=[UI.FileType.grp()])
				self.ticon = Config.File(default=Assets.mpq_file_ref('unit', 'cmdbtns', 'ticon.pcx'), name='ticon.pcx', filetypes=[UI.FileType.pal_pcx()])
				self.tfontgam = Config.File(default=Assets.mpq_file_ref('game', 'tfontgam.pcx'), name='tfontgam.pcx', filetypes=[UI.FileType.pcx()])
				self.font8 = Config.File(default=Assets.mpq_file_ref('font', 'font8.fnt'), name='font8.fnt', filetypes=[UI.FileType.fnt()])
				self.icons = Config.File(default=Assets.mpq_file_ref('game', 'icons.grp'), name='icons.grp', filetypes=[UI.FileType.grp()])
				self.unit_pal = Config.File(default=Assets.palette_file_path('Units.pal'), name='Unit Palette', filetypes=[UI.FileType.pal()])
				super().__init__()

		class LastPath(Config.Group):
			def __init__(self) -> None:
				self.mpqs = Config.SelectFile(name='MPQ', filetypes=[UI.FileType.mpq_all(),UI.FileType.mpq(),UI.FileType.exe_mpq(),UI.FileType.scm(),UI.FileType.scx()])
				super().__init__()

		def __init__(self) -> None:
			self.files = PyGRAFTConfig.Settings.Files()
			self.mpq_select_history = Config.List(value_type=str)
			self.mpqs = Config.List(value_type=str)
			self.last_path = PyGRAFTConfig.Settings.LastPath()
			super().__init__()

	class Code(Config.Group):
		class Highlights(Config.Group):
			def __init__(self) -> None:
				self.comment = Config.HighlightStyle(default=Config.Style(foreground='#008000'))
				self.string = Config.HighlightStyle(default=Config.Style(foreground='#A31515'))
				self.command = Config.HighlightStyle(default=Config.Style(foreground='#0000AA'))
				self.keyword = Config.HighlightStyle(default=Config.Style(foreground='#0000FF', bold=True))
				self.number = Config.HighlightStyle(default=Config.Style(foreground='#FF0000'))
				self.operator = Config.HighlightStyle(default=Config.Style(foreground='#0000FF', bold=True))
				self.newline = Config.HighlightStyle(default=Config.Style())
				self.selection = Config.HighlightStyle(default=Config.Style(background='#C0C0C0'))
				self.error = Config.HighlightStyle(default=Config.Style(background='#FF8C8C'))
				self.warning = Config.HighlightStyle(default=Config.Style(background='#FFC8C8'))
				super().__init__()

		def __init__(self) -> None:
			self.highlights = PyGRAFTConfig.Code.Highlights()
			super().__init__()

	def __init__(self) -> None:
		self.theme = Config.String()
		self.windows = PyGRAFTConfig.Windows()
		self.last_path = PyGRAFTConfig.LastPath()
		self.settings = PyGRAFTConfig.Settings()
		self.code = PyGRAFTConfig.Code()
		self.list_size = Config.PaneSizes(defaults=(300,))
		self.show_used_by = Config.Boolean(default=True)
		super().__init__()
