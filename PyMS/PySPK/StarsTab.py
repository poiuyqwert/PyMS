
from .Tool import Tool

from ..Utilities.UIKit import *
from ..Utilities.Notebook import NotebookTab
from ..Utilities.ScrolledListbox import ScrolledListbox
from ..Utilities.Toolbar import Toolbar
from ..Utilities import Assets

class StarsTab(NotebookTab):
	def __init__(self, parent, toplevel):
		self.toplevel = toplevel
		NotebookTab.__init__(self, parent)

		self.listbox = ScrolledListbox(self, selectmode=MULTIPLE, font=Font.fixed(), width=1, height=1)
		self.listbox.bind(WidgetEvent.Listbox.Select, self.select_updated)
		self.listbox.pack(side=TOP, fill=BOTH, padx=2, expand=1)

		self.toolbar = Toolbar(self, bind_target=self.toplevel)
		self.toolbar.add_radiobutton(Assets.get_image('select'), self.toplevel.tool, Tool.Select, 'Select', Key.m, enabled=False, tags='file_open')
		self.toolbar.add_radiobutton(Assets.get_image('arrows'), self.toplevel.tool, Tool.Move, 'Move', Key.v, enabled=False, tags='file_open')
		self.toolbar.add_radiobutton(Assets.get_image('pencil'), self.toplevel.tool, Tool.Draw, 'Draw', Key.p, enabled=False, tags='file_open')
		self.toolbar.add_spacer(2, flexible=True)
		self.toolbar.add_button(Assets.get_image('up'), lambda: self.move_stars(-1), 'Move Stars Up', enabled=False, tags='stars_selected')
		self.toolbar.add_button(Assets.get_image('down'), lambda: self.move_stars(-1), 'Move Stars Down', enabled=False, tags='stars_selected')
		self.toolbar.pack(side=TOP, fill=X, padx=2, pady=(2,0))

	def action_states(self):
		self.toolbar.tag_enabled('file_open', self.toplevel.is_file_open())
		self.toolbar.tag_enabled('stars_selected', self.toplevel.are_stars_selected())

	def select_updated(self, e=None):
		if not self.toplevel.is_file_open():
			return
		sel = tuple(int(s) for s in self.listbox.curselection())
		i = 0
		for l,layer in enumerate(self.toplevel.spk.layers):
			if self.toplevel.visible.get() & (1 << l) and not self.toplevel.locked.get() & (1 << l):
				for star in layer.stars:
					if i in sel and not star in self.toplevel.selected_stars:
						self.toplevel.selected_stars.append(star)
					elif star in self.toplevel.selected_stars and not i in sel:
						self.toplevel.selected_stars.remove(star)
					i += 1
		self.toplevel.update_selection()

	def update_list(self):
		miny,_ = self.listbox.yview()
		s = self.listbox.size()
		self.listbox.delete(0, END)
		if not self.toplevel.is_file_open():
			return
		if self.toplevel.spk:
			for l,layer in enumerate(self.toplevel.spk.layers):
				if self.toplevel.visible.get() & (1 << l) and not self.toplevel.locked.get() & (1 << l):
					for star in layer.stars:
						self.listbox.insert(END, '(%s,%s) on Layer %d' % (str(star.x).rjust(3),str(star.y).rjust(3),l+1))
						if star in self.toplevel.selected_stars:
							self.listbox.selection_set(END)
			if self.listbox.size():
				s /= float(self.listbox.size())
			else:
				s = 1
			self.listbox.yview_moveto(miny * s)

	def update_selection(self):
		if not self.toplevel.is_file_open():
			return
		self.listbox.select_clear(0,END)
		i = 0
		for l,layer in enumerate(self.toplevel.spk.layers):
			if self.toplevel.visible.get() & (1 << l) and not self.toplevel.locked.get() & (1 << l):
				for star in layer.stars:
					if star in self.toplevel.selected_stars:
						self.listbox.select_set(i)
					i += 1
		self.action_states()

	def move_stars(self, delta):
		if not self.toplevel.is_file_open():
			return
		for layer in self.toplevel.spk.layers:
			if delta > 0:
				r = range(len(layer.stars)-1,-1,-1)
			else:
				r = range(0,len(layer.stars))
			update = False
			for i in r:
				if layer.stars[i] in self.toplevel.selected_stars:
					o = i + delta
					if o >= 0 and o < len(layer.stars):
						tmp = layer.stars[i]
						layer.stars[i] = layer.stars[o]
						layer.stars[o] = tmp
						update = True
			if update:
				self.update_list()

	def clear(self):
		self.listbox.delete(0, END)
