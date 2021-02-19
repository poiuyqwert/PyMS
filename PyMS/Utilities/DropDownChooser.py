
from utils import couriernew
from UIKit import *

class DropDownChooser(Toplevel):
	def __init__(self, parent, list, select):
		self.focus = 0
		self.parent = parent
		self.result = select
		Toplevel.__init__(self, parent, relief=SOLID, borderwidth=1)
		self.protocol('WM_LOSE_FOCUS', self.select)
		self.wm_overrideredirect(1)
		scrollbar = Scrollbar(self)
		self.listbox = Listbox(self, selectmode=SINGLE, height=min(10,len(list)), borderwidth=0, font=couriernew, highlightthickness=0, yscrollcommand=scrollbar.set, activestyle=DOTBOX)
		for e in list:
			self.listbox.insert(END,e)
		if self.result > -1:
			self.listbox.select_set(self.result)
			self.listbox.see(self.result)
		self.listbox.bind('<ButtonRelease-1>', self.select)
		bind = [
			('<Enter>', lambda e,i=1: self.enter(e,i)),
			('<Leave>', lambda e,i=0: self.enter(e,i)),
			('<Button-1>', self.focusout),
			('<Return>', self.select),
			('<Escape>', self.close),
			('<MouseWheel>', self.scroll),
			('<Home>', lambda a,i=0: self.move(a,i)),
			('<End>', lambda a,i=END: self.move(a,i)),
			('<Up>', lambda a,i=-1: self.move(a,i)),
			('<Left>', lambda a,i=-1: self.move(a,i)),
			('<Down>', lambda a,i=1: self.move(a,i)),
			('<Right>', lambda a,i=-1: self.move(a,i)),
			('<Prior>', lambda a,i=-10: self.move(a,i)),
			('<Next>', lambda a,i=10: self.move(a,i)),
		]
		for b in bind:
			self.bind(*b)
		scrollbar.config(command=self.listbox.yview)
		if len(list) > 10:
			scrollbar.pack(side=RIGHT, fill=Y)
		self.listbox.pack(side=LEFT, fill=BOTH, expand=1)
		self.focus_set()
		self.update_idletasks()
		size = self.parent.winfo_geometry().split('+',1)[0].split('x')
		if self.parent.winfo_rooty() + self.parent.winfo_reqheight() + self.winfo_reqheight() > self.winfo_screenheight():
			self.geometry('%sx%s+%d+%d' % (size[0],self.winfo_reqheight(),self.parent.winfo_rootx(), self.parent.winfo_rooty() - self.winfo_reqheight()))
		else:
			self.geometry('%sx%s+%d+%d' % (size[0],self.winfo_reqheight(),self.parent.winfo_rootx(), self.parent.winfo_rooty() + self.parent.winfo_reqheight()))
		self.grab_set()
		self.update_idletasks()
		self.wait_window(self)

	def enter(self, e, f):
		self.focus = f

	def focusout(self, e):
		if not self.focus:
			self.select()

	def move(self, e, a):
		if not a in [0,END]:
			a = max(min(self.listbox.size()-1,int(self.listbox.curselection()[0]) + a),0)
		self.listbox.select_clear(0,END)
		self.listbox.select_set(a)
		self.listbox.see(a)

	def scroll(self, e):
		if e.delta > 0:
			self.listbox.yview('scroll', -2, 'units')
		else:
			self.listbox.yview('scroll', 2, 'units')

	def home(self, e):
		self.listbox.yview('moveto', 0.0)

	def end(self, e):
		self.listbox.yview('moveto', 1.0)

	def up(self, e):
		self.listbox.yview('scroll', -1, 'units')

	def down(self, e):
		self.listbox.yview('scroll', 1, 'units')

	def pageup(self, e):
		self.listbox.yview('scroll', -1, 'pages')

	def pagedown(self, e):
		self.listbox.yview('scroll', 1, 'pages')

	def select(self, e=None):
		s = self.listbox.curselection()
		if s:
			self.result = int(s[0])
		self.close()

	def close(self, e=None):
		self.parent.focus_set()
		self.withdraw()
		self.update_idletasks()
		self.destroy()
