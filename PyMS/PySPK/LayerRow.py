
from ..Utilities import Assets
from ..Utilities.UIKit import *

class LayerRow(Frame):
	def __init__(self, parent, selvar=None, visvar=None, lockvar=None, layer=None, **kwargs):
		Frame.__init__(self, parent, **kwargs)
		self.selvar = selvar
		self.visvar = visvar
		self.lockvar = lockvar
		self.layer = layer
		self.visible = BooleanVar()
		self.visible.set(True)
		self.locked = BooleanVar()
		self.locked.set(False)
		# TODO: Use Toolbar?
		visbtn = Checkbutton(self, image=Assets.get_image('eye'), indicatoron=0, width=20, height=20, variable=self.visible, onvalue=True, offvalue=False, command=self.toggle_vis, highlightthickness=0)
		visbtn.pack(side=LEFT)
		lockbtn = Checkbutton(self, image=Assets.get_image('lock'), indicatoron=0, width=20, height=20, variable=self.locked, onvalue=True, offvalue=False, command=self.toggle_lock, highlightthickness=0)
		lockbtn.pack(side=LEFT)
		self.label = Label(self, text='Layer %d' % (layer+1))
		self.label.pack(side=LEFT)
		self.selvar.trace('w', self.update_state)
		self.visvar.trace('w', self.update_state)
		self.lockvar.trace('w', self.update_state)
		self.update_state()
		self.bind(Mouse.Click_Left, self.select)
		self.label.bind(Mouse.Click_Left, self.select)
		self.hide_widget = None # Gross :(

	def update_state(self, *args, **kwargs):
		self.visible.set((self.visvar.get() & (1 << self.layer)) != 0)
		self.locked.set((self.lockvar.get() & (1 << self.layer)) != 0)
		if self.selvar.get() == self.layer:
			self.config(background=Colors.SystemHighlight)
			self.label.config(background=Colors.SystemHighlight)
		else:
			self.config(background='#FFFFFF')
			self.label.config(background='#FFFFFF')

	def select(self, event):
		self.selvar.set(self.layer)

	def toggle_vis(self):
		if self.visible.get():
			self.visvar.set(self.visvar.get() | (1 << self.layer))
		else:
			self.visvar.set(self.visvar.get() & ~(1 << self.layer))

	def toggle_lock(self):
		if self.locked.get():
			self.lockvar.set(self.lockvar.get() | (1 << self.layer))
		else:
			self.lockvar.set(self.lockvar.get() & ~(1 << self.layer))

	def hide(self):
		if self.hide_widget == None:
			self.hide_widget = Frame(self)
		self.hide_widget.place(in_=self, relwidth=1, relheight=1)

	def show(self):
		if self.hide_widget:
			self.hide_widget.place_forget()
