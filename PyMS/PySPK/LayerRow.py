
from ..Utilities import Assets
from ..Utilities import UIKit as UI

from typing import Any

class LayerRow(UI.Frame):
	def __init__(self, *, parent: UI.Misc, selvar: UI.IntVar, visvar: UI.IntVar, lockvar: UI.IntVar, layer: int, **kwargs: Any) -> None:
		UI.Frame.__init__(self, parent, **kwargs)
		self.selvar = selvar
		self.visvar = visvar
		self.lockvar = lockvar
		self.layer = layer
		self.visible = UI.BooleanVar()
		self.visible.set(True)
		self.locked = UI.BooleanVar()
		self.locked.set(False)
		# TODO: Use Toolbar?
		visbtn = UI.Checkbutton(self, image=Assets.get_image('eye'), indicatoron=False, width=20, height=20, variable=self.visible, onvalue=True, offvalue=False, command=self.toggle_vis, highlightthickness=0)
		visbtn.pack(side=UI.LEFT)
		lockbtn = UI.Checkbutton(self, image=Assets.get_image('lock'), indicatoron=False, width=20, height=20, variable=self.locked, onvalue=True, offvalue=False, command=self.toggle_lock, highlightthickness=0)
		lockbtn.pack(side=UI.LEFT)
		self.label = UI.Label(self, text=f'Layer {layer+1}')
		self.label.pack(side=UI.LEFT)
		self.selvar.trace_add('write', self.update_state)
		self.visvar.trace_add('write', self.update_state)
		self.lockvar.trace_add('write', self.update_state)
		self.update_state()
		self.bind(UI.Mouse.Click_Left(), self.select)
		self.label.bind(UI.Mouse.Click_Left(), self.select)
		self.hide_widget: UI.Frame | None = None # Gross :(

	def update_state(self, *_args: Any, **_kwargs: Any) -> None:
		self.visible.set((self.visvar.get() & (1 << self.layer)) != 0)
		self.locked.set((self.lockvar.get() & (1 << self.layer)) != 0)
		# TODO: Support theme
		if self.selvar.get() == self.layer:
			self.config(background=UI.Colors.SystemHighlight)
			self.label.config(background=UI.Colors.SystemHighlight)
		else:
			self.config(background='#FFFFFF')
			self.label.config(background='#FFFFFF')

	def select(self, _event: UI.Event) -> None:
		self.selvar.set(self.layer)

	def toggle_vis(self) -> None:
		if self.visible.get():
			self.visvar.set(self.visvar.get() | (1 << self.layer))
		else:
			self.visvar.set(self.visvar.get() & ~(1 << self.layer))

	def toggle_lock(self) -> None:
		if self.locked.get():
			self.lockvar.set(self.lockvar.get() | (1 << self.layer))
		else:
			self.lockvar.set(self.lockvar.get() & ~(1 << self.layer))

	def hide(self) -> None:
		if self.hide_widget is None:
			self.hide_widget = UI.Frame(self)
		self.hide_widget.place(in_=self, relwidth=1, relheight=1)

	def show(self) -> None:
		if self.hide_widget:
			self.hide_widget.place_forget()
