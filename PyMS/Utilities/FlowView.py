
from .AutohideScrollbar import AutohideScrollbar
from .UIKit import *


# WARNING: You must use the `flowView.content_view` as the master of the widgets placed into a FlowView
# TODO: Subclass ScrollView?
class FlowView(Frame):
	def __init__(self, parent, **config):
		Frame.__init__(self, parent, **config)

		self._content_area = Canvas(self, scrollregion=(0,0,0,0), highlightthickness=0)
		self.content_view = Frame(self._content_area)
		self.content_view_id = self._content_area.create_window(0, 0, window=self.content_view, anchor=NW)
		self._content_area.grid(sticky=NSEW)
		xscrollbar = AutohideScrollbar(self, orient=HORIZONTAL, command=self._content_area.xview)
		xscrollbar.grid(sticky=EW)
		yscrollbar = AutohideScrollbar(self, command=self._content_area.yview)
		yscrollbar.grid(sticky=NS, row=0, column=1)
		def scrolled(l,h,bar):
			bar.set(l,h)
			# self.update_viewport()
		self._content_area.config(xscrollcommand=lambda l,h,s=xscrollbar: scrolled(l,h,s),yscrollcommand=lambda l,h,s=yscrollbar: scrolled(l,h,s))
		def scroll(event):
			horizontal = False
			if hasattr(event, 'state') and getattr(event, 'state', 0) & Modifier.Shift.state:
				horizontal = True
			view = self._content_area.yview
			if horizontal:
				view = self._content_area.xview
			cur = view()
			if event.delta > 0 and cur[0] > 0:
				view('scroll', -1, 'units')
			elif event.delta <= 0 and cur[1] < 1:
				view('scroll', 1, 'units')
		self.bind_all(Mouse.Scroll, scroll)
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
		self.bind('<<Update>>', self._update_layout)
		self._viewport_widths = []
		def resize(*_):
			viewport_width = self.viewport_size()[0]
			if not viewport_width in self._viewport_widths or self._viewport_widths.count(viewport_width) < 2:
				self._viewport_widths.append(viewport_width)
				if len(self._viewport_widths) > 3:
					del self._viewport_widths[0]
				self.set_needs_update()
		self._content_area.bind(WidgetEvent.Configure, resize)

		self._focus_bind_info = None
		def check_focus():
			focused = self.content_view.focus_displayof()
			if self._focus_bind_info:
				view,bind_id = self._focus_bind_info
				try:
					view.unbind(Focus.Out, bind_id)
				except:
					pass
				self._focus_bind_info = None
			def focus_out(*_):
				check_focus()
			if focused:
				self._focus_bind_info = (focused,focused.bind(Focus.Out, focus_out, True))
				self.scroll_to_view(focused)
		def focus_in(*_):
			check_focus()
		self.content_view.bind(Focus.In, focus_in)

	def viewport_size(self):
		return (self._content_area.winfo_width(), self._content_area.winfo_height())
	def content_size(self):
		_,_,w,h = (int(v) for v in self._content_area.cget('scrollregion').split(' '))
		return (w,h)
	def content_offset(self):
		w,h = self.content_size()
		x = w * self._content_area.xview()[0]
		y = h * self._content_area.yview()[0]
		return (x,y)

	def set_needs_update(self):
		# import inspect
		# print(inspect.stack()[1][3])
		self._update = True
		self.event_generate('<<Update>>')

	def scroll_to_view(self, view):
		offset_x = 0
		offset_y = 0
		view_w = view.winfo_width()
		view_h = view.winfo_height()
		while not view in self.subviews:
			offset_x += view.winfo_x()
			offset_y += view.winfo_y()
			parent = view.nametowidget(view.winfo_parent())
			if not parent or parent == view:
				return
			view = parent
		view_x1 = view.winfo_x() + offset_x
		view_x2 = view_x1 + view_w
		view_y1 = view.winfo_y() + offset_y
		view_y2 = view_y1 + view_h
		viewport_x1,viewport_y1 = self.content_offset()
		viewport_w,viewport_h = self.viewport_size()
		viewport_x2 = viewport_x1 + viewport_w
		viewport_y2 = viewport_y1 + viewport_h
		content_w,content_h = self.content_size()
		if view_x1 < viewport_x1:
			self._content_area.xview_moveto(view_x1 / float(content_w))
		elif view_x2 > viewport_x2:
			xview = list(self._content_area.xview())
			x_span = xview[1] - xview[0]
			self._content_area.xview_moveto(view_x2 / float(content_w) - x_span)
		if view_y1 < viewport_y1:
			self._content_area.yview_moveto(view_y1 / float(content_h))
		elif view_y2 > viewport_y2:
			yview = list(self._content_area.yview())
			y_span = yview[1] - yview[0]
			self._content_area.yview_moveto(view_y2 / float(content_h) - y_span)

	def _insert_subview(self, index, view, padx=0,pady=0, weight=0):
		self.subviews.insert(index, view)
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
		self._bindings[name] = view.bind(WidgetEvent.Configure, lambda *_: self._update_view_size(view, set_needs_update=True), True)

	def insert_subview(self, index, view, padx=0,pady=0, weight=0):
		self._insert_subview(index, view, padx=padx,pady=pady, weight=weight)
		self.set_needs_update()

	def insert_subviews(self, index, views, padx=0,pady=0, weight=0):
		for view in reversed(views):
			self._insert_subview(index, view, padx=padx,pady=pady, weight=weight)
		self.set_needs_update()

	def add_subview(self, view, padx=0,pady=0, weight=0):
		self.insert_subview(len(self.subviews), view, padx=padx,pady=pady, weight=weight)

	def add_subviews(self, views, padx=0,pady=0, weight=0):
		self.insert_subviews(len(self.subviews), views, padx=padx,pady=pady, weight=weight)

	def _remove_subview(self, view):
		if not view in self.subviews:
			return
		name = str(view)
		view.place_forget()
		view.unbind(WidgetEvent.Configure, self._bindings[name])
		del self._bindings[name]
		del self._sizes[name]
		del self._subview_configs[name]
		self.subviews.remove(view)

	def remove_subview(self, view):
		self._remove_subview(view)
		self.set_needs_update()

	def remove_subviews(self, views):
		for view in views:
			self._remove_subview(view)
		self.set_needs_update()

	def remove_all_subviews(self):
		self.remove_subviews(list(self.subviews))

	def update_subview_config(self, view, padx=None,pady=None, weight=None):
		if not view in self.subviews:
			return
		name = str(view)
		if padx != None:
			self._subview_configs[name]['padx'] = padx
		if pady != None:
			self._subview_configs[name]['pady'] = pady
		if weight != None:
			self._subview_configs[name]['weight'] = weight
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
		max_w = self._content_area.winfo_width()
		# print(max_w)
		x = 0
		y = 0
		w = 0
		rows = [[]]
		row_widths = []
		row_h = 0
		def place(view, x,y, width):
			view.place(x=x, y=y, width=width)
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
				total_weight = 0.0
				for _,_,_,_,weight in row:
					total_weight += weight
				if total_weight:
					distrubute = max_w - row_width
					add_widths = tuple(int(col[4] / total_weight * distrubute) for col in row)
					offset = 0
					for n in range(len(row)):
						row[n][1] += offset
						row[n][3] += add_widths[n]
						offset += add_widths[n]
				row_width = max_w
			total_w = max(total_w,row_width)
			for view,x,y,w,_ in row:
				place(view, x,y, w)
		# print(total_w,total_h)
		self._content_area.itemconfig(self.content_view_id, width=total_w,height=total_h)
		self._content_area.config(scrollregion=(0,0,total_w,total_h))

if __name__ == '__main__':
	import random,string

	window = Tk()
	flow = FlowView(window, borderwidth=2, relief=SUNKEN, width=500,height=350)
	flow.pack(fill=BOTH, expand=1, padx=30,pady=30)
	count = random.randint(10,20)
	for n in range(count):
		f = LabelFrame(flow.content_view, text=''.join([random.choice(string.lowercase + ' ') for i in range(random.randint(10,20))]))
		for t in range(random.randint(1,5)):
			if t == 3:
				e = Entry(f, width=5)
				e.pack()
			l = Label(f, text=''.join([random.choice(string.lowercase + ' ') for i in range(random.randint(10,20))]))
			l.pack()
		flow.add_subview(f, padx=2,pady=2, weight=0 if n % 5 else 1)
	flow.scroll_to_view(flow)
	window.mainloop()
