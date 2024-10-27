
from .Components.MainWindow import MainWindow as _MainWindow
from .Widgets import Toplevel as _Toplevel

from typing import TypeAlias as _TypeAlias
from typing import Literal as _Literal

import tkinter as _tk

AnyWindow: _TypeAlias = _MainWindow | _Toplevel

try:
	from PIL import Image as _PILImage
	from PIL import ImageTk as _ImageTk

	AnyImage = _tk.Image | _ImageTk.PhotoImage | _ImageTk.BitmapImage | _PILImage.Image
	AnyPhotoImage = _tk.PhotoImage | _ImageTk.PhotoImage | _PILImage.Image
	AnyBitmapImage = _tk.BitmapImage | _ImageTk.BitmapImage
except:
	AnyImage: _TypeAlias = _tk.Image # type: ignore
	AnyPhotoImage: _TypeAlias = _tk.PhotoImage # type: ignore
	AnyBitmapImage: _TypeAlias = _tk.BitmapImage # type: ignore

WidgetState = _Literal['normal', 'disabled']

Relief = _Literal['raised', 'sunken', 'flat', 'ridge', 'solid', 'groove']

Anchor = _Literal['n', 's', 'w', 'e', 'nw', 'sw', 'ne', 'se', 'ns', 'ew', 'nsew', 'center']

Sticky = _Literal['n', 's', 'w', 'e', 'nw', 'sw', 'ne', 'se', 'ns', 'ew', 'nsew', 'center']

# Fill = _Literal['none', 'x', 'y', 'both']

# Side = _Literal['left', 'top', 'right', 'bottom']

SelectMode = _Literal['single', 'browse', 'multiple', 'extended']

MoveViewBy = _Literal['moveto', 'scroll', 'units', 'pages']

Comparitors = _Literal['<', '<=', '==', '>=', '>', '!=']
