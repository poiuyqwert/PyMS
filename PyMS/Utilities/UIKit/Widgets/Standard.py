
from .. import Theme as _Theme
from .Extensions import MiscExtensions, WindowExtensions

import tkinter as _Tk

from typing import Any

__all__ = [
	'Widget',
	'Misc',
	'Wm',
	'Tk',
	'Toplevel',
	'Frame',
	'Button',
	'Checkbutton',
	'Radiobutton',
	'Label',
	'Text',
	'Entry',
	'Listbox',
	'Scrollbar',
	'LabelFrame',
	'PanedWindow',
]

# For type hinting
Widget = _Tk.Widget
Misc = _Tk.Misc
Wm = _Tk.Wm

class Tk(_Tk.Tk, WindowExtensions):
	def __init__(self, *args: Any, **kwargs: Any) -> None:
		_Tk.Tk.__init__(self, *args, **kwargs)
		_Theme.apply_theme(self)

class Toplevel(_Tk.Toplevel, WindowExtensions):
	def __init__(self, *args: Any, **kwargs: Any) -> None:
		_Tk.Toplevel.__init__(self, *args, **kwargs)
		_Theme.apply_theme(self)

class Frame(_Tk.Frame, MiscExtensions):
	def __init__(self, *args: Any, **kwargs: Any) -> None:
		_Tk.Frame.__init__(self, *args, **kwargs)
		_Theme.apply_theme(self)

class Button(_Tk.Button, MiscExtensions):
	def __init__(self, *args: Any, **kwargs: Any) -> None:
		_Tk.Button.__init__(self, *args, **kwargs)
		_Theme.apply_theme(self)

class Checkbutton(_Tk.Checkbutton, MiscExtensions):
	def __init__(self, *args: Any, **kwargs: Any) -> None:
		_Tk.Checkbutton.__init__(self, *args, **kwargs)
		_Theme.apply_theme(self)

class Radiobutton(_Tk.Radiobutton, MiscExtensions):
	def __init__(self, *args: Any, **kwargs: Any) -> None:
		_Tk.Radiobutton.__init__(self, *args, **kwargs)
		_Theme.apply_theme(self)

class Label(_Tk.Label, MiscExtensions):
	def __init__(self, *args: Any, **kwargs: Any) -> None:
		_Tk.Label.__init__(self, *args, **kwargs)
		_Theme.apply_theme(self)

class Text(_Tk.Text, MiscExtensions):
	def __init__(self, *args: Any, **kwargs: Any) -> None:
		_Tk.Text.__init__(self, *args, **kwargs)
		_Theme.apply_theme(self)

class Entry(_Tk.Entry, MiscExtensions):
	def __init__(self, *args: Any, **kwargs: Any) -> None:
		_Tk.Entry.__init__(self, *args, **kwargs)
		_Theme.apply_theme(self)

class Listbox(_Tk.Listbox, MiscExtensions):
	def __init__(self, *args: Any, **kwargs: Any) -> None:
		_Tk.Listbox.__init__(self, *args, **kwargs)
		_Theme.apply_theme(self)

# class Scrollbar(ttk.Scrollbar):
# 	def __init__(self, *args: Any, **kwargs: Any) -> None:
# 		ttk.Scrollbar.__init__(self, *args, **kwargs)

class Scrollbar(_Tk.Scrollbar, MiscExtensions):
	def __init__(self, *args: Any, **kwargs: Any) -> None:
		_Tk.Scrollbar.__init__(self, *args, **kwargs)
		_Theme.apply_theme(self)

class LabelFrame(_Tk.LabelFrame, MiscExtensions):
	def __init__(self, *args: Any, **kwargs: Any) -> None:
		_Tk.LabelFrame.__init__(self, *args, **kwargs)
		_Theme.apply_theme(self)

class PanedWindow(_Tk.PanedWindow, MiscExtensions):
	def __init__(self, *args: Any, **kwargs: Any) -> None:
		_Tk.PanedWindow.__init__(self, *args, **kwargs)
		_Theme.apply_theme(self)
