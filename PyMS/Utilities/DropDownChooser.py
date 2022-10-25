
from .UIKit import *
from .EventPattern import *

class DropDownChooser(Toplevel):
	def __init__(self, parent, list, select):
		self.focus = 0
		self.parent = parent
		self.result = select
		self._typed = ''
		self._typed_timer = None
		Toplevel.__init__(self, parent, relief=SOLID, borderwidth=1)
		self.wm_overrideredirect(1)
		parent_toplevel = parent.winfo_toplevel()
		if is_mac():
			self.transient(parent_toplevel)
		scrollbar = Scrollbar(self)
		self.listbox = Listbox(self, selectmode=SINGLE, height=min(10,len(list)), borderwidth=0, font=Font.fixed(), highlightthickness=0, yscrollcommand=scrollbar.set, activestyle=DOTBOX)
		for e in list:
			self.listbox.insert(END,e)
		if self.result > -1:
			self.listbox.select_set(self.result)
			self.listbox.see(self.result)
		self.listbox.bind(ButtonRelease.Click_Left, self.select)
		bind = [
			(Cursor.Enter, lambda e,i=1: self.enter(e,i)),
			(Cursor.Leave, lambda e,i=0: self.enter(e,i)),
			(Mouse.Click_Left, self.focusout),
			(Key.Return, self.select),
			(Key.Escape, self.close),
			(Mouse.Scroll, self.scroll),
			(Key.Home, lambda e: self.move(0)),
			(Key.End, lambda e: self.move(END)),
			(Key.Up, lambda e: self.move(-1)),
			(Key.Left, lambda e: self.move(-1)),
			(Key.Down, lambda e: self.move(1)),
			(Key.Right, lambda e: self.move(-1)),
			(Key.Prior, lambda e: self.move(-10)),
			(Key.Next, lambda e: self.move(10)),
			(Key.Pressed, self.key_pressed)
		]
		for b in bind:
			self.bind(*b)
		scrollbar.config(command=self.listbox.yview)
		if len(list) > 10:
			scrollbar.pack(side=RIGHT, fill=Y)
		self.listbox.pack(side=LEFT, fill=BOTH, expand=1)
		w = parent.winfo_width()
		h = self.listbox.winfo_reqheight()
		x = parent.winfo_rootx()
		y = parent.winfo_rooty() + parent.winfo_height()
		if y + h > self.winfo_screenheight():
			y -= parent.winfo_height() + h
		self.geometry('%dx%d+%d+%d' % (w,h,x, y))
		self.focus_binding = None
		self.focus_binding = parent_toplevel.bind(Mouse.ButtonPress, self.select, True)
		self.bind(Focus.Out, self.select)
		self.focus_set()
		self.wait_window(self)

	def enter(self, e, f):
		self.focus = f

	def focusout(self, e):
		if not self.focus:
			self.select()

	def move(self, offset):
		if offset in [0,END]:
			index = offset
		else:
			index = max(min(self.listbox.size()-1,int(self.listbox.curselection()[0]) + offset),0)
		self.jump_to(index)

	def jump_to(self, index):
		self.listbox.select_clear(0,END)
		self.listbox.select_set(index)
		self.listbox.see(index)

	def scroll(self, e):
		if e.delta > 0:
			self.listbox.yview('scroll', -2, 'units')
		else:
			self.listbox.yview('scroll', 2, 'units')

	def home(self, e):
		self.listbox.yview('moveto', 0.0)

	def end(self, e):
		self.listbox.yview('moveto', 1.0)

	def up(self, e):
		self.listbox.yview('scroll', -1, 'units')

	def down(self, e):
		self.listbox.yview('scroll', 1, 'units')

	def pageup(self, e):
		self.listbox.yview('scroll', -1, 'pages')

	def pagedown(self, e):
		self.listbox.yview('scroll', 1, 'pages')

	def select(self, e=None):
		s = self.listbox.curselection()
		if s:
			self.result = int(s[0])
		self.close()

	def close(self, e=None):
		self.parent.focus_set()
		self.withdraw()
		self.update_idletasks()
		self.destroy()

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
					self.jump_to(index)
					break
			self._typed_timer = self.after(1000, self.clear_typed)

	def clear_typed(self):
		self._typed_timer = None
		self._typed = ''

	def destroy(self):
		if self.focus_binding:
			parent_toplevel = self.parent.winfo_toplevel()
			unbind(parent_toplevel, Mouse.ButtonPress, self.focus_binding)
		Toplevel.destroy(self)
