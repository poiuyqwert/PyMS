
from .DropDownChooser import DropDownChooser
from ..Widgets import *
from ..Font import Font
from ..EventPattern import *
from ..Variables import IntegerVar

from ... import Assets

from typing import Callable, Literal, Sequence

class DropDown(Frame):
	def __init__(self, parent: Misc, variable: IntVar, entries: Sequence[str], display: IntegerVar | Callable[[int], None] | None = None, width: int = 1, state: Literal['normal', 'active', 'disabled'] = NORMAL, stay_right: bool = False, none_name: str = 'None', none_value: int | None = None):
		self.variable = variable
		self.variable.set = self.set # type: ignore[assignment]
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
		# self.size = min(10,len(entries))
		self.none_name = none_name
		self.none_value = none_value
		self._typed = ''
		self._typed_timer: str | None = None
		Frame.__init__(self, parent, borderwidth=2, relief=SUNKEN, takefocus=False)
		self.text = StringVar()
		self.entry = Entry(self, textvariable=self.text, font=Font.fixed(), width=width, highlightthickness=0, cursor='arrow', insertontime=0)
		self.entry.config(bd=0)
		self.entry.pack(side=LEFT, fill=X, expand=1)
		self.entry['state'] = state
		self.entry.bind(Mouse.Click_Left(), self.choose)
		def move_callback(i: int| Literal['end']) -> Callable[[Event], None]:
			def move(e: Event) -> None:
				self.move(e, i)
			return move
		self.entry.bind(Key.Home(), move_callback(0)),
		self.entry.bind(Key.End(), move_callback(END)),
		self.entry.bind(Key.Up(), move_callback(-1)),
		self.entry.bind(Key.Left(), move_callback(-1)),
		self.entry.bind(Key.Down(), move_callback(1)),
		self.entry.bind(Key.Right(), move_callback(1)),
		self.entry.bind(Key.Prior(), move_callback(-10)),
		self.entry.bind(Key.Next(), move_callback(10)),
		self.entry.bind(Key.Pressed(), self.key_pressed),
		self.entry.bind(Key.Return(), self.choose)
		self.setentries(entries)
		self.button = Button(self, image=Assets.get_image('arrow'), command=self.choose, state=state)
		self.button.pack(side=RIGHT, fill=Y)

		self.background_color = self.entry.cget('bg')
		self.highlight_color = self.entry.cget('selectbackground')
		def update_background(color):
			self.entry['bg'] = color
		self.entry.bind(Focus.In(), lambda *_: update_background(self.highlight_color))
		self.entry.bind(Focus.Out(), lambda *_: update_background(self.background_color))
		# The Focus.Out event stops firing sometimes, so we use a workaround with `validatecommand` triggering on `focusout` to overcome the issue
		def validate(reason):
			if reason == 'focusout':
				update_background(self.background_color)
			return True
		self.entry.config(validate='focusout', validatecommand=(self.register(validate), '%V'))

	def __setitem__(self, item: str, value: Any) -> None:
		if item == 'state':
			self.entry['state'] = value
			self.button['state'] = value
		else:
			Frame.__setitem__(self, item, value)

	def setentries(self, entries: Sequence[str]) -> None:
		self.entries = list(entries)
		if self.entries:
			self.text.set(self.entries[self.variable.get()])
		else:
			self.text.set('')

	def set(self, num: int) -> None:
		self.change(num)
		IntVar.set(self.variable, num)
		self.disp(num)
		if self.stay_right:
			self.entry.xview_moveto(1.0)

	def change(self, num: int) -> None:
		if num >= len(self.entries):
			num = len(self.entries)-1
		if self.entries:
			self.text.set(self.entries[num])
			if self.stay_right:
				self.entry.xview_moveto(1.0)
		else:
			self.text.set('')

	def move(self, e: Event, a: int | Literal['end']) -> str:
		if self.entry['state'] == NORMAL:
			if a == END:
				i = len(self.entries)-1
			elif a:
				i = max(min(len(self.entries)-1,self.variable.get() + a),0)
			self.set(i)
		return EventPropogation.Break

	def choose(self, e: Event | None = None) -> None:
		if self.entry['state'] == NORMAL:
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

	def disp(self, n: int) -> None:
		if self.display:
			if isinstance(self.display, Variable):
				self.display.set(n)
			else:
				self.display(n)

	def key_pressed(self, event: Event) -> str:
		if self._typed_timer:
			self.after_cancel(self._typed_timer)
			self._typed_timer = None
		if event.keysym == Key.Backspace.name():
			self._typed = self._typed[:-1]
		elif event.keysym == Key.Tab.name() or event.char == '\t':
			return EventPropogation.Continue
		elif event.char:
			self._typed += event.char.lower()
		if self._typed:
			for index,item in enumerate(self.entries):
				if self._typed in item.lower():
					self.set(index)
					break
			self._typed_timer = self.after(1000, self.clear_typed)
		return EventPropogation.Break

	def clear_typed(self) -> None:
		self._typed_timer = None
		self._typed = ''
