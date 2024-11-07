
from .Tool import Tool
from .Delegates import MainDelegate

from ..FileFormats import SPK
from ..FileFormats import BMP

from ..Utilities.UIKit import *
from ..Utilities import Assets
from ..Utilities.PyMSError import PyMSError
from ..Utilities.ErrorDialog import ErrorDialog

class PaletteTab(NotebookTab):
	MAX_SIZE = 150
	PAD = 10

	def __init__(self, parent: Misc, delegate: MainDelegate, bind_target: Misc):
		self.delegate = delegate
		self.item_palette_box = None
		NotebookTab.__init__(self, parent)

		scrollframe = Frame(self, bd=2, relief=SUNKEN)
		self.starsCanvas = Canvas(scrollframe, background='#000000', highlightthickness=0, width=PaletteTab.MAX_SIZE+PaletteTab.PAD*2, theme_tag='preview') # type: ignore[call-arg]
		def scroll_palette(event):
			if self.toplevel.spk:
				if event.delta > 0:
					self.starsCanvas.yview('scroll', -1, 'units')
				else:
					self.starsCanvas.yview('scroll', 1, 'units')
		self.starsCanvas.bind(Mouse.Scroll(), scroll_palette)
		self.starsCanvas.bind(Mouse.Click_Left(), self.palette_select)
		self.starsCanvas.pack(side=LEFT, fill=Y, expand=1)
		scrollbar = Scrollbar(scrollframe, command=self.starsCanvas.yview)
		self.starsCanvas.config(yscrollcommand=scrollbar.set)
		scrollbar.pack(side=LEFT, fill=Y, expand=1)
		scrollframe.pack(side=TOP, padx=2, fill=Y, expand=1)

		self.toolbar = Toolbar(self, bind_target=bind_target)
		self.toolbar.add_radiobutton(Assets.get_image('select'), self.delegate.tool, Tool.select, 'Select', Key.m, enabled=False, tags='file_open')
		self.toolbar.add_radiobutton(Assets.get_image('arrows'), self.delegate.tool, Tool.move, 'Move', Key.v, enabled=False, tags='file_open')
		self.toolbar.add_radiobutton(Assets.get_image('pencil'), self.delegate.tool, Tool.draw, 'Draw', Key.p, enabled=False, tags='file_open')
		self.toolbar.add_spacer(2, flexible=True)
		self.toolbar.add_button(Assets.get_image('exportc'), self.export_image, 'Export Star', enabled=False, tags='image_selected')
		self.toolbar.add_button(Assets.get_image('importc'), self.import_image, 'Import Star', enabled=False, tags='file_open')
		self.toolbar.pack(side=TOP, fill=X, padx=2, pady=(2,0))

	def action_states(self) -> None:
		self.toolbar.tag_enabled('file_open', self.delegate.is_file_open())
		self.toolbar.tag_enabled('image_selected', self.delegate.is_image_selected())

	def reload_palette(self, scroll: bool = True) -> None:
		y = 0
		if self.delegate.spk:
			for img in self.delegate.spk.images:
				height = min(img.height,PaletteTab.MAX_SIZE)+PaletteTab.PAD*2
				image = self.delegate.get_image(img)

				self.starsCanvas.create_image(PaletteTab.MAX_SIZE//2+PaletteTab.PAD,y + height//2, image=image)
				y += height
		self.starsCanvas.config(scrollregion=(0,0,PaletteTab.MAX_SIZE,y))
		self.update_palette_selection(scroll)

	def update_palette_selection(self, scroll: bool = False) -> None:
		if self.delegate.spk and self.delegate.selected_image:
			index = self.delegate.spk.images.index(self.delegate.selected_image)
			y = 0
			height = 0
			for i,img in enumerate(self.delegate.spk.images):
				height = min(img.height,PaletteTab.MAX_SIZE)+PaletteTab.PAD*2
				if i == index:
					break
				y += height
			x2 = PaletteTab.MAX_SIZE+PaletteTab.PAD*2-1
			y2 = y+height-1
			if self.item_palette_box:
				self.starsCanvas.coords(self.item_palette_box, 0,y, x2,y2)
			else:
				self.item_palette_box = self.starsCanvas.create_rectangle(0,y, x2,y2, width=1, outline='#FFFFFF') # type: ignore[assignment]
			if scroll:
				miny,maxy = self.starsCanvas.yview()
				area = maxy-miny
				maxy = 1-area
				center = y + (y2-y)//2
				_,_,_,height = parse_scrollregion(self.starsCanvas.cget('scrollregion'))
				vis = height * area
				top = center - vis//2
				y = int(top / float(height))
				self.starsCanvas.yview_moveto(y)
		elif self.item_palette_box:
			self.starsCanvas.delete(self.item_palette_box)
			self.item_palette_box = None

	def palette_select(self, event: Event) -> None:
		if not self.delegate.spk or not len(self.delegate.spk.images):
			return
		_,_,_,height = parse_scrollregion(self.starsCanvas.cget('scrollregion'))
		y = event.y + self.starsCanvas.yview()[0] * height
		for img in self.delegate.spk.images:
			height = min(img.height,PaletteTab.MAX_SIZE)+PaletteTab.PAD*2
			if y < height:
				self.delegate.selected_image = img
				self.update_palette_selection()
				self.delegate.action_states()
				break
			y -= height

	def clear(self) -> None:
		self.starsCanvas.delete(ALL)
		self.item_palette_box = None

	def export_image(self, *args) -> None:
		if not self.delegate.selected_image:
			return
		filepath = self.delegate.config_.last_path.bmp.select_save(self, title='Export Star')
		if filepath:
			bmp = BMP.BMP()
			bmp.set_pixels(self.delegate.selected_image.pixels, self.delegate.platform_wpe.palette)
			bmp.save_file(filepath)

	def import_image(self, *args) -> None:
		if not self.delegate.spk:
			return
		filepath = self.delegate.config_.last_path.bmp.select_open(self, title='Import Star')
		if not filepath:
			return
		b = BMP.BMP()
		try:
			b.load_file(filepath)
		except PyMSError as e:
			ErrorDialog(self, e)
		else:
			image = SPK.SPKImage()
			image.width = b.width
			image.height = b.height
			image.pixels = b.image
			self.delegate.spk.images.append(image)
			self.delegate.selected_image = image
			self.reload_palette()
			self.delegate.edit()
