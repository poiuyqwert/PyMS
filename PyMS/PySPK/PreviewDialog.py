
from ..FileFormats import SPK

from ..Utilities.UIKit import *
from ..Utilities.PyMSDialog import PyMSDialog

class PreviewDialog(PyMSDialog):
	MAP_WIDTH = 32*256
	MAP_HEIGHT = 32*256

	def __init__(self, parent):
		self.items = {}
		self.last_x = None
		self.last_y = None
		PyMSDialog.__init__(self, parent, 'Parallax Preview', center=False, resizable=(False, False))

	def widgetize(self):
		self.canvas = Canvas(self, background='#000000', highlightthickness=0, width=640, height=480, scrollregion=(0,0,PreviewDialog.MAP_WIDTH,PreviewDialog.MAP_HEIGHT))
		self.canvas.grid(row=0,column=0)
		xscrollbar = Scrollbar(self, orient=HORIZONTAL, command=self.canvas.xview)
		xscrollbar.grid(row=1,column=0, sticky=EW)
		yscrollbar = Scrollbar(self, command=self.canvas.yview)
		yscrollbar.grid(row=0,column=1, sticky=NS)
		def scroll(l,h,bar):
			bar.set(l,h)
			self.update_viewport()
		self.canvas.config(xscrollcommand=lambda l,h,s=xscrollbar: scroll(l,h,s),yscrollcommand=lambda l,h,s=yscrollbar: scroll(l,h,s))
		self.grid_rowconfigure(0,weight=1)
		self.grid_columnconfigure(0,weight=1)

		self.canvas.focus_set()
		def scroll_map(event=None, horizontal=None,delta=None):
			if event:
				horizontal = False
				if hasattr(event, 'state') and getattr(event, 'state', 0):
					horizontal = True
				delta = event.delta
			view = self.canvas.yview
			if horizontal:
				view = self.canvas.xview
			if delta > 0:
				view('scroll', -1, 'units')
			else:
				view('scroll', 1, 'units')
			self.update_viewport()
		self.canvas.bind(Mouse.Scroll, scroll_map)
		self.bind(Key.Up, lambda e: scroll_map(None, False,1))
		self.bind(Key.Down, lambda e: scroll_map(None, False,-1))
		self.bind(Key.Left, lambda e: scroll_map(None, True,1))
		self.bind(Key.Right, lambda e: scroll_map(None, True,-1))

		self.parent.settings.windows.load_window_size('preview', self)

		self.load_viewport()

	def load_viewport(self):
		for layer in self.parent.spk.layers:
			for star in layer.stars:
				image = self.parent.get_image(star.image)
				item = self.canvas.create_image(star.x,star.y, image=image, anchor=NW)
				self.items[star] = item

	def update_viewport(self):
		if len(self.items):
			x = int(PreviewDialog.MAP_WIDTH * self.canvas.xview()[0])
			y = int(PreviewDialog.MAP_HEIGHT * self.canvas.yview()[0])
			if x != self.last_x or y != self.last_y:
				self.last_x = x
				self.last_y = y
				for l,layer in enumerate(self.parent.spk.layers):
					ratio = SPK.SPK.PARALLAX_RATIOS[l]
					ox = int(x * ratio) % 640
					oy = int(y * ratio) % 480
					for star in layer.stars:
						px = star.x - ox
						if px < 0:
							px += 640
						py = star.y - oy
						if py < 0:
							py += 480
						self.canvas.coords(self.items[star], x+px,y+py)

	def cancel(self):
		self.parent.settings.windows.save_window_size('preview', self)
		PyMSDialog.cancel(self)
