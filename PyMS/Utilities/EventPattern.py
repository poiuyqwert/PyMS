# coding=utf-8

from utils import is_mac

import inspect

# https://www.tcl-lang.org/man/tcl8.4/TkCmd/bind.htm

class EventPattern(object):
	def __init__(self, *fields):
		# TODO: Validate fields make sense?
		self.fields = fields

	def name(self):
		return '-'.join(field.value for field in self.fields)

	def event(self):
		return '<%s>' % self.name()

	def description(self):
		return ('' if is_mac() else '+').join(field.description for field in self.fields)

	def __str__(self):
		return self.event()

	def __repr__(self):
		return '<EventPattern %s>' % self

	def __add__(self, other):
		if isinstance(other, EventPattern):
			return EventPattern(*(self.fields + other.fields))
		elif isinstance(other, Field):
			return EventPattern(*(self.fields + (other,)))
		else:
			raise TypeError("unsupported operand type(s) for +: '%s' and '%s'" % (type(self).__name__, type(other).__name__))

class Field(object):
	def __init__(self, value, description=None):
		self.value = value
		self.description = description or value

	def __eq__(self, other):
		if not isinstance(other, Field):
			return False
		return other.value == self.value

	def __add__(self, other):
		if isinstance(other, EventPattern):
			return EventPattern(*((self,) + other.fields))
		elif isinstance(other, Field):
			return EventPattern(self, other)
		else:
			raise TypeError("unsupported operand type(s) for +: '%s' and '%s'" % (type(self).__name__, type(other).__name__))

class Modifier:
	Shift = Field('Shift', '⇧' if is_mac() else None)
	Ctrl = Field('Command' if is_mac() else 'Control', '⌘' if is_mac() else 'Ctrl')
	Alt = Field('Option' if is_mac() else 'Alt', '⌥' if is_mac() else None)
	class Mac:
		Ctrl = Field('Control', '⌃' if is_mac() else 'Ctrl')

	Double = Field('Double')
	Triple = Field('Triple')
	Quadruple = Field('Quadruple')

	ButtonRelease = Field('ButtonRelease')

	Left_Click = Field('B1', 'Left-Click')
	Middle_Click = Field('B2', 'Middle-Click')
	Right_Click = Field('B2' if is_mac() else 'B3', 'Right-Click')

# Modifier.Shift = Field('Shift', '⇧' if is_mac() else None)
Modifier.Shift.state = 0x1
# Modifier.Ctrl = Field('Command' if is_mac() else 'Control', '⌘' if is_mac() else 'Ctrl')
Modifier.Ctrl.state = 0x8 if is_mac() else 0x4
# Modifier.Alt = Field('Option' if is_mac() else 'Alt', '⌥' if is_mac() else None)
Modifier.Alt.state = 0x10
# Modifier.Mac.Ctrl = Field('Control', '⌃' if is_mac() else 'Ctrl')
Modifier.Mac.Ctrl.state = 0x4

# Modifier.Double = Field('Double')
# Modifier.Triple = Field('Triple')
# Modifier.Quadruple = Field('Quadruple')

# Modifier.ButtonRelease = Field('ButtonRelease')

# Modifier.Left_Click = Field('B1', 'Left-Click')
# Modifier.Middle_Click = Field('B2', 'Middle-Click')
# Modifier.Right_Click = Field('B2' if is_mac() else 'B3', 'Right-Click')

class Keysym(Field):
	# When using the Shift modifier, something like `Shift-c` does not work, it would need to be `Shift-C`
	# So Keysym's specify their capitalized versions (if applicable) to automatically be adjusted for Shift modifiers
	def __init__(self, key, description=None, capitalized_key=None, capitalized_key_description=None):
		value = key
		description = description or key.capitalize()
		Field.__init__(self, value, description)
		self._capitalized_key = capitalized_key
		self._capitalized_key_description = capitalized_key_description

	def capitalized(self):
		if not self._capitalized_key:
			return self
		return Keysym(self._capitalized_key, self._capitalized_key_description)

	def __repr__(self):
		return "<Keysym '%s'>" % self.value

class Events(object):
	@classmethod
	def modify(cls, *modifiers):
		for attr, value in inspect.getmembers(cls, lambda member: not inspect.ismethod(member)):
			if not attr.startswith('_') and isinstance(value, EventPattern):
				fields = value.fields
				if Modifier.Shift in modifiers:
					fields = tuple(field.capitalized() if isinstance(field, Keysym) else field for field in fields)
				setattr(cls, attr, EventPattern(*(modifiers + fields)))

class Key(Events):
	# https://www.tcl.tk/man/tcl8.6/TkCmd/keysyms.htm
	a = EventPattern(Keysym('a', capitalized_key='A'))
	b = EventPattern(Keysym('b', capitalized_key='B'))
	c = EventPattern(Keysym('c', capitalized_key='C'))
	d = EventPattern(Keysym('d', capitalized_key='D'))
	e = EventPattern(Keysym('e', capitalized_key='E'))
	f = EventPattern(Keysym('f', capitalized_key='F'))
	g = EventPattern(Keysym('g', capitalized_key='G'))
	h = EventPattern(Keysym('h', capitalized_key='H'))
	i = EventPattern(Keysym('i', capitalized_key='I'))
	j = EventPattern(Keysym('j', capitalized_key='J'))
	k = EventPattern(Keysym('k', capitalized_key='K'))
	l = EventPattern(Keysym('l', capitalized_key='L'))
	m = EventPattern(Keysym('m', capitalized_key='M'))
	n = EventPattern(Keysym('n', capitalized_key='N'))
	o = EventPattern(Keysym('o', capitalized_key='O'))
	p = EventPattern(Keysym('p', capitalized_key='P'))
	q = EventPattern(Keysym('q', capitalized_key='Q'))
	r = EventPattern(Keysym('r', capitalized_key='R'))
	s = EventPattern(Keysym('s', capitalized_key='S'))
	t = EventPattern(Keysym('t', capitalized_key='T'))
	u = EventPattern(Keysym('u', capitalized_key='U'))
	v = EventPattern(Keysym('v', capitalized_key='V'))
	w = EventPattern(Keysym('w', capitalized_key='W'))
	x = EventPattern(Keysym('x', capitalized_key='X'))
	y = EventPattern(Keysym('y', capitalized_key='Y'))
	z = EventPattern(Keysym('z', capitalized_key='Z'))

	Return = EventPattern(Keysym('Return'))
	Left = EventPattern(Keysym('Left', '←' if is_mac() else None))
	Right = EventPattern(Keysym('Right', '→' if is_mac() else None))
	Up = EventPattern(Keysym('Up', '↑' if is_mac() else None))
	Down = EventPattern(Keysym('Down', '↓' if is_mac() else None))
	Insert = EventPattern(Keysym('Insert'))
	Delete = EventPattern(Keysym('Delete', '⌫' if is_mac() else None))
	Home = EventPattern(Keysym('Home'))
	End = EventPattern(Keysym('End'))
	Next = EventPattern(Keysym('Next'))
	Prior = EventPattern(Keysym('Prior'))
	Space = EventPattern(Keysym('space'))
	Backspace = EventPattern(Keysym('BackSpace'))
	Escape = EventPattern(Keysym('Escape'))
	Tab = EventPattern(Keysym('Tab'))

	F1 = EventPattern(Keysym('F1'))
	F2 = EventPattern(Keysym('F2'))
	F3 = EventPattern(Keysym('F3'))
	F4 = EventPattern(Keysym('F4'))
	F5 = EventPattern(Keysym('F5'))
	F6 = EventPattern(Keysym('F6'))
	F7 = EventPattern(Keysym('F7'))
	F8 = EventPattern(Keysym('F8'))
	F9 = EventPattern(Keysym('F9'))
	F10 = EventPattern(Keysym('F10'))
	F11 = EventPattern(Keysym('F11'))
	F12 = EventPattern(Keysym('F12'))

	Pressed = EventPattern(Field('KeyPress'))
	Released = EventPattern(Field('KeyRelease'))

class Mouse(Events):
	Left_Click = EventPattern(Field('Button-1', 'Left-Click'))
	Click = Left_Click
	Middle_Click = EventPattern(Field('Button-2', 'Middle-Click'))
	Right_Click = EventPattern(Field('Button-2' if is_mac() else 'Button-3', 'Right-Click'))
	# 4
	# 5

	Left_Drag = EventPattern(Modifier.Left_Click,Field('Motion', '-Drag'))
	Middle_Drag = EventPattern(Modifier.Middle_Click,Field('Motion', '-Drag'))
	Right_Drag = EventPattern(Modifier.Right_Click,Field('Motion', '-Drag'))

	ButtonPress = EventPattern(Field('ButtonPress'))
	ButtonRelease = EventPattern(Field('ButtonRelease'))
	Scroll = EventPattern(Field('MouseWheel'))

class ButtonRelease(Events):
	Left_Click = EventPattern(Field('1', 'Left-Click'))
	Click = Left_Click
	Middle_Click = EventPattern(Field('2', 'Middle-Click'))
	Right_Click = EventPattern(Field('2' if is_mac() else '3', 'Right-Click'))
ButtonRelease.modify(Modifier.ButtonRelease)

# Control
# Alt
# Shift
# Double
# Triple
# Quadruple

class Shift(Key, Mouse):
	class Double(Mouse):
		pass
	class Triple(Mouse):
		pass
	class Quadruple(Mouse):
		pass
	class Ctrl(Key, Mouse):
		class Double(Mouse):
			pass
		class Triple(Mouse):
			pass
		class Quadruple(Mouse):
			pass
		class Alt(Key, Mouse):
			class Double(Mouse):
				pass
			class Triple(Mouse):
				pass
			class Quadruple(Mouse):
				pass
Shift.modify(Modifier.Shift)
Shift.Double.modify(Modifier.Shift, Modifier.Double)
Shift.Triple.modify(Modifier.Shift, Modifier.Triple)
Shift.Quadruple.modify(Modifier.Shift, Modifier.Quadruple)
Shift.Ctrl.modify(Modifier.Shift, Modifier.Ctrl)
Shift.Ctrl.Double.modify(Modifier.Shift, Modifier.Ctrl, Modifier.Double)
Shift.Ctrl.Triple.modify(Modifier.Shift, Modifier.Ctrl, Modifier.Triple)
Shift.Ctrl.Quadruple.modify(Modifier.Shift, Modifier.Ctrl, Modifier.Quadruple)
Shift.Ctrl.Alt.modify(Modifier.Shift, Modifier.Ctrl, Modifier.Alt)
Shift.Ctrl.Alt.Double.modify(Modifier.Shift, Modifier.Ctrl, Modifier.Alt, Modifier.Double)
Shift.Ctrl.Alt.Triple.modify(Modifier.Shift, Modifier.Ctrl, Modifier.Alt, Modifier.Triple)
Shift.Ctrl.Alt.Quadruple.modify(Modifier.Shift, Modifier.Ctrl, Modifier.Alt, Modifier.Quadruple)

class Ctrl(Key, Mouse):
	class Double(Mouse):
		pass
	class Triple(Mouse):
		pass
	class Quadruple(Mouse):
		pass
	class Alt(Key, Mouse):
		class Double(Mouse):
			pass
		class Triple(Mouse):
			pass
		class Quadruple(Mouse):
			pass
Ctrl.modify(Modifier.Ctrl)
Ctrl.Double.modify(Modifier.Ctrl, Modifier.Double)
Ctrl.Triple.modify(Modifier.Ctrl, Modifier.Triple)
Ctrl.Quadruple.modify(Modifier.Ctrl, Modifier.Quadruple)
Ctrl.Alt.modify(Modifier.Ctrl, Modifier.Alt)
Ctrl.Alt.Double.modify(Modifier.Ctrl, Modifier.Alt, Modifier.Double)
Ctrl.Alt.Triple.modify(Modifier.Ctrl, Modifier.Alt, Modifier.Triple)
Ctrl.Alt.Quadruple.modify(Modifier.Ctrl, Modifier.Alt, Modifier.Quadruple)

class Alt(Key, Mouse):
	class Double(Mouse):
		pass
	class Triple(Mouse):
		pass
	class Quadruple(Mouse):
		pass
Alt.modify(Modifier.Alt)
Alt.Double.modify(Modifier.Alt, Modifier.Double)
Alt.Triple.modify(Modifier.Alt, Modifier.Triple)
Alt.Quadruple.modify(Modifier.Alt, Modifier.Quadruple)

class Double(Mouse):
	pass
Double.modify(Modifier.Double)
class Triple(Mouse):
	pass
Triple.modify(Modifier.Triple)
class Quadruple(Mouse):
	pass
Quadruple.modify(Modifier.Quadruple)

class Cursor:
	Enter = EventPattern(Field('Enter'))
	Motion = EventPattern(Field('Motion'))
	Leave = EventPattern(Field('Leave'))

class Focus:
	In = EventPattern(Field('FocusIn'))
	Out = EventPattern(Field('FocusOut'))

class WidgetEvent:
	Configure = EventPattern(Field('Configure'))

def main():
	events = [
		Ctrl.a,
		Modifier.Ctrl + Key.a,
		Alt.a,
		Ctrl.Alt.a,
		Shift.Ctrl.Alt.a,
		Shift.Click,
		Shift.Right_Click,
		Shift.Double.Click,
		Shift.Ctrl.Alt.Quadruple.Right_Click,
		Mouse.Left_Drag,
		Shift.Ctrl.Alt.Left_Drag,
		ButtonRelease.Left_Click,
		Double.Click,
		Ctrl.Double.Click
	]
	for event in events:
		print(event)
		print(event.name())
		print(event.description())

	import Tkinter as Tk

	root = Tk.Tk()
	canvas = Tk.Canvas(root, width=400, height=400, bg='grey')
	canvas.grid(row=0, column=1)
	def double_click(*e):
		print('Double')
	canvas.bind(Double.Left_Click, double_click)
	def click(*e):
		print('Left')
	canvas.bind(Mouse.Left_Click, click)
	root.mainloop()

if __name__ == '__main__':
	main()
