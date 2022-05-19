
from UIKit import *
from PyMSDialog import PyMSDialog
from MarkdownView import MarkdownView
from TreeList import TreeList
import Assets

class HelpDialog(PyMSDialog):
	def __init__(self, parent, help_file_path=None):
		self.initial_file_path = help_file_path
		PyMSDialog.__init__(self, parent, 'Help')

	def widgetize(self):
		self.treelist = TreeList(self, width=30)
		self.treelist.pack(side=LEFT, fill=Y)
		self.treelist.build(((folder,True) for folder in Assets.help_tree().folders), lambda node: () if isinstance(node, Assets.HelpFile) else tuple((file,None) for file in node.files) + tuple((folder,True) for folder in node.folders), lambda node: node.name)
		self.treelist.bind(WidgetEvent.Listbox.Select, lambda *_: self.load_help_file())

		self.markdownview = MarkdownView(self, link_callback=self.load)
		self.markdownview.pack(side=LEFT, fill=BOTH, expand=1)

	def setup_complete(self):
		if self.initial_file_path:
			self.load(self.initial_file_path)

	def load(self, path): # type: (str) -> None
		index = Assets.help_tree().index(path)
		if not index:
			return
		self.treelist.select(index)
		self.load_help_file()
		if '#' in path:
			fragment = path.split('#')[-1].lower()
			self.markdownview.view_fragment(fragment)

	def load_help_file(self):
		index = self.treelist.cur_selection()[-1]
		if index == None:
			return
		help_file = Assets.help_tree().get_file(self.treelist.index(index))
		if not help_file:
			return
		with open(Assets.help_file_path(help_file.path), 'r') as f:
			self.markdownview.load_markdown(f.read())