
from .UIKit import *
from .PyMSDialog import PyMSDialog
from .MarkdownView import MarkdownView
from . import Assets
from . import Config

class HelpDialog(PyMSDialog):
	def __init__(self, parent, window_geometry_config, help_file_path=None): # type: (Misc, Config.WindowGeometry, str | None) -> None
		self.window_geometry_config = window_geometry_config
		self.initial_file_path = help_file_path
		PyMSDialog.__init__(self, parent, 'Help')

	def widgetize(self): # type: () -> (Misc | None)
		self.treelist = TreeList(self, width=30)
		self.treelist.pack(side=LEFT, fill=Y)
		self.treelist.build(list((folder,True) for folder in Assets.help_tree().folders), lambda node: () if isinstance(node, Assets.HelpFile) else tuple((file,None) for file in node.files) + tuple((folder,True) for folder in node.folders), lambda node: node.name.replace('_', ' '))
		self.treelist.bind(WidgetEvent.Listbox.Select(), lambda *_: self.load_help_file())

		self.markdownview = MarkdownView(self, link_callback=self.load)
		self.markdownview.set_link_foreground(Theme.get_color('help', 'linkforeground', default='#6A5EFF'))
		self.markdownview.set_code_background(Theme.get_color('help', 'codebackground', default='#EEEEEE'))
		self.markdownview.pack(side=LEFT, fill=BOTH, expand=1)
		return None

	def setup_complete(self): # type: () -> None
		if self.initial_file_path:
			self.load(self.initial_file_path, force_update=True)
		self.window_geometry_config.load(self)

	def load(self, path, force_update=False): # type: (str, bool) -> None
		index = Assets.help_tree(force_update=force_update).index(path)
		if not index:
			return
		self.treelist.select(index)
		self.load_help_file()
		if '#' in path:
			fragment = path.split('#')[-1].lower()
			self.markdownview.view_fragment(fragment)

	def load_help_file(self): # type: () -> None
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

	def destroy(self): # type: () -> None
		Assets.clear_help_image_cache()
		PyMSDialog.destroy(self)

	def dismiss(self): # type: () -> None
		self.window_geometry_config.save(self)
		PyMSDialog.dismiss(self)
