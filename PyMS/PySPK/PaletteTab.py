
from .Tool import Tool

from ..FileFormats import SPK
from ..FileFormats import BMP

from ..Utilities.UIKit import *
from ..Utilities.Notebook import NotebookTab
from ..Utilities.Toolbar import Toolbar
from ..Utilities import Assets
from ..Utilities.PyMSError import PyMSError
from ..Utilities.ErrorDialog import ErrorDialog
from ..Utilities.FileType import FileType

class PaletteTab(NotebookTab):
	MAX_SIZE = 150
	PAD = 10

	def __init__(self, parent, toplevel):
		self.toplevel = toplevel
		self.item_palette_box = None
		NotebookTab.__init__(self, parent)

		scrollframe = Frame(self, bd=2, relief=SUNKEN)
		self.starsCanvas = Canvas(scrollframe, background='#000000', highlightthickness=0, width=PaletteTab.MAX_SIZE+PaletteTab.PAD*2)
		def scroll_palette(event):
			if self.toplevel.spk:
				if event.delta > 0:
					self.starsCanvas.yview('scroll', -1, 'units')
				else:
					self.starsCanvas.yview('scroll', 1, 'units')
		self.starsCanvas.bind(Mouse.Scroll, scroll_palette)
		self.starsCanvas.bind(Mouse.Click_Left, self.palette_select)
		self.starsCanvas.pack(side=LEFT, fill=Y, expand=1)
		scrollbar = Scrollbar(scrollframe, command=self.starsCanvas.yview)
		self.starsCanvas.config(yscrollcommand=scrollbar.set)
		scrollbar.pack(side=LEFT, fill=Y, expand=1)
		scrollframe.pack(side=TOP, padx=2, fill=Y, expand=1)

		self.toolbar = Toolbar(self, bind_target=self.toplevel)
		self.toolbar.add_radiobutton(Assets.get_image('select'), self.toplevel.tool, Tool.Select, 'Select', Key.m, enabled=False, tags='file_open')
		self.toolbar.add_radiobutton(Assets.get_image('arrows'), self.toplevel.tool, Tool.Move, 'Move', Key.v, enabled=False, tags='file_open')
		self.toolbar.add_radiobutton(Assets.get_image('pencil'), self.toplevel.tool, Tool.Draw, 'Draw', Key.p, enabled=False, tags='file_open')
		self.toolbar.add_spacer(2, flexible=True)
		self.toolbar.add_button(Assets.get_image('exportc'), self.export_image, 'Export Star', enabled=False, tags='image_selected')
		self.toolbar.add_button(Assets.get_image('importc'), self.import_image, 'Import Star', enabled=False, tags='file_open')
		self.toolbar.pack(side=TOP, fill=X, padx=2, pady=(2,0))

	def action_states(self):
		self.toolbar.tag_enabled('file_open', self.toplevel.is_file_open())
		self.toolbar.tag_enabled('image_selected', self.toplevel.is_image_selected())

	def reload_palette(self, scroll=True):
		y = 0
		for img in self.toplevel.spk.images:
			height = min(img.height,PaletteTab.MAX_SIZE)+PaletteTab.PAD*2
			image = self.toplevel.get_image(img)

			self.starsCanvas.create_image(PaletteTab.MAX_SIZE/2+PaletteTab.PAD,y + height/2, image=image)
			y += height
		self.starsCanvas.config(scrollregion=(0,0,PaletteTab.MAX_SIZE,y))
		self.update_palette_selection(scroll)

	def update_palette_selection(self, scroll=False):
		if self.toplevel.is_image_selected():
			index = self.toplevel.spk.images.index(self.toplevel.selected_image)
			y = 0
			height = 0
			for i,img in enumerate(self.toplevel.spk.images):
				height = min(img.height,PaletteTab.MAX_SIZE)+PaletteTab.PAD*2
				if i == index:
					break
				y += height
			x2 = PaletteTab.MAX_SIZE+PaletteTab.PAD*2-1
			y2 = y+height-1
			if self.item_palette_box:
				self.starsCanvas.coords(self.item_palette_box, 0,y, x2,y2)
			else:
				self.item_palette_box = self.starsCanvas.create_rectangle(0,y, x2,y2, width=1, outline='#FFFFFF')
			if scroll:
				miny,maxy = self.starsCanvas.yview()
				area = maxy-miny
				maxy = 1-area
				center = y + (y2-y)/2
				_,_,_,height = parse_scrollregion(self.starsCanvas.cget('scrollregion'))
				vis = height * area
				top = center - vis/2
				y = top/height
				self.starsCanvas.yview_moveto(y)
		elif self.item_palette_box:
			self.starsCanvas.delete(self.item_palette_box)
			self.item_palette_box = None

	def palette_select(self, event):
		if not self.toplevel.is_file_open() or not len(self.toplevel.spk.images):
			return
		_,_,_,height = parse_scrollregion(self.starsCanvas.cget('scrollregion'))
		y = event.y + self.starsCanvas.yview()[0] * height
		for img in self.toplevel.spk.images:
			height = min(img.height,PaletteTab.MAX_SIZE)+PaletteTab.PAD*2
			if y < height:
				self.toplevel.selected_image = img
				self.update_palette_selection()
				self.toplevel.action_states()
				break
			y -= height

	def clear(self):
		self.starsCanvas.delete(ALL)
		self.item_palette_box = None

	def export_image(self, *args):
		if not self.toplevel.is_image_selected():
			return
		filepath = self.toplevel.settings.lastpath.bmp.select_save_file(self, key='export', title='Export Star To...', filetypes=[FileType.bmp()])
		if filepath:
			bmp = BMP.BMP()
			bmp.set_pixels(self.toplevel.selected_image.pixels, self.toplevel.platformwpe.palette)
			bmp.save_file(filepath)

	def import_image(self, *args):
		filepath = self.toplevel.settings.lastpath.bmp.select_open_file(self, key='import', title='Import Star From...', filetypes=[FileType.bmp()])
		if not filepath:
			return
		b = BMP.BMP()
		try:
			b.load_file(filepath)
		except PyMSError as e:
			ErrorDialog(self.toplevel, e)
		else:
			image = SPK.SPKImage()
			image.width = b.width
			image.height = b.height
			image.pixels = b.image
			self.toplevel.spk.images.append(image)
			self.toplevel.selected_image = image
			self.reload_palette()
			self.toplevel.edit()
