
from utils import BASE_DIR
from Hotlink import Hotlink

from Tkinter import *

import os

class DependencyError(Tk):
	def __init__(self, prog, msg, hotlink=None):
		#Window
		Tk.__init__(self)
		self.resizable(False,False)
		self.title('Dependency Error')
		try:
			self.icon = os.path.join(BASE_DIR,'Images','%s.ico' % prog)
			self.wm_iconbitmap(self.icon)
		except:
			self.icon = '@%s' % os.path.join(BASE_DIR, 'Images','%s.xbm' % prog)
			self.wm_iconbitmap(self.icon)
		Label(self, text=msg, anchor=W, justify=LEFT).pack(side=TOP,pady=2,padx=2)
		if hotlink:
			f = Frame(self)
			Hotlink(f, *hotlink).pack(side=RIGHT, padx=10, pady=2)
			f.pack(side=TOP,fill=X)
		Button(self, text='Ok', width=10, command=self.destroy).pack(side=TOP, pady=2)
		self.update_idletasks()
		w,h = self.winfo_width(),self.winfo_height()
		self.geometry('%ix%i+%i+%i' % (w,h,(self.winfo_screenwidth() - w)/2,(self.winfo_screenheight() - h)/2))
