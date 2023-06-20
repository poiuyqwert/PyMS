
from ..Widgets import *
from ..Font import Font
from ..EventPattern import *
from ..Utils import remove_bind

from typing import Callable, Literal

class DropDownChooser(Toplevel):
	def __init__(self, parent: Misc, options: list[str], select: int) -> None:
		self.focus_index = 0
		self.parent = parent
		self.result = select
		self._typed = ''
		self._typed_timer: str | None = None
		Toplevel.__init__(self, parent, relief=SOLID, borderwidth=1)
		self.wm_overrideredirect(True)
		parent_toplevel = parent.winfo_toplevel()
		if is_mac():
			self.transient(parent_toplevel)
		scrollbar = Scrollbar(self)
		self.listbox = Listbox(self, selectmode=SINGLE, height=min(10,len(options)), font=Font.fixed(), highlightthickness=0, yscrollcommand=scrollbar.set, activestyle=DOTBOX)
		self.listbox.config(bd=0)
		for e in options:
			self.listbox.insert(END,e)
		if self.result > -1:
			self.listbox.select_set(self.result)
			self.listbox.see(self.result)
		self.listbox.bind(ButtonRelease.Click_Left(), self.select)
		def enter_callback(i: int) -> Callable[[Event], None]:
			def enter(e: Event) -> None:
				self.enter(e, i)
			return enter
		bind: list[tuple[str, Callable[[Event], None]]] = [
			(Cursor.Enter(), enter_callback(1)),
			(Cursor.Leave(), enter_callback(0)),
			(Mouse.Click_Left(), self.focusout),
			(Key.Return(), self.select),
			(Key.Escape(), self.close),
			(Mouse.Scroll(), self.scroll),
			(Key.Home(), lambda e: self.move(0)),
			(Key.End(), lambda e: self.move(END)),
			(Key.Up(), lambda e: self.move(-1)),
			(Key.Left(), lambda e: self.move(-1)),
			(Key.Down(), lambda e: self.move(1)),
			(Key.Right(), lambda e: self.move(-1)),
			(Key.Prior(), lambda e: self.move(-10)),
			(Key.Next(), lambda e: self.move(10)),
			(Key.Pressed(), self.key_pressed)
		]
		for b in bind:
			self.bind(*b)
		scrollbar.config(command=self.listbox.yview)
		if len(options) > 10:
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
		self.focus_binding = parent_toplevel.bind(Mouse.ButtonPress(), self.select, True)
		self.bind(Focus.Out(), self.select)
		self.focus_set()
		self.wait_window(self)

	def enter(self, e: Event, f: int) -> None:
		self.focus_index = f

	def focusout(self, e: Event) -> None:
		if not self.focus_index:
			self.select()

	def move(self, offset: int | Literal['end']) -> None:
		index: int | Literal['end']
		if offset == 0 or offset == END:
			index = offset
		else:
			index = max(min(self.listbox.size()-1,int(self.listbox.curselection()[0]) + offset),0)
		self.jump_to(index)

	def jump_to(self, index: int | Literal['end']) -> None:
		self.listbox.select_clear(0,END)
		self.listbox.select_set(index)
		self.listbox.see(index)

	def scroll(self, e: Event) -> None:
		if e.delta > 0:
			self.listbox.yview('scroll', -2, 'units')
		else:
			self.listbox.yview('scroll', 2, 'units')

	def home(self, e: Event) -> None:
		self.listbox.yview('moveto', 0.0)

	def end(self, e: Event) -> None:
		self.listbox.yview('moveto', 1.0)

	def up(self, e: Event) -> None:
		self.listbox.yview('scroll', -1, 'units')

	def down(self, e: Event) -> None:
		self.listbox.yview('scroll', 1, 'units')

	def pageup(self, e: Event) -> None:
		self.listbox.yview('scroll', -1, 'pages')

	def pagedown(self, e: Event) -> None:
		self.listbox.yview('scroll', 1, 'pages')

	def select(self, e: Event | None = None) -> None:
		s = self.listbox.curselection()
		if s:
			self.result = int(s[0])
		self.close()

	def close(self, e: Event | None = None) -> None:
		self.parent.focus_set()
		self.withdraw()
		self.update_idletasks()
		self.destroy()

	def key_pressed(self, event: Event) -> None:
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

	def clear_typed(self) -> None:
		self._typed_timer = None
		self._typed = ''

	def destroy(self) -> None:
		if self.focus_binding:
			parent_toplevel = self.parent.winfo_toplevel()
			remove_bind(parent_toplevel, Mouse.ButtonPress(), self.focus_binding)
		Toplevel.destroy(self)
