
from utils import BASE_DIR, couriernew
from ..Utilities.DropDownChooser import DropDownChooser
from UIKit import *
from EventPattern import *

import os

class DropDown(Frame):
	ARROW = None

	def __init__(self, parent, variable, entries, display=None, width=1, state=NORMAL, stay_right=False, none_name='None', none_value=None):
		self.variable = variable
		self.variable.set = self.set
		self.display = display
		self.stay_right = stay_right
		self._original_display_callback = None
		if display and isinstance(display, Variable):
			self._original_display_callback = display.callback
			def callback_wrapper(num):
				self.set(num)
				if self._original_display_callback:
					self._original_display_callback(self.variable.get())
			display.callback = callback_wrapper
		self.size = min(10,len(entries))
		self.none_name = none_name
		self.none_value = none_value
		self._typed = ''
		self._typed_timer = None
		Frame.__init__(self, parent, borderwidth=2, relief=SUNKEN)
		self.listbox = Listbox(self, selectmode=SINGLE, font=couriernew, width=width, height=1, borderwidth=0, exportselection=1, activestyle=DOTBOX)
		self.listbox.bind(Mouse.Click, self.choose)
		self.listbox.bind(Mouse.Scroll, lambda *args: Event.BREAK)
		bind = [
			(Key.Home, lambda a,i=0: self.move(a,i)),
			(Key.End, lambda a,i=END: self.move(a,i)),
			(Key.Up, lambda a,i=-1: self.move(a,i)),
			(Key.Left, lambda a,i=-1: self.move(a,i)),
			(Key.Down, lambda a,i=1: self.move(a,i)),
			(Key.Right, lambda a,i=-1: self.move(a,i)),
			(Key.Prior, lambda a,i=-10: self.move(a,i)),
			(Key.Next, lambda a,i=10: self.move(a,i)),
			# (Key.Space, self.choose),
			(Key.Pressed, self.key_pressed)
		]
		for b in bind:
			self.bind(*b)
			self.listbox.bind(*b)
		self.setentries(entries)
		self.listbox.pack(side=LEFT, fill=X, expand=1)
		self.listbox['state'] = state
		if DropDown.ARROW == None:
			DropDown.ARROW = PhotoImage(file=os.path.join(BASE_DIR, 'PyMS','Images','arrow.gif'))
		self.button = Button(self, image=DropDown.ARROW, command=self.choose, state=state)
		self.button.image = DropDown.ARROW
		self.button.pack(side=RIGHT, fill=Y)

	def __setitem__(self, item, value):
		if item == 'state':
			self.listbox['state'] = value
			self.button['state'] = value
		else:
			Frame.__setitem__(self, item, value)

	def setentries(self, entries):
		selected = self.variable.get()
		self.entries = list(entries)
		self.listbox.delete(0,END)
		for entry in entries:
			self.listbox.insert(END, entry)
		if selected >= self.listbox.size():
			selected = self.listbox.size()-1
		self.listbox.see(selected)
		if self.stay_right:
			self.listbox.xview_moveto(1.0)

	def set(self, num):
		self.change(num)
		Variable.set(self.variable, num)
		self.disp(num)
		if self.stay_right:
			self.listbox.xview_moveto(1.0)

	def change(self, num):
		if num >= self.listbox.size():
			num = self.listbox.size()-1
		self.listbox.select_clear(0,END)
		#self.listbox.select_set(num)
		self.listbox.see(num)

	def move(self, e, a):
		if self.listbox['state'] == NORMAL:
			if a not in [0,END]:
				a = max(min(self.listbox.size(),self.variable.get() + a),0)
			self.set(a)
			self.listbox.select_set(a)

	def choose(self, e=None):
		if self.listbox['state'] == NORMAL:
			i = self.variable.get()
			if i == self.none_value:
				n = self.entries.index(self.none_name)
				if n >= 0:
					i = n
			c = DropDownChooser(self, self.entries, i)
			if c.result > -1 and c.result < len(self.entries) and self.entries[c.result] == self.none_name and self.none_value:
				self.set(self.none_value)
			else:
				self.set(c.result)
			self.listbox.select_set(c.result)

	def disp(self, n):
		if self.display:
			if isinstance(self.display, Variable):
				self.display.set(n)
			else:
				self.display(n)

	def key_pressed(self, event):
		if self._typed_timer:
			self.after_cancel(self._typed_timer)
		if event.keysym == Key.Backspace.name():
			self._typed = self._typed[:-1]
		elif event.char:
			self._typed += event.char.lower()
		if self._typed:
			items = self.listbox.get(0, END)
			for index,item in enumerate(items):
				if self._typed in item.lower():
					self.set(index)
					break
			self._typed_timer = self.after(1000, self.clear_typed)

	def clear_typed(self):
		self._typed_timer = None
		self._typed = ''
