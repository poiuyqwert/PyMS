
from Tkinter import *


class FlowView(Frame):
	def __init__(self, parent, **config):
		Frame.__init__(self, parent, **config)

		self._canvas = Canvas(self)
		self._canvas.grid(sticky=NSEW)
		xscrollbar = Scrollbar(self, orient=HORIZONTAL, command=self._canvas.xview)
		xscrollbar.grid(sticky=EW)
		yscrollbar = Scrollbar(self, command=self._canvas.yview)
		yscrollbar.grid(sticky=NS, row=0, column=1)
		def scroll(l,h,bar):
			bar.set(l,h)
			# self.update_viewport()
		self._canvas.config(xscrollcommand=lambda l,h,s=xscrollbar: scroll(l,h,s),yscrollcommand=lambda l,h,s=yscrollbar: scroll(l,h,s))
		self.grid_rowconfigure(0,weight=1)
		self.grid_columnconfigure(0,weight=1)

		self.subviews = []
		self._sizes = {}
		self._paddings = {}
		self._bindings = {}
		self._update = False
		self.bind('<<Update>>', self._update_layout)
		# self.event_add('<<Update>>', '<Configure>')
		self._canvas.bind('<Configure>', lambda *_: self.set_needs_update())

	def set_needs_update(self):
		self._update = True
		self.event_generate('<<Update>>')

	# padx/y can be None, an Int, or a 2 len tuple combination of them
	def add_subview(self, view, padx=None,pady=None):
		self.subviews.append(view)
		padx_l = padx
		padx_r = padx
		if isinstance(padx, tuple):
			padx_l,padx_r = padx
		pady_t = pady
		pady_b = pady
		if isinstance(pady, tuple):
			pady_t,pady_b = pady
		name = str(view)
		self._paddings[name] = (padx_l or 0,padx_r or 0, pady_t or 0,pady_b or 0)
		self._update_view_size(view, update_idletasks=True)
		self._bindings[name] = view.bind('<Configure>', lambda *_: self._update_view_size(view, set_needs_update=True), True)
		self.set_needs_update()

	def remove_subview(self, view):
		if not view in self.subviews:
			return
		name = str(view)
		self._canvas.delete(name)
		view.unbind('<Configure>', self._bindings[name])
		del self._bindings[name]
		del self._sizes[name]
		del self._paddings[name]
		self.subviews.remove(view)
		self.set_needs_update()

	def _update_view_size(self, view, update_idletasks=False, set_needs_update=False):
		if update_idletasks:
			view.update_idletasks()
		self._sizes[str(view)] = (view.winfo_width(), view.winfo_height())
		if set_needs_update:
			self.set_needs_update()
	def _update_layout(self, *_):
		if not self._update:
			return
		self._update = False
		print 'update'
		max_w = self._canvas.winfo_width()
		x = 0
		y = 0
		w = 0
		row_h = 0
		def place(view, x,y):
			name = str(view)
			if self._canvas.find_withtag(name):
				self._canvas.coords(name, (x,y))
			else:
				self._canvas.create_window((x,y), window=view, anchor=NW, tags=name)
		for view in self.subviews:
			name = str(view)
			if not name in self._sizes:
				self._update_view_size(view, update_idletasks=True)
			view_w,view_h = self._sizes[name]
			padx_l,padx_r, pady_t,pady_b = self._paddings[name]
			view_w += padx_l+padx_r
			view_h += pady_t+pady_b
			if x > 0 and x+view_w > max_w:
				w = max(w,x)
				x = 0
				y += row_h
				row_h = 0
			if x == 0 and view_w > max_w:
				w = max(w,view_w)
				place(view, padx_l,y+pady_t)
				y += view_h
			else:
				place(view, x+padx_l,y+pady_t)
				x += view_w
				row_h = max(row_h, view_h)
		h = y + row_h
		self._canvas.config(scrollregion=(0,0,w,h))

if __name__ == '__main__':
	import random,string

	window = Tk()
	flow = FlowView(window, borderwidth=2, relief=SUNKEN, width=500,height=350)
	flow.pack(fill=BOTH, expand=1, padx=30,pady=30)
	for n in range(random.randint(10,20)):
		f = LabelFrame(text=''.join([random.choice(string.lowercase + ' ') for i in xrange(random.randint(10,20))]))
		l = Label(f, text=''.join([random.choice(string.lowercase + ' ') for i in xrange(random.randint(10,20))]))
		l.pack()
		flow.add_subview(f, padx=2,pady=2)
	window.mainloop()
