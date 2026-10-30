
from .Components.MainWindow import MainWindow as _MainWindow
from .Widgets import Toplevel as _Toplevel

from typing import TypeAlias as _TypeAlias
from typing import Literal as _Literal

import tkinter as _tk

__all__ = [
	'AnyWindow',
	'AnyPhotoImage',
	'WidgetState',
	'Relief',
	'Anchor',
	'Sticky',
	'SelectMode',
	'MoveViewBy',
	'Comparitors',
]

AnyWindow: _TypeAlias = _MainWindow | _Toplevel

try:
	from PIL import ImageTk as _ImageTk

	AnyPhotoImage: _TypeAlias = _tk.PhotoImage | _ImageTk.PhotoImage
except Exception:
	AnyPhotoImage: _TypeAlias = _tk.PhotoImage # type: ignore

WidgetState = _Literal['normal', 'disabled']

Relief = _Literal['raised', 'sunken', 'flat', 'ridge', 'solid', 'groove']

Anchor = _Literal['n', 's', 'w', 'e', 'nw', 'sw', 'ne', 'se', 'ns', 'ew', 'nsew', 'center']

Sticky = _Literal['n', 's', 'w', 'e', 'nw', 'sw', 'ne', 'se', 'ns', 'ew', 'nsew', 'center']

# Fill = _Literal['none', 'x', 'y', 'both']

# Side = _Literal['left', 'top', 'right', 'bottom']

SelectMode = _Literal['single', 'browse', 'multiple', 'extended']

MoveViewBy = _Literal['moveto', 'scroll', 'units', 'pages']

Comparitors = _Literal['<', '<=', '==', '>=', '>', '!=']
