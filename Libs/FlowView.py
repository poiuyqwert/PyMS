
from Tkinter import *

class AutohideScrollbar(Scrollbar):
	def set(self, lo, hi):
		if float(lo) <= 0.0 and float(hi) >= 1.0:
			self.grid_remove()
		else:
			self.grid()
		Scrollbar.set(self, lo, hi)

class FlowView(Frame):
	def __init__(self, parent, **config):
		Frame.__init__(self, parent, **config)

		content_area = Frame(self)
		self.content_view = Canvas(content_area, scrollregion=(0,0,0,0), highlightthickness=0)
		self.content_view.pack(fill=BOTH, expand=1)
		content_area.grid(sticky=NSEW)
		xscrollbar = AutohideScrollbar(self, orient=HORIZONTAL, command=self.content_view.xview)
		xscrollbar.grid(sticky=EW)
		yscrollbar = AutohideScrollbar(self, command=self.content_view.yview)
		yscrollbar.grid(sticky=NS, row=0, column=1)
		def scrolled(l,h,bar):
			bar.set(l,h)
			# self.update_viewport()
		self.content_view.config(xscrollcommand=lambda l,h,s=xscrollbar: scrolled(l,h,s),yscrollcommand=lambda l,h,s=yscrollbar: scrolled(l,h,s))
		def scroll(event):
			horizontal = False
			if hasattr(event, 'state') and getattr(event, 'state', 0):
				horizontal = True
			view = self.content_view.yview
			if horizontal:
				view = self.content_view.xview
			if event.delta > 0:
				# for some reason I can scroll past the left side but xview doesn't actually change, so just don't scroll past 0
				if not horizontal or self.content_view.xview()[0] > 0:
					view('scroll', -1, 'units')
			else:
				view('scroll', 1, 'units')
			print self.content_view.xview(),self.content_view.yview()
		self.bind_all('<MouseWheel>', scroll)
		self.grid_rowconfigure(0,weight=1)
		self.grid_columnconfigure(0,weight=1)

		self._staging_view = Frame(self.content_view)
		self._staging_view.place()

		self.subviews = []
		self._sizes = {}
		self._size_adjustments = {}
		self._subview_configs = {}
		self._bindings = {}
		self._update = False
		# self._updates = 0
		self.bind('<<Update>>', self._update_layout)
		self._viewport_size = (0,0)
		def resize(*_):
			viewport_size = (self.content_view.winfo_width(), self.content_view.winfo_height())
			if viewport_size != self._viewport_size:
				self._viewport_size = viewport_size
				self.set_needs_update()
		self.content_view.bind('<Configure>', resize)

	def content_size(self):
		x,y,w,h = (int(v) for v in self.content_view.cget('scrollregion').split(' '))
		return (w,h)

	def set_needs_update(self):
		# import inspect
		# print inspect.stack()[1][3]
		self._update = True
		self.event_generate('<<Update>>')

	# WARNING: You must use the `content_view` as the master of the widgets placed into a FlowView
	# padx/y can be None, an Int, or a 2 len tuple combination of them
	def add_subview(self, view, padx=0,pady=0, weight=0):
		self.subviews.append(view)
		if not isinstance(padx, tuple):
			padx = (padx,padx)
		if not isinstance(pady, tuple):
			pady = (pady,pady)
		name = str(view)
		self._subview_configs[name] = {
			'padx': padx,
			'pady': pady,
			'weight': weight
		}
		self._subview_configs[name]
		view.grid(in_=self._staging_view)
		self._update_view_size(view, update_idletasks=True)
		self._bindings[name] = view.bind('<Configure>', lambda *_: self._update_view_size(view, set_needs_update=True), True)
		self.set_needs_update()

	def remove_subview(self, view):
		if not view in self.subviews:
			return
		name = str(view)
		self.content_view.delete(name)
		view.unbind('<Configure>', self._bindings[name])
		del self._bindings[name]
		del self._sizes[name]
		del self._subview_configs[name]
		self.subviews.remove(view)
		self.set_needs_update()

	def _update_view_size(self, view, update_idletasks=False, set_needs_update=False):
		if update_idletasks:
			view.update_idletasks()
		name = str(view)
		size = (view.winfo_reqwidth(), view.winfo_reqheight())
		changed = True
		if name in self._sizes:
			changed = size != self._sizes[name]
		self._sizes[name] = size
		if changed and set_needs_update:
			self.set_needs_update()
	def _update_layout(self, *_):
		if not self._update:
			return
		self._update = False
		# self._updates += 1
		# print 'update %d' % self._updates
		max_w = self.content_view.winfo_width() - 10
		# print max_w
		x = 0
		y = 0
		w = 0
		rows = [[]]
		row_widths = []
		row_h = 0
		def place(view, x,y, width):
			name = str(view)
			# improve check?
			if self.content_view.find_withtag(name):
				self.content_view.coords(name, (x,y))
				self.content_view.itemconfig(name, width=width)
			else:
				self.content_view.create_window((x,y), window=view, anchor=NW, tags=name, width=width)
		for view in self.subviews:
			name = str(view)
			if not name in self._sizes:
				self._update_view_size(view, update_idletasks=True)
			view_w_real,view_h = self._sizes[name]
			padx_l,padx_r = self._subview_configs[name]['padx']
			pady_t,pady_b = self._subview_configs[name]['pady']
			weight = self._subview_configs[name]['weight']
			view_w = view_w_real+padx_l+padx_r
			view_h += pady_t+pady_b
			if x > 0 and x+view_w > max_w:
				w = max(w,x)
				row_widths.append(x)
				x = 0
				y += row_h
				rows.append([])
				row_h = 0
			rows[-1].append([view,x+padx_l,y+pady_t,view_w_real,weight])
			if x == 0 and view_w > max_w:
				w = max(w,view_w)
				row_widths.append(view_w)
				y += view_h
				rows.append([])
			else:
				x += view_w
				row_h = max(row_h, view_h)
		if x:
			row_widths.append(x)
		total_w = 0
		total_h = y + row_h
		for row,row_width in zip(rows,row_widths):
			if row_width < max_w:
				total = 0.0
				for _,_,_,_,weight in row:
					total += weight
				if total:
					distrubute = max_w - row_width
					add_widths = tuple(int(col[4] / total * distrubute) for col in row)
					offset = 0
					for n in range(len(row)):
						row[n][1] += offset
						row[n][3] += add_widths[n]
						offset += add_widths[n]
			for view,x,y,w,_ in row:
				total_w = max(total_w,w)
				place(view, x,y, w)
		self.content_view.config(scrollregion=(0,0,total_w,total_h))

if __name__ == '__main__':
	import random,string

	window = Tk()
	flow = FlowView(window, borderwidth=2, relief=SUNKEN, width=500,height=350)
	flow.pack(fill=BOTH, expand=1, padx=30,pady=30)
	count = random.randint(10,20)
	print count
	for n in range(count):
		f = LabelFrame(flow.content_view, text=''.join([random.choice(string.lowercase + ' ') for i in xrange(random.randint(10,20))]))
		for t in range(random.randint(1,5)):
			if t == 3:
				e = Entry(f, width=5)
				e.pack()
			l = Label(f, text=''.join([random.choice(string.lowercase + ' ') for i in xrange(random.randint(10,20))]))
			l.pack()
		flow.add_subview(f, padx=2,pady=2, weight=0 if n % 5 else 1)
	window.mainloop()
