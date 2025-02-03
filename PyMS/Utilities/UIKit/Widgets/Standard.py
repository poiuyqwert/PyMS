
from .. import Theme as _Theme
from .Extensions import Extensions

import tkinter as _Tk

from typing import Any

__all__ = [
	'Widget',
	'Misc',
	'Tk',
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

class Tk(_Tk.Tk, Extensions):
	def __init__(self, *args: Any, **kwargs: Any) -> None:
		_Tk.Tk.__init__(self, *args, **kwargs)
		_Theme.apply_theme(self)

class Frame(_Tk.Frame, Extensions):
	def __init__(self, *args: Any, **kwargs: Any) -> None:
		_Tk.Frame.__init__(self, *args, **kwargs)
		_Theme.apply_theme(self)

class Button(_Tk.Button, Extensions):
	def __init__(self, *args: Any, **kwargs: Any) -> None:
		_Tk.Button.__init__(self, *args, **kwargs)
		_Theme.apply_theme(self)

class Checkbutton(_Tk.Checkbutton, Extensions):
	def __init__(self, *args: Any, **kwargs: Any) -> None:
		_Tk.Checkbutton.__init__(self, *args, **kwargs)
		_Theme.apply_theme(self)

class Radiobutton(_Tk.Radiobutton, Extensions):
	def __init__(self, *args: Any, **kwargs: Any) -> None:
		_Tk.Radiobutton.__init__(self, *args, **kwargs)
		_Theme.apply_theme(self)

class Label(_Tk.Label, Extensions):
	def __init__(self, *args: Any, **kwargs: Any) -> None:
		_Tk.Label.__init__(self, *args, **kwargs)
		_Theme.apply_theme(self)

class Text(_Tk.Text, Extensions):
	def __init__(self, *args: Any, **kwargs: Any) -> None:
		_Tk.Text.__init__(self, *args, **kwargs)
		_Theme.apply_theme(self)

class Entry(_Tk.Entry, Extensions):
	def __init__(self, *args: Any, **kwargs: Any) -> None:
		_Tk.Entry.__init__(self, *args, **kwargs)
		_Theme.apply_theme(self)

class Listbox(_Tk.Listbox, Extensions):
	def __init__(self, *args: Any, **kwargs: Any) -> None:
		_Tk.Listbox.__init__(self, *args, **kwargs)
		_Theme.apply_theme(self)

# class Scrollbar(ttk.Scrollbar):
# 	def __init__(self, *args: Any, **kwargs: Any) -> None:
# 		ttk.Scrollbar.__init__(self, *args, **kwargs)

class Scrollbar(_Tk.Scrollbar, Extensions):
	def __init__(self, *args: Any, **kwargs: Any) -> None:
		_Tk.Scrollbar.__init__(self, *args, **kwargs)
		_Theme.apply_theme(self)

class LabelFrame(_Tk.LabelFrame, Extensions):
	def __init__(self, *args: Any, **kwargs: Any) -> None:
		_Tk.LabelFrame.__init__(self, *args, **kwargs)
		_Theme.apply_theme(self)

class PanedWindow(_Tk.PanedWindow, Extensions):
	def __init__(self, *args: Any, **kwargs: Any) -> None:
		_Tk.PanedWindow.__init__(self, *args, **kwargs)
		_Theme.apply_theme(self)
