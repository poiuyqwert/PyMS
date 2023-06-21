
from .Components.MainWindow import MainWindow as _MainWindow
from .Widgets import Toplevel as _Toplevel

from typing import TypeAlias as _TypeAlias
from typing import Literal as _Literal

AnyWindow: _TypeAlias = _MainWindow | _Toplevel

WidgetState = _Literal['normal', 'disabled']

Relief = _Literal['raised', 'sunken', 'flat', 'ridge', 'solid', 'groove']

Anchor = _Literal['n', 's', 'w', 'e', 'nw', 'sw', 'ne', 'se', 'ns', 'ew', 'nsew', 'center']

Sticky = _Literal['n', 's', 'w', 'e', 'nw', 'sw', 'ne', 'se', 'ns', 'ew', 'nsew', 'center']

# Fill = _Literal['none', 'x', 'y', 'both']

# Side = _Literal['left', 'top', 'right', 'bottom']

SelectMode = _Literal['single', 'browse', 'multiple', 'extended']
