
try: # Python 2
	from Tkinter import *
	import tkFileDialog as FileDialog
	import tkMessageBox as MessageBox
	import tkColorChooser as ColorChooser
except: # Python 3
	from tkinter import * 
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

from .EventPattern import *

# TkinterExt wraps some Tkinter widgets to provide extensions
from .TkinterExt import *
