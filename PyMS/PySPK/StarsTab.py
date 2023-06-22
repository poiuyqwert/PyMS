
from .Delegates import MainDelegate
from .Tool import Tool

from ..Utilities.UIKit import *
from ..Utilities import Assets

class StarsTab(NotebookTab):
	def __init__(self, parent: Misc, bind_target: Misc, delegate: MainDelegate) -> None:
		self.delegate = delegate
		NotebookTab.__init__(self, parent)

		self.listbox = ScrolledListbox(self, selectmode=MULTIPLE, font=Font.fixed(), width=1, height=1)
		self.listbox.bind(WidgetEvent.Listbox.Select(), self.select_updated)
		self.listbox.pack(side=TOP, fill=BOTH, padx=2, expand=1)

		self.toolbar = Toolbar(self, bind_target=bind_target)
		self.toolbar.add_radiobutton(Assets.get_image('select'), self.delegate.tool, Tool.select, 'Select', Key.m, enabled=False, tags='file_open')
		self.toolbar.add_radiobutton(Assets.get_image('arrows'), self.delegate.tool, Tool.move, 'Move', Key.v, enabled=False, tags='file_open')
		self.toolbar.add_radiobutton(Assets.get_image('pencil'), self.delegate.tool, Tool.draw, 'Draw', Key.p, enabled=False, tags='file_open')
		self.toolbar.add_spacer(2, flexible=True)
		self.toolbar.add_button(Assets.get_image('up'), lambda: self.move_stars(-1), 'Move Stars Up', enabled=False, tags='stars_selected')
		self.toolbar.add_button(Assets.get_image('down'), lambda: self.move_stars(-1), 'Move Stars Down', enabled=False, tags='stars_selected')
		self.toolbar.pack(side=TOP, fill=X, padx=2, pady=(2,0))

	def action_states(self) -> None:
		self.toolbar.tag_enabled('file_open', self.delegate.is_file_open())
		self.toolbar.tag_enabled('stars_selected', self.delegate.are_stars_selected())

	def select_updated(self, event: Event | None = None) -> None:
		if not self.delegate.spk:
			return
		sel = tuple(int(s) for s in self.listbox.curselection())
		i = 0
		for l,layer in enumerate(self.delegate.spk.layers):
			if self.delegate.visible.get() & (1 << l) and not self.delegate.locked.get() & (1 << l):
				for star in layer.stars:
					if i in sel and not star in self.delegate.selected_stars:
						self.delegate.selected_stars.append(star)
					elif star in self.delegate.selected_stars and not i in sel:
						self.delegate.selected_stars.remove(star)
					i += 1
		self.delegate.update_selection()

	def update_list(self) -> None:
		miny,_ = self.listbox.yview()
		s: float = self.listbox.size() # type: ignore[assignment]
		self.listbox.delete(0, END)
		if not self.delegate.is_file_open():
			return
		if self.delegate.spk:
			for l,layer in enumerate(self.delegate.spk.layers):
				if self.delegate.visible.get() & (1 << l) and not self.delegate.locked.get() & (1 << l):
					for star in layer.stars:
						self.listbox.insert(END, '(%s,%s) on Layer %d' % (str(star.x).rjust(3),str(star.y).rjust(3),l+1))
						if star in self.delegate.selected_stars:
							self.listbox.selection_set(END)
			if self.listbox.size():
				s /= float(self.listbox.size()) # type: ignore[arg-type]
			else:
				s = 1
			self.listbox.yview_moveto(miny * s)

	def update_selection(self) -> None:
		if not self.delegate.spk:
			return
		self.listbox.select_clear(0,END)
		i = 0
		for l,layer in enumerate(self.delegate.spk.layers):
			if self.delegate.visible.get() & (1 << l) and not self.delegate.locked.get() & (1 << l):
				for star in layer.stars:
					if star in self.delegate.selected_stars:
						self.listbox.select_set(i)
					i += 1
		self.action_states()

	def move_stars(self, delta: int) -> None:
		if not self.delegate.spk:
			return
		for layer in self.delegate.spk.layers:
			if delta > 0:
				r = list(range(len(layer.stars)-1,-1,-1))
			else:
				r = list(range(0,len(layer.stars)))
			update = False
			for i in r:
				if layer.stars[i] in self.delegate.selected_stars:
					o = i + delta
					if o >= 0 and o < len(layer.stars):
						tmp = layer.stars[i]
						layer.stars[i] = layer.stars[o]
						layer.stars[o] = tmp
						update = True
			if update:
				self.update_list()

	def clear(self) -> None:
		self.listbox.delete(0, END)
