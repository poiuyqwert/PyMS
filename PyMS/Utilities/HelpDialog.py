
from .UIKit import *
from .PyMSDialog import PyMSDialog
from .MarkdownView import MarkdownView
from . import Assets
from . import Config

class HelpDialog(PyMSDialog):
	def __init__(self, parent: Misc, window_geometry_config: Config.WindowGeometry, help_file_path: str | None = None) -> None:
		self.window_geometry_config = window_geometry_config
		self.initial_file_path = help_file_path
		PyMSDialog.__init__(self, parent, 'Help')

	def widgetize(self) -> Misc | None:
		self.treelist = TreeList(self, width=30)
		self.treelist.pack(side=LEFT, fill=Y)
		roots: list[tuple[Assets.HelpFolder | Assets.HelpFile, bool]] = list((folder,True) for folder in Assets.help_tree().folders)
		self.treelist.build(roots, lambda node: () if isinstance(node, Assets.HelpFile) else tuple((file,None) for file in node.files) + tuple((folder,True) for folder in node.folders), lambda node: node.name.replace('_', ' '))
		self.treelist.bind(WidgetEvent.Listbox.Select(), lambda *_: self.load_help_file())

		self.markdownview = MarkdownView(self, link_callback=self.load)
		self.markdownview.set_link_foreground(Theme.get_color('help', 'linkforeground', default='#6A5EFF'))
		self.markdownview.set_code_background(Theme.get_color('help', 'codebackground', default='#EEEEEE'))
		self.markdownview.pack(side=LEFT, fill=BOTH, expand=1)
		return None

	def setup_complete(self) -> None:
		if self.initial_file_path:
			self.load(self.initial_file_path, force_update=True)
		self.window_geometry_config.load_size(self)

	def load(self, path: str, force_update: bool = False) -> None:
		index = Assets.help_tree(force_update=force_update).index(path)
		if not index:
			return
		self.treelist.select(index)
		self.load_help_file()
		if '#' in path:
			fragment = path.split('#')[-1].lower()
			self.markdownview.view_fragment(fragment)

	def load_help_file(self) -> None:
		entry = self.treelist.cur_selection()[-1]
		if entry is None:
			return
		index = self.treelist.index(entry)
		if index is None:
			return
		help_file = Assets.help_tree().get_file(index)
		if not help_file:
			return
		if help_file_path := Assets.help_file_path(help_file.path):
			with open(help_file_path, 'r') as f:
				self.markdownview.load_markdown(f.read())

	def destroy(self) -> None:
		Assets.clear_help_image_cache()
		PyMSDialog.destroy(self)

	def dismiss(self) -> None:
		self.window_geometry_config.save_size(self)
		PyMSDialog.dismiss(self)
