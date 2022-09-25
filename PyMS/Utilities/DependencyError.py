
from . import Assets
from .Hotlink import Hotlink
from .UIKit import *

import os

class DependencyError(MainWindow):
	def __init__(self, prog, msg, hotlinks=None): # type: (str, str, list[tuple[str, str]] | None) -> DependencyError
		#Window
		MainWindow.__init__(self)
		self.resizable(False,False)
		self.title('Dependency Error')
		self.set_icon(prog)
		frame = Frame(self)
		frame.pack(side=TOP, padx=20,pady=20)
		Label(frame, text=msg, anchor=W, justify=LEFT).pack(side=TOP,pady=2,padx=2)
		if hotlinks:
			for hotlink in hotlinks:
				f = Frame(frame)
				Hotlink(f, *hotlink).pack(side=RIGHT, padx=10, pady=2)
				f.pack(side=TOP,fill=X)
		Button(frame, text='Ok', width=10, command=self.destroy).pack(side=TOP, pady=2)
		self.update_idletasks()
		w,h = self.winfo_width(),self.winfo_height()
		self.geometry('%ix%i+%i+%i' % (w,h,(self.winfo_screenwidth() - w)/2,(self.winfo_screenheight() - h)/2))
