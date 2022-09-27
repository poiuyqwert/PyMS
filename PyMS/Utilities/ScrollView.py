
from .UIKit import *
from .AutohideScrollbar import AutohideScrollbar
from .EventPattern import *


# WARNING: You must use the `scrollView.content_view` as the master of the widgets placed into a ScrollView
# WARNING: ScrollView relies on `bind_all` for scrolling, only 1 can be used per window
class ScrollView(Frame):
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
		# self.bind(Mouse.Scroll, scroll)
		self.grid_rowconfigure(0,weight=1)
		self.grid_columnconfigure(0,weight=1)

		def resize(*_):
			self._content_area.config(scrollregion=self._content_area.bbox("all"))
		self.content_view.bind(WidgetEvent.Configure, resize)

		def bind_scroll(*_):
			self.bind_all(Mouse.Scroll, scroll)
		def unbind_scroll(*_):
			self.unbind_all(Mouse.Scroll)
		self.bind(WidgetEvent.Activate, bind_scroll)
		self.bind(WidgetEvent.Deactivate, unbind_scroll)
		self.bind(WidgetEvent.Map, bind_scroll)
		self.bind(WidgetEvent.Unmap, unbind_scroll)

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
		x,y,w,h = (int(v) for v in self._content_area.cget('scrollregion').split(' '))
		return (w,h)
	def content_offset(self):
		w,h = self.content_size()
		x = w * self._content_area.xview()[0]
		y = h * self._content_area.yview()[0]
		return (x,y)

	def scroll_to_view(self, view):
		if isinstance(view, Toplevel):
			return
		view_x1 = 0
		view_y1 = 0
		view_w = view.winfo_width()
		view_h = view.winfo_height()
		while view and view != self.content_view:
			view_x1 += view.winfo_x()
			view_y1 += view.winfo_y()
			parent = view.nametowidget(view.winfo_parent())
			if parent == view:
				break
			view = parent
		if view != self.content_view:
			return
		view_x2 = view_x1 + view_w
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

if __name__ == '__main__':
	from .UIKit import Font

	window = MainWindow()

	def add_scroll():
		scrollview = ScrollView(window, width=500,height=400)
		scrollview.grid()

		frame = Frame(scrollview.content_view)
		statframe = Frame(frame)
		l = LabelFrame(statframe, text='Vital Statistics')
		s = Frame(l)
		r = Frame(s)
		f = Frame(r)
		Label(f, text='Hit Points:', width=9, anchor=E).pack(side=LEFT)
		Entry(f, font=Font.fixed(), width=10).pack(side=LEFT)
		f.pack(side=LEFT)
		f = Frame(r)
		Label(f, text='Fraction:', anchor=E).pack(side=LEFT)
		Entry(f, font=Font.fixed(), width=3).pack(side=LEFT)
		f.pack(side=LEFT)
		r.pack(fill=X)
		f = Frame(s)
		x = Frame(f)
		Label(x, text='Shields:', width=9, anchor=E).pack(side=LEFT)
		Entry(x, font=Font.fixed(), width=10).pack(side=LEFT)
		x.pack(side=LEFT)
		x = Frame(f)
		Checkbutton(x, text='Enabled').pack(side=LEFT)
		x.pack(side=LEFT, fill=X)
		f.pack(fill=X)
		f = Frame(s)
		Label(f, text='Armor:', width=9, anchor=E).pack(side=LEFT)
		Entry(f, font=Font.fixed(), width=10).pack(side=LEFT)
		f.pack(fill=X)
		f = Frame(s)
		Label(f, text='Upgrade:', width=9, anchor=E).pack(side=LEFT)
		Entry(f, font=Font.fixed(), width=3).pack(side=LEFT)
		Label(f, text='=').pack(side=LEFT)
		Entry(f, font=Font.fixed(), width=20).pack(side=LEFT, fill=X, expand=1)
		Button(f, text='Jump ->').pack(side=LEFT)
		f.pack(fill=X)
		s.pack(fill=BOTH, padx=5, pady=5)
		l.pack(side=LEFT, fill=X, expand=1)

		l = LabelFrame(statframe, text='Build Cost')
		s = Frame(l)
		f = Frame(s)
		Label(f, text='Minerals:', width=9, anchor=E).pack(side=LEFT)
		Entry(f, font=Font.fixed(), width=5).pack(side=LEFT)
		f.pack(fill=X)
		f = Frame(s)
		Label(f, text='Vespene:', width=9, anchor=E).pack(side=LEFT)
		Entry(f, font=Font.fixed(), width=5).pack(side=LEFT)
		f.pack(fill=X)
		f = Frame(s)
		Label(f, text='Time:', width=9, anchor=E).pack(side=LEFT)
		Entry(f, font=Font.fixed(), width=5).pack(side=LEFT)
		Label(f, text='=').pack(side=LEFT)
		Entry(f, font=Font.fixed(), width=9).pack(side=LEFT)
		Label(f, text='secs.').pack(side=LEFT)
		f.pack(fill=X)
		c = Checkbutton(s, text='BroodWar')
		c.pack()
		s.pack(fill=BOTH, padx=5, pady=5)
		l.pack(side=LEFT, fill=BOTH)
		statframe.pack(fill=X)

		l = LabelFrame(frame, text='Weapons')
		s = Frame(l)
		f = Frame(s)
		Label(f, text='Ground:', width=9, anchor=E).pack(side=LEFT)
		Entry(f, font=Font.fixed(), width=3).pack(side=LEFT)
		Label(f, text='=').pack(side=LEFT)
		Entry(f, font=Font.fixed()).pack(side=LEFT, fill=X, expand=1, padx=2)
		Button(f, text='Jump ->').pack(side=LEFT)
		f.pack(fill=X)
		f = Frame(s)
		Label(f, text='Max Hits:', width=9, anchor=E).pack(side=LEFT)
		Entry(f, font=Font.fixed(), width=3).pack(side=LEFT)
		f.pack(fill=X)
		f = Frame(s)
		Label(f, text='Air:', width=9, anchor=E).pack(side=LEFT)
		Entry(f, font=Font.fixed(), width=3).pack(side=LEFT)
		Label(f, text='=').pack(side=LEFT)
		Entry(f, font=Font.fixed()).pack(side=LEFT, fill=X, expand=1, padx=2)
		Button(f, text='Jump ->').pack(side=LEFT)
		f.pack(fill=X)
		f = Frame(s)
		Label(f, text='Max Hits:', width=9, anchor=E).pack(side=LEFT)
		Entry(f, font=Font.fixed(), width=3).pack(side=LEFT)
		f.pack(fill=X)
		s.pack(fill=BOTH, padx=5, pady=5)
		l.pack(fill=X)

		ssframe = Frame(frame)
		l = LabelFrame(ssframe, text='Supply')
		s = Frame(l)
		f = Frame(s)
		Label(f, text='Required:', width=9, anchor=E).pack(side=LEFT)
		Entry(f, font=Font.fixed(), width=3).pack(side=LEFT)
		Checkbutton(f, text='+0.5').pack(side=LEFT)
		f.pack(fill=X)
		f = Frame(s)
		Label(f, text='Provided:', width=9, anchor=E).pack(side=LEFT)
		Entry(f, font=Font.fixed(), width=3).pack(side=LEFT)
		Checkbutton(f, text='+0.5').pack(side=LEFT)
		f.pack(fill=X)
		f = Frame(s)
		c = Checkbutton(f, text='Zerg')
		c.pack(side=LEFT)
		c = Checkbutton(f, text='Terran')
		c.pack(side=LEFT)
		c = Checkbutton(f, text='Protoss')
		c.pack(side=LEFT)
		f.pack()
		s.pack(fill=BOTH, padx=5, pady=5)
		l.pack(side=LEFT, fill=X, expand=1)

		l = LabelFrame(ssframe, text='Space')
		s = Frame(l)
		f = Frame(s)
		Label(f, text='Required:', width=9, anchor=E).pack(side=LEFT)
		Entry(f, font=Font.fixed(), width=3).pack(side=LEFT)
		f.pack(fill=X)
		f = Frame(s)
		Label(f, text='Provided:', width=9, anchor=E).pack(side=LEFT)
		Entry(f, font=Font.fixed(), width=3).pack(side=LEFT)
		f.pack(fill=X)
		s.pack(fill=BOTH, padx=5, pady=5)
		l.pack(side=LEFT, fill=BOTH, expand=1)

		l = LabelFrame(ssframe, text='Score')
		s = Frame(l)
		f = Frame(s)
		Label(f, text='Build:', width=9, anchor=E).pack(side=LEFT)
		Entry(f, font=Font.fixed(), width=5).pack(side=LEFT)
		f.pack(fill=X)
		f = Frame(s)
		Label(f, text='Destroy:', width=9, anchor=E).pack(side=LEFT)
		Entry(f, font=Font.fixed(), width=5).pack(side=LEFT)
		f.pack(fill=X)
		s.pack(fill=BOTH, padx=5, pady=5)
		l.pack(side=LEFT, fill=BOTH, expand=1)
		ssframe.pack(fill=X)

		otherframe = Frame(frame)
		l = LabelFrame(otherframe, text='Other')
		s = Frame(l)
		t = Frame(s)
		Label(t, text='Unit Size:', anchor=E).pack(side=LEFT)
		Entry(t, font=Font.fixed()).pack(side=LEFT, fill=X, expand=1)
		t.pack(side=LEFT, fill=X, expand=1)
		t = Frame(s)
		Label(t, text='Sight:', anchor=E).pack(side=LEFT)
		Entry(t, font=Font.fixed(), width=2).pack(side=LEFT)
		t.pack(side=LEFT)
		t = Frame(s)
		Label(t, text='Target Acquisition Range:', anchor=E).pack(side=LEFT)
		Entry(t, font=Font.fixed(), width=3).pack(side=LEFT)
		t.pack(side=LEFT)
		s.pack(fill=BOTH, padx=5, pady=5)
		l.pack(side=LEFT, fill=BOTH, expand=1)
		otherframe.pack(fill=X)

		frame.pack(side=LEFT, fill=Y, padx=5,pady=5)

	add_scroll()
	add_scroll()

	window.startup()
