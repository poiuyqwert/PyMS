
import TkinterExt

try: # Python 2
	import Tkinter as _tk
except: # Python 3
	import tkinter as _tk
import inspect as _inspect

_THEME = [] # type: list[tuple[_Selector, dict[str, str | int]]]
_WIDGET_TYPES = None

def _resolve_widget_types():
	global _WIDGET_TYPES
	_WIDGET_TYPES = {
		'Tk': _tk.Tk,
		'Toplevel': TkinterExt.Toplevel,
		'MainWindow': TkinterExt.MainWindow,
		'Frame': _tk.Frame,
		'Button': _tk.Button,
		'Checkbutton': _tk.Checkbutton,
		'Radiobutton': _tk.Radiobutton,
		'Label': _tk.Label,
		'Text': _tk.Text,
		'Entry': _tk.Entry,
		'Canvas': TkinterExt.Canvas,
		'Listbox': _tk.Listbox,
		'Menu': TkinterExt.Menu,
		'Scrollbar': _tk.Scrollbar,
		'LabelFrame': _tk.LabelFrame,
		'PanedWindow': _tk.PanedWindow,
	}
	from DropDown import DropDown
	from Toolbar import Toolbar
	from StatusBar import StatusBar
	_WIDGET_TYPES.update({
		'DropDown': DropDown,
		'Toolbar': Toolbar,
		'StatusBar': StatusBar
	})

class _Selector(object):
	def __init__(self, definition): # type: (str) -> _Selector
		global _WIDGET_TYPES
		if _WIDGET_TYPES == None:
			_resolve_widget_types()
		self.components = []
		for component in definition.split(' '):
			if not component in '**':
				component = _WIDGET_TYPES[component]
			self.components.insert(0, component)

	def is_default(self):
		return len(self.components) == 1 and self.components[0] == '*'

	def priority(self):
		if self.is_default():
			return 0
		priority = 0
		for component in self.components:
			if isinstance(component, str):
				continue
			priority += len(_inspect.getmro(component))
		return priority + 100 * len(self.components)

	def matches(self, widget): # type: (_tk.Misc) -> bool
		if self.is_default():
			return True
		component_index = 0
		wildcard = False
		while component_index < len(self.components):
			component = self.components[component_index]
			if component == '*':
				widget = widget.master
				component_index += 1
			elif component == '**':
				wildcard = True
				component_index += 1
			else:
				if isinstance(widget, component):
					widget = widget.master
					component_index += 1
					wildcard = False
				elif wildcard:
					widget = widget.master
				else:
					return False
		return True

def load_theme(name, main_window): # type: (str, _tk.Tk) -> None
	global _THEME
	_THEME = []

	from . import Assets
	import json

	try:
		with open(Assets.theme_file_path(name), 'r') as f:
			theme = json.load(f) # type: dict[str, dict[str, str | int]]
	except:
		raise # TODO: Handle better?

	for selector,styles in theme.items():
		try:
			selector = _Selector(selector)
			_THEME.append((selector, styles))
		except:
			raise # TODO: Handle better?
	_THEME.sort(key=lambda item: item[0].priority())

	_apply_theme(main_window)

def _apply_theme(widget): # type: (_tk.Misc) -> None
	for selector,styles in _THEME:
		if selector.matches(widget):
			for key,value in styles.items():
				if not key in widget.keys():
					continue
				widget.config({key: value})

class Tk(_tk.Tk):
	def __init__(self, *args, **kwargs):
		_tk.Tk.__init__(self, *args, **kwargs)
		_apply_theme(self)

class Toplevel(TkinterExt.Toplevel):
	def __init__(self, *args, **kwargs):
		TkinterExt.Toplevel.__init__(self, *args, **kwargs)
		_apply_theme(self)

class Frame(_tk.Frame):
	def __init__(self, *args, **kwargs):
		_tk.Frame.__init__(self, *args, **kwargs)
		_apply_theme(self)

class Button(_tk.Button):
	def __init__(self, *args, **kwargs):
		_tk.Button.__init__(self, *args, **kwargs)
		_apply_theme(self)

class Checkbutton(_tk.Checkbutton):
	def __init__(self, *args, **kwargs):
		_tk.Checkbutton.__init__(self, *args, **kwargs)
		_apply_theme(self)

class Radiobutton(_tk.Radiobutton):
	def __init__(self, *args, **kwargs):
		_tk.Radiobutton.__init__(self, *args, **kwargs)
		_apply_theme(self)

class Label(_tk.Label):
	def __init__(self, *args, **kwargs):
		_tk.Label.__init__(self, *args, **kwargs)
		_apply_theme(self)

class Text(_tk.Text):
	def __init__(self, *args, **kwargs):
		_tk.Text.__init__(self, *args, **kwargs)
		_apply_theme(self)

class Entry(_tk.Entry):
	def __init__(self, *args, **kwargs):
		_tk.Entry.__init__(self, *args, **kwargs)
		_apply_theme(self)

class Canvas(TkinterExt.Canvas):
	def __init__(self, *args, **kwargs):
		TkinterExt.Canvas.__init__(self, *args, **kwargs)
		_apply_theme(self)

class Listbox(_tk.Listbox):
	def __init__(self, *args, **kwargs):
		_tk.Listbox.__init__(self, *args, **kwargs)
		_apply_theme(self)

class Menu(TkinterExt.Menu):
	def __init__(self, *args, **kwargs):
		TkinterExt.Menu.__init__(self, *args, **kwargs)
		_apply_theme(self)

# class Scrollbar(ttk.Scrollbar):
# 	def __init__(self, *args, **kwargs):
# 		ttk.Scrollbar.__init__(self, *args, **kwargs)

class Scrollbar(_tk.Scrollbar):
	def __init__(self, *args, **kwargs):
		_tk.Scrollbar.__init__(self, *args, **kwargs)
		_apply_theme(self)

class LabelFrame(_tk.LabelFrame):
	def __init__(self, *args, **kwargs):
		_tk.LabelFrame.__init__(self, *args, **kwargs)
		_apply_theme(self)

class PanedWindow(_tk.PanedWindow):
	def __init__(self, *args, **kwargs):
		_tk.PanedWindow.__init__(self, *args, **kwargs)
		_apply_theme(self)
