
from .Widgets import *
from .Components import *
from .Variables import *
from .Colors import *
from .Font import *
from .Utils import *
from . import Theme
from .EventPattern import *
from .FileType import *
from .ShowScrollbar import *


try: # Python 2
	import tkinter.filedialog as FileDialog
	import tkinter.messagebox as MessageBox
	import tkinter.colorchooser as ColorChooser
except: # Python 3
	import tkinter.filedialog as FileDialog
	import tkinter.messagebox as MessageBox
	import tkinter.colorchooser as ColorChooser
# import Tkdnd


try:
	from PIL import Image as PILImage
	try:
		from PIL import ImageTk
	except:
		import ImageTk
except:
	class PILImage(object):
		pass
	class ImageTk(object):
		pass
