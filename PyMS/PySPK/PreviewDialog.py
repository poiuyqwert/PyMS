
from .Delegates import MainDelegate

from ..FileFormats import SPK

from ..Utilities.UIKit import *
from ..Utilities.PyMSDialog import PyMSDialog

from typing import Callable

class PreviewDialog(PyMSDialog):
	MAP_WIDTH = 32*256
	MAP_HEIGHT = 32*256

	def __init__(self, parent: Misc, delegate: MainDelegate) -> None:
		self.delegate = delegate
		self.items: dict[SPK.SPKStar, Canvas.Item] = {} # type: ignore[name-defined]
		self.last_x: int | None = None
		self.last_y: int | None = None
		PyMSDialog.__init__(self, parent, 'Parallax Preview', center=False, resizable=(False, False))

	def widgetize(self) -> (Misc | None):
		self.canvas = Canvas(self, background='#000000', highlightthickness=0, width=640, height=480, scrollregion=(0,0,PreviewDialog.MAP_WIDTH,PreviewDialog.MAP_HEIGHT), theme_tag='preview') # type: ignore[call-arg]
		self.canvas.grid(row=0,column=0)
		xscrollbar = Scrollbar(self, orient=HORIZONTAL, command=self.canvas.xview)
		xscrollbar.grid(row=1,column=0, sticky=EW)
		yscrollbar = Scrollbar(self, command=self.canvas.yview)
		yscrollbar.grid(row=0,column=1, sticky=NS)
		def scroll_callback(scrollbar: Scrollbar) -> Callable[[float, float], None]:
			def scroll(l,h):
				scrollbar.set(l,h)
				self.update_viewport()
			return scroll
		self.canvas.config(xscrollcommand=scroll_callback(xscrollbar),yscrollcommand=scroll_callback(yscrollbar))
		self.grid_rowconfigure(0,weight=1)
		self.grid_columnconfigure(0,weight=1)

		self.canvas.focus_set()
		def scroll_map(event: Event | None = None, horizontal: bool = False, delta: int = 0):
			if event:
				horizontal = False
				if hasattr(event, 'state') and getattr(event, 'state', 0) & Modifier.Shift.state:
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
		self.canvas.bind(Mouse.Scroll(), scroll_map)
		self.bind(Key.Up(), lambda e: scroll_map(None, False, 1))
		self.bind(Key.Down(), lambda e: scroll_map(None, False, -1))
		self.bind(Key.Left(), lambda e: scroll_map(None, True, 1))
		self.bind(Key.Right(), lambda e: scroll_map(None, True, -1))

		return None

	def setup_complete(self) -> None:
		self.delegate.config_.windows.preview.load(self)

		self.load_viewport()

	def load_viewport(self) -> None:
		if not self.delegate.spk:
			return
		for layer in self.delegate.spk.layers:
			for star in layer.stars:
				image = self.delegate.get_image(star.image)
				item = self.canvas.create_image(star.x,star.y, image=image, anchor=NW)
				self.items[star] = item

	def update_viewport(self) -> None:
		if not len(self.items) or not self.delegate.spk:
			return
		x = int(PreviewDialog.MAP_WIDTH * self.canvas.xview()[0])
		y = int(PreviewDialog.MAP_HEIGHT * self.canvas.yview()[0])
		if x == self.last_x and y == self.last_y:
			return
		self.last_x = x
		self.last_y = y
		for l,layer in enumerate(self.delegate.spk.layers):
			ratio = SPK.SPK.PARALLAX_RATIOS[l]
			ox = int(x * ratio) % SPK.SPK.LAYER_SIZE[0]
			oy = int(y * ratio) % SPK.SPK.LAYER_SIZE[1]
			for star in layer.stars:
				px = star.x - ox
				if px < 0:
					px += SPK.SPK.LAYER_SIZE[0]
				py = star.y - oy
				if py < 0:
					py += SPK.SPK.LAYER_SIZE[1]
				px -= SPK.SPK.LAYER_ORIGIN[0]
				py -= SPK.SPK.LAYER_ORIGIN[1]
				self.canvas.coords(self.items[star], x+px,y+py)

	def dismiss(self) -> None:
		self.delegate.config_.windows.preview.save(self)
		PyMSDialog.dismiss(self)
