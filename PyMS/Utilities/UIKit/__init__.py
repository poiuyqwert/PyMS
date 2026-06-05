
# This package is the public-API barrel: the `*` re-exports are deliberate, each
# backed by an `__all__` in the submodule. (Wildcards elsewhere were removed.)
# pylint: disable=wildcard-import,unused-wildcard-import

from tkinter import Event

from .Constants import *
from .Variables import *
from .Images import *
from .Widgets import *
from .Components import *
from .Colors import *
from .Font import *
from .Utils import *
from . import Theme
from .EventPattern import *
from .FileType import *
from .ShowScrollbar import *
from .Types import *
from .SyntaxHighlighting import *

import tkinter.filedialog as FileDialog
import tkinter.messagebox as MessageBox
import tkinter.colorchooser as ColorChooser

from tkinter import Tcl
from tkinter.ttk import Style
READONLY = 'readonly'

try:
	from PIL import Image as PILImage
	from PIL import ImageTk
except Exception:
	pass
