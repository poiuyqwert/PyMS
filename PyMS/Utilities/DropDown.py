
from .DropDownChooser import DropDownChooser
from .UIKit import *
from .EventPattern import *
from . import Assets

class DropDown(Frame):
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
		Frame.__init__(self, parent, borderwidth=2, relief=SUNKEN, takefocus=False)
		self.text = StringVar()
		self.entry = Entry(self, textvariable=self.text, font=Font.fixed(), width=width, borderwidth=0, highlightthickness=0, cursor='arrow', insertontime=0)
		self.entry.pack(side=LEFT, fill=X, expand=1)
		self.entry['state'] = state
		self.entry.bind(Mouse.Click_Left, self.choose)
		self.entry.bind(Key.Home, lambda a,i=0: self.move(a,i)),
		self.entry.bind(Key.End, lambda a,i=END: self.move(a,i)),
		self.entry.bind(Key.Up, lambda a,i=-1: self.move(a,i)),
		self.entry.bind(Key.Left, lambda a,i=-1: self.move(a,i)),
		self.entry.bind(Key.Down, lambda a,i=1: self.move(a,i)),
		self.entry.bind(Key.Right, lambda a,i=1: self.move(a,i)),
		self.entry.bind(Key.Prior, lambda a,i=-10: self.move(a,i)),
		self.entry.bind(Key.Next, lambda a,i=10: self.move(a,i)),
		self.entry.bind(Key.Pressed, self.key_pressed),
		self.entry.bind(Key.Return, self.choose)
		self.setentries(entries)
		self.button = Button(self, image=Assets.get_image('arrow'), command=self.choose, state=state)
		self.button.pack(side=RIGHT, fill=Y)

		self.background_color = self.entry.cget('bg')
		self.highlight_color = self.entry.cget('selectbackground')
		def update_background(color):
			self.entry['bg'] = color
		self.entry.bind(Focus.In, lambda *_: update_background(self.highlight_color))
		self.entry.bind(Focus.Out, lambda *_: update_background(self.background_color))
		# The Focus.Out event stops firing sometimes, so we use a workaround with `validatecommand` triggering on `focusout` to overcome the issue
		def validate(reason):
			if reason == 'focusout':
				update_background(self.background_color)
			return True
		self.entry.config(validate='focusout', validatecommand=(self.register(validate), '%V'))

	def __setitem__(self, item, value):
		if item == 'state':
			self.entry['state'] = value
			self.button['state'] = value
		else:
			Frame.__setitem__(self, item, value)

	def setentries(self, entries):
		self.entries = list(entries)
		if self.entries:
			self.text.set(self.entries[self.variable.get()])
		else:
			self.text.set('')

	def set(self, num):
		self.change(num)
		Variable.set(self.variable, num)
		self.disp(num)
		if self.stay_right:
			self.entry.xview_moveto(1.0)

	def change(self, num):
		if num >= len(self.entries):
			num = len(self.entries)-1
		if self.entries:
			self.text.set(self.entries[num])
			if self.stay_right:
				self.entry.xview_moveto(1.0)
		else:
			self.text.set('')

	def move(self, e, a):
		if self.entry['state'] == NORMAL:
			if a == END:
				a = len(self.entries)-1
			elif a:
				a = max(min(len(self.entries)-1,self.variable.get() + a),0)
			self.set(a)
		return EventPropogation.Break

	def choose(self, e=None):
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

	def clear_typed(self):
		self._typed_timer = None
		self._typed = ''
