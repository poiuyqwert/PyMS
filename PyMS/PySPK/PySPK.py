
from .Config import PySPKConfig
from .Delegates import MainDelegate
from .Tool import Tool
from .LayerRow import LayerRow
from .PaletteTab import PaletteTab
from .StarsTab import StarsTab
from .PreviewDialog import PreviewDialog
from .LayerCountDialog import LayerCountDialog
from .SettingsUI.SettingsDialog import SettingsDialog

from ..FileFormats import SPK
from ..FileFormats import Palette
from ..FileFormats import GRP

from ..Utilities.utils import WIN_REG_AVAILABLE, register_registry
from ..Utilities.UIKit import *
from ..Utilities.analytics import ga, GAScreen
from ..Utilities.trace import setup_trace
from ..Utilities import Assets
from ..Utilities.MPQHandler import MPQHandler
from ..Utilities.UpdateDialog import UpdateDialog
from ..Utilities.PyMSError import PyMSError
from ..Utilities.ErrorDialog import ErrorDialog
from ..Utilities.AboutDialog import AboutDialog
from ..Utilities.HelpDialog import HelpDialog
from ..Utilities.fileutils import check_allow_overwrite_internal_file
from ..Utilities.CheckSaved import CheckSaved
from ..Utilities.SettingsUI.BaseSettingsDialog import ErrorableSettingsDialogDelegate

from enum import Enum

from typing import Callable, cast

LONG_VERSION = 'v%s' % Assets.version('PySPK')

class MouseEvent(Enum):
	down = 0
	move = 1
	up = 2

class ClickModifier(Enum):
	none = 0
	shift = 1
	ctrl = 2

class PySPK(MainWindow, MainDelegate, ErrorableSettingsDialogDelegate):
	def __init__(self, guifile: str | None = None) -> None:
		self.guifile = guifile

		#Window
		MainWindow.__init__(self)
		self.set_icon('PySPK')
		self.protocol('WM_DELETE_WINDOW', self.exit)
		ga.set_application('PySPK', Assets.version('PySPK'))
		ga.track(GAScreen('PySPK'))
		setup_trace('PySPK', self)

		self.config_ = PySPKConfig()
		Theme.load_theme(self.config_.theme.value, self)

		self.minsize(870, 547)
		self.maxsize(1000, 547)

		self.spk: SPK.SPK | None = None
		self.file: str | None = None
		self.edited = False

		self.update_title()

		self.platform_wpe: Palette.Palette

		self.images: dict[SPK.SPKImage, Image] = {}
		self.star_map: dict[Canvas.Item, SPK.SPKStar] = {} # type: ignore[name-defined]
		self.item_map: dict[SPK.SPKStar, Canvas.Item] = {} # type: ignore[name-defined]

		self.selected_image: SPK.SPKImage | None = None
		self.item_place_image: Canvas.Item | None = None # type: ignore[name-defined]
		self.selecting_start: tuple[int, int] | None = None
		self.item_selecting_box: Canvas.Item | None = None # type: ignore[name-defined]
		self.selected_stars: list[SPK.SPKStar] = []
		self.item_selection_boxs: list[Canvas.Item] = [] # type: ignore[name-defined]

		self.layer = IntVar()
		self.layer.trace('w', self.layer_updated)
		self.visible = IntVar()
		self.visible.trace('w', self.visible_updated)
		self.locked = IntVar()
		self.locked.trace('w', self.locked_updated)
		self.autovis = BooleanVar()
		self.autovis.trace('w', self.autovis_updated)
		self.autolock = BooleanVar()
		self.autolock.trace('w', self.autolock_updated)
		self.tool = IntVar()
		self.tool.set(Tool.select.value)

		self.load_settings()

		#Toolbar
		self.toolbar = Toolbar(self)
		self.toolbar.add_button(Assets.get_image('new'), self.new, 'New', Ctrl.n)
		self.toolbar.add_gap()
		self.toolbar.add_button(Assets.get_image('open'), self.open, 'Open', Ctrl.o)
		self.toolbar.add_button(Assets.get_image('importc'), self.iimport, 'Import from BMP', Ctrl.i)
		self.toolbar.add_gap()
		def save():
			self.save()
		self.toolbar.add_button(Assets.get_image('save'), save, 'Save', Ctrl.s, enabled=False, tags='file_open')
		def saveas():
			self.saveas()
		self.toolbar.add_button(Assets.get_image('saveas'), saveas, 'Save As', Ctrl.Alt.a, enabled=False, tags='file_open')
		self.toolbar.add_button(Assets.get_image('exportc'), self.export, 'Export to BMP', Ctrl.e, enabled=False, tags=('file_open', 'has_layers'))
		self.toolbar.add_gap()
		self.toolbar.add_button(Assets.get_image('close'), self.close, 'Close', Ctrl.w, enabled=False, tags='file_open')
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('fwp'), self.preview, 'Preview', Ctrl.l, enabled=False, tags='file_open')
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('asc3topyai'), self.mpqsettings, 'Manage Settings', Ctrl.m)
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('register'), self.register_registry, 'Set as default *.spk editor (Windows Only)', enabled=WIN_REG_AVAILABLE)
		self.toolbar.add_button(Assets.get_image('help'), self.help, 'Help', Key.F1)
		self.toolbar.add_button(Assets.get_image('about'), self.about, 'About PySPK')
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('exit'), self.exit, 'Exit', Shortcut.Exit)
		self.toolbar.pack(side=TOP, padx=1, pady=1, fill=X)

		frame = Frame(self)
		leftframe = Frame(frame)
		layersframe = LabelFrame(leftframe, text='Layers:')
		f = Frame(layersframe)
		listbox = Frame(f, border=2, relief=SUNKEN)
		self.rows: list[LayerRow] = []
		for l in range(5):
			row = LayerRow(listbox, selvar=self.layer, visvar=self.visible, lockvar=self.locked, layer=l)
			row.hide()
			row.pack(side=TOP, fill=X, expand=1)
			self.rows.append(row)
		listbox.pack(side=TOP, padx=5, fill=X, expand=1)

		self.edit_toolbar = Toolbar(f)
		self.edit_toolbar.add_button(Assets.get_image('add'), self.add_layer, 'Add Layer', Key.Insert, enabled=False, tags=('file_open', 'can_add_layers'))
		self.edit_toolbar.add_button(Assets.get_image('remove'), self.remove_layer, 'Remove Layer', Key.Delete, enabled=False, tags='layer_selected')
		self.edit_toolbar.add_spacer(2, flexible=True)
		self.edit_toolbar.add_button(Assets.get_image('up'), lambda: self.move_layer(-1), 'Move Layer Up', enabled=False, tags='can_move_up')
		self.edit_toolbar.add_button(Assets.get_image('down'), lambda: self.move_layer(1), 'Move Layer Down', enabled=False, tags='can_move_down')
		self.edit_toolbar.add_gap()
		self.edit_toolbar.add_checkbutton(Assets.get_image('lock'), self.autolock, 'Auto-lock', enabled=False, tags='file_open')
		self.edit_toolbar.add_checkbutton(Assets.get_image('eye'), self.autovis, 'Auto-visibility', enabled=False, tags='file_open')
		self.edit_toolbar.pack(side=TOP, fill=X, padx=2)

		f.pack(padx=2, pady=2, expand=1, fill=BOTH)
		layersframe.grid(row=0,column=0, sticky=NSEW, padx=(2,0))

		notebook = Notebook(leftframe)
		self.palette_tab = PaletteTab(notebook, self, self)
		notebook.add_tab(self.palette_tab, 'Palette')
		self.stars_tab = StarsTab(notebook, self, self)
		notebook.add_tab(self.stars_tab, 'Stars')
		notebook.grid(row=1,column=0, stick=NSEW, padx=(2,0), pady=(4,0))

		leftframe.grid_columnconfigure(0, weight=1)
		leftframe.grid_rowconfigure(1, weight=1)
		leftframe.grid(row=0, column=0, padx=2, pady=2, sticky=NSEW)
		frame.grid_columnconfigure(0, weight=1, minsize=128)

		rightframe = Frame(frame, bd=1, relief=SUNKEN)
		self.skyCanvas = Canvas(rightframe, background='#000000', highlightthickness=0, width=SPK.SPK.LAYER_SIZE[0], height=SPK.SPK.LAYER_SIZE[1], theme_tag='preview') # type: ignore[call-arg]
		self.skyCanvas.pack(fill=BOTH)
		self.skyCanvas.focus_set()
		self.skyCanvas.bind(Mouse.Motion(), lambda e: self.mouse_move(e,ClickModifier.none))
		self.skyCanvas.bind(Shift.Motion(), lambda e: self.mouse_move(e,ClickModifier.shift))
		self.skyCanvas.bind(Cursor.Leave(), self.mouse_leave)
		self.bind(Key.Up(), lambda _: self.move_stars((0, -1)))
		self.bind(Key.Down(), lambda _: self.move_stars((0, 1)))
		self.bind(Key.Left(), lambda _: self.move_stars((-1, 0)))
		self.bind(Key.Right(), lambda _: self.move_stars((1, 0)))
		self.bind(Key.Delete(), lambda _: self.delete_stars())
		self.bind(Key.Backspace(), lambda _: self.delete_stars())
		rightframe.grid(row=0, column=1, padx=2, pady=2, sticky=NSEW)
		frame.pack(fill=X)
		mouse_events = (
			(Mouse.Click_Left, MouseEvent.down),
			(Mouse.Drag_Left, MouseEvent.move),
			(ButtonRelease.Click_Left, MouseEvent.up),
		)
		mouse_modifiers = (
			(None,ClickModifier.none),
			(Modifier.Shift,ClickModifier.shift),
			(Modifier.Ctrl,ClickModifier.ctrl)
		)
		def mouse_event_callback(mouse_event: MouseEvent, click_modifier: ClickModifier) -> Callable[[Event], None]:
			def _mouse_event(event: Event) -> None:
				self.mouse_event(event, mouse_event, click_modifier)
			return _mouse_event
		for base_event,mouse_event in mouse_events:
			for event_mod,click_modifier in mouse_modifiers:
				event = base_event
				if event_mod:
					event = event_mod + event
				self.skyCanvas.bind(event(), mouse_event_callback(mouse_event, click_modifier))

		#Statusbar
		self.status = StringVar()
		self.status.set('Load or create a Parallax SPK.')
		self.edit_status = StringVar()
		statusbar = StatusBar(self)
		statusbar.add_label(self.status, width=35)
		self.editstatus = statusbar.add_icon(Assets.get_image('save'))
		statusbar.add_label(self.edit_status, weight=1)
		statusbar.pack(side=BOTTOM, fill=X)

		self.mpq_handler = MPQHandler(self.config_.mpqs)

	def initialize(self) -> None:
		e = self.open_files()
		if e:
			self.mpqsettings(err=e)
		if self.guifile:
			self.open(file=self.guifile)
		UpdateDialog.check_update(self, 'PySPK')

	def get_tool(self) -> Tool:
		return Tool(self.tool.get())

	def add_layer(self) -> None:
		if not self.spk:
			return
		layer = SPK.SPKLayer()
		self.spk.layers.append(layer)
		l = len(self.spk.layers)-1
		self.layer.set(l)
		self.rows[l].show()
		self.action_states()
		self.edit()

	def remove_layer(self) -> None:
		if not self.spk:
			return
		layer = self.layer.get()
		if layer < 0 or layer >= len(self.spk.layers):
			return
		if len(self.spk.layers[layer].stars) and not MessageBox.askyesno(parent=self, title='Delete Layer', message="Are you sure you want to delete the layer?"):
			return
		del self.spk.layers[layer]
		self.skyCanvas.delete('layer%d' % layer)
		if layer < len(self.spk.layers):
			for i in range(layer+1,len(self.spk.layers)+1):
				self.skyCanvas.addtag_withtag('layer%d' % (i-1), 'layer%d' % i)
				self.skyCanvas.dtag('layer%d' % i)
		else:
			self.layer.set(layer-1)
		self.rows[len(self.spk.layers)].hide()
		self.action_states()
		self.edit()

	def move_layer(self, delta: int) -> None:
		if not self.spk:
			return
		cur_layer = self.layer.get()
		swap_layer = cur_layer + delta
		self.layer.set(swap_layer)
		temp = self.spk.layers[cur_layer]
		self.spk.layers[cur_layer] = self.spk.layers[swap_layer]
		self.spk.layers[swap_layer] = temp
		self.skyCanvas.addtag_withtag('temp', 'layer%d' % cur_layer)
		self.skyCanvas.dtag('layer%d' % cur_layer)
		self.skyCanvas.addtag_withtag('layer%d' % cur_layer, 'layer%d' % swap_layer)
		self.skyCanvas.dtag('layer%d' % swap_layer)
		self.skyCanvas.addtag_withtag('layer%d' % swap_layer, 'temp')
		self.skyCanvas.dtag('temp')
		self.edit()

	def open_files(self) -> (PyMSError | None):
		self.mpq_handler.open_mpqs()
		err = None
		try:
			platformwpe = Palette.Palette()
			platformwpe.load_file(self.mpq_handler.load_file(self.config_.settings.files.platform_wpe.file_path))
		except PyMSError as e:
			err = e
		else:
			self.platform_wpe = platformwpe
		self.mpq_handler.close_mpqs()
		return err

	def mpqsettings(self, err: PyMSError | None = None) -> None:
		SettingsDialog(self, self.config_, self, err, self.mpq_handler)

	def check_saved(self) -> CheckSaved:
		if not self.spk or not self.edited:
			return CheckSaved.saved
		file = self.file
		if not file:
			file = 'Unnamed.spk'
		save = MessageBox.askquestion(parent=self, title='Save Changes?', message="Save changes to '%s'?" % file, default=MessageBox.YES, type=MessageBox.YESNOCANCEL)
		if save == MessageBox.NO:
			return CheckSaved.saved
		if save == MessageBox.CANCEL:
			return CheckSaved.cancelled
		if self.file:
			return self.save()
		else:
			return self.saveas()

	def is_file_open(self) -> bool:
		return not not self.spk

	def are_stars_selected(self) -> bool:
		return len(self.selected_stars) > 0

	def is_layer_selected(self) -> bool:
		return self.layer.get() > -1

	def is_image_selected(self) -> bool:
		return not not self.selected_image

	def action_states(self) -> None:
		self.toolbar.tag_enabled('file_open', self.is_file_open())
		self.toolbar.tag_enabled('has_layers', not not self.spk and len(self.spk.layers) > 0)

		self.edit_toolbar.tag_enabled('file_open', self.is_file_open())
		self.edit_toolbar.tag_enabled('can_add_layers', not not self.spk and len(self.spk.layers) < 5)
		self.edit_toolbar.tag_enabled('layer_selected', self.is_layer_selected())
		self.edit_toolbar.tag_enabled('can_move_up', self.is_layer_selected() and self.layer.get() > 0)
		self.edit_toolbar.tag_enabled('can_move_down', self.is_layer_selected() and not not self.spk and self.layer.get() < len(self.spk.layers)-1)

		self.palette_tab.action_states()
		self.stars_tab.action_states()

	def edit(self) -> None:
		self.mark_edited()
		self.action_states()

	def reload_list(self) -> None:
		if not self.spk:
			return
		for l,row in enumerate(self.rows):
			if l < len(self.spk.layers):
				row.show()
			else:
				row.hide()

	def layer_updated(self, *args) -> None:
		if not self.is_file_open():
			return
		layer = self.layer.get()
		if layer == -1:
			return
		if self.autovis.get():
			self.visible.set(1 << layer)
		if self.autolock.get():
			self.locked.set((1+2+4+8+16) & ~(1 << layer))
		self.action_states()

	def visible_updated(self, *args) -> None:
		if not self.spk:
			return
		visible = self.visible.get()
		update_sel = False
		for l,layer in enumerate(self.spk.layers):
			self.skyCanvas.itemconfig('layer%d' % l, state=(NORMAL if (visible & (1 << l)) else HIDDEN))
			for star in layer.stars:
				if star in self.selected_stars:
					update_sel = True
					self.selected_stars.remove(star)
		self.stars_tab.update_list()
		if update_sel:
			self.update_selection()

	def locked_updated(self, *args) -> None:
		if not self.spk:
			return
		updated_sel = False
		for layer in self.spk.layers:
			for star in layer.stars:
				if star in self.selected_stars:
					updated_sel = True
					self.selected_stars.remove(star)
		self.stars_tab.update_list()
		if updated_sel:
			self.update_selection()

	def autovis_updated(self, *args) -> None:
		if not self.is_file_open() or not self.autovis.get():
			return
		self.layer_updated()

	def autolock_updated(self, *args) -> None:
		if not self.is_file_open() or not self.autolock.get():
			return
		self.layer_updated()

	def update_zorder(self) -> None:
		if not self.spk:
			return
		for l in range(len(self.spk.layers)):
			self.skyCanvas.tag_lower('layer%d' % l)
		self.skyCanvas.lift('selection')

	def get_image(self, spkimage: SPK.SPKImage) -> (Image | None):
		if not spkimage in self.images:
			image = cast(Image, GRP.frame_to_photo(self.platform_wpe.palette, spkimage.pixels, None, size=False))
			self.images[spkimage] = image
		return self.images.get(spkimage)

	def update_star(self, star: SPK.SPKStar, layer: int) -> None:
		visible = (self.visible.get() & (1 << layer))
		if star in self.item_map:
			item = self.item_map[star]
			self.skyCanvas.coords(item, star.x,star.y)
			self.skyCanvas.itemconfig(item, state=(NORMAL if visible else HIDDEN))
		else:
			image = self.get_image(star.image)
			item = self.skyCanvas.create_image(star.x,star.y, image=image, anchor=NW, tags='layer%d' % layer, state=(NORMAL if visible else HIDDEN))
			self.star_map[item] = star
			self.item_map[star] = item

	def update_canvas(self) -> None:
		if not self.spk:
			return
		for l,layer in enumerate(self.spk.layers):
			for star in layer.stars:
				self.update_star(star, l)
		self.update_selection()

	def update_stars(self) -> None:
		self.update_canvas()
		self.stars_tab.update_list()

	def update_selection(self) -> None:
		while len(self.selected_stars) < len(self.item_selection_boxs):
			self.skyCanvas.delete(self.item_selection_boxs[-1])
			del self.item_selection_boxs[-1]
		for i,star in enumerate(self.selected_stars):
			x1,y1,x2,y2 = star.x-1,star.y-1, star.x+star.image.width,star.y+star.image.height
			if i >= len(self.item_selection_boxs):
				item = self.skyCanvas.create_rectangle(x1,y1, x2,y2, width=1, outline='#F9515B', tags='selection')
				self.item_selection_boxs.append(item)
			else:
				self.skyCanvas.coords(self.item_selection_boxs[i], x1,y1, x2,y2)
		self.edit_status.set('%d stars selected' % len(self.selected_stars))
		self.stars_tab.update_selection()

	# def edit_star_settings(self, star=None):
	# 	if star is None:
	# 		star = self.selected_stars[0]
	# 	if star and star.widget:
	# 		StarSettings(self, star)

	def move_stars(self, delta: tuple[int, int]) -> None:
		if not len(self.selected_stars):
			return
		for star in self.selected_stars:
			star.x = max(0,star.x + delta[0])
			star.y = max(0,star.y + delta[1])
		self.update_canvas()
		self.stars_tab.update_list()
		self.edit()

	def delete_stars(self) -> None:
		if not self.spk:
			return
		if not len(self.selected_stars) or not MessageBox.askyesno(parent=self, title='Delete Stars', message="Are you sure you want to delete the stars?"):
			return
		for star in self.selected_stars:
			self.skyCanvas.delete(self.item_map[star])
			del self.item_map[star]
			for layer in self.spk.layers:
				try:
					layer.stars.remove(star)
				except:
					pass
		self.selected_stars = []
		self.update_selection()
		self.stars_tab.update_list()
		self.edit()

	def select_event(self, event: Event, mouse_event, click_modifier):
		if mouse_event == MouseEvent.down:
			self.selecting_start = (event.x,event.y)
		elif mouse_event == MouseEvent.move and self.selecting_start:
			if self.item_selecting_box is None:
				self.item_selecting_box = self.skyCanvas.create_rectangle(event.x,event.y, event.x,event.y, outline='#FF0000')
			else:
				self.skyCanvas.itemconfig(self.item_selecting_box, state=NORMAL)
			self.skyCanvas.coords(self.item_selecting_box, self.selecting_start[0],self.selecting_start[1], event.x,event.y)
		elif mouse_event == MouseEvent.up:
			x,y = event.x,event.y
			if self.selecting_start is not None:
				x,y = self.selecting_start
			if self.item_selecting_box:
				self.item_selecting_box.config(state=HIDDEN)
			items = self.skyCanvas.find_overlapping(x,y, event.x,event.y)
			if click_modifier == ClickModifier.none:
				self.selected_stars = []
			for item in items:
				if item in self.star_map:
					layer = -1
					for tag in self.skyCanvas.gettags(item):
						if tag.startswith('layer'):
							layer = int(tag[5:])
							break
					if layer > -1 and not self.locked.get() & (1 << layer):
						star = self.star_map[item]
						if not star in self.selected_stars:
							self.selected_stars.append(star)
			self.update_selection()
			self.selecting_start = None

	def move_event(self, event: Event, mouse_event: MouseEvent, click_modifier: ClickModifier) -> None:
		if mouse_event == MouseEvent.down:
			self.last_pos = (event.x,event.y)
		else:
			dx,dy = event.x-self.last_pos[0],event.y-self.last_pos[1]
			self.move_stars((dx,dy))
			self.last_pos = (event.x,event.y)

	def draw_event(self, event: Event, mouse_event: MouseEvent, click_modifier: ClickModifier) -> None:
		if not self.spk:
			return
		if mouse_event != MouseEvent.up \
				or not self.selected_image \
				or not len(self.spk.layers) \
				or self.layer.get() < 0 \
				or self.locked.get() & (1 << self.layer.get()):
			return
		star = SPK.SPKStar()
		star.image = self.selected_image
		star.x = max(0,event.x - star.image.width//2)
		star.y = max(0,event.y - star.image.height//2)
		self.spk.layers[self.layer.get()].stars.append(star)
		self.update_star(star, self.layer.get())
		self.update_zorder()
		self.stars_tab.update_list()
		if not self.visible.get() & (1 << self.layer.get()):
			self.visible.set(self.visible.get() | (1 << self.layer.get()))
		self.edit()

	def mouse_event(self, event: Event, mouse_event: MouseEvent, click_modifier: ClickModifier) -> None:
		if not self.is_file_open():
			return
		match self.get_tool():
			case Tool.select:
				f = self.select_event
			case Tool.move:
				f = self.move_event
			case Tool.draw:
				f = self.draw_event
		f(event, mouse_event, click_modifier)

	def mouse_move(self, event: Event, click_modifier: ClickModifier) -> None:
		if self.get_tool() == Tool.draw and self.layer.get() > -1 and self.selected_image:
			x,y = event.x,event.y
			if click_modifier == ClickModifier.shift:
				x += self.selected_image.width//2
				y += self.selected_image.height//2
			else:
				x = max(self.selected_image.width//2,x)
				y = max(self.selected_image.height//2,y)
			if not self.item_place_image:
				image = self.get_image(self.selected_image)
				self.item_place_image = self.skyCanvas.create_image(x,y, image=image)
			else:
				self.skyCanvas.coords(self.item_place_image, x,y)

	def mouse_leave(self, event: Event) -> None:
		if self.item_place_image:
			self.skyCanvas.delete(self.item_place_image)
			self.item_place_image = None

	def preview(self) -> None:
		PreviewDialog(self, self)

	def clear(self) -> None:
		self.spk = None
		self.file = None
		self.mark_edited(False)
		
		self.update_title()
		
		self.selected_image = None
		self.selected_stars = []

		self.layer.set(-1)
		self.visible.set(1+2+4+8+16)
		if self.autolock.get():
			self.locked.set(2+4+8+16)
		else:
			self.locked.set(0)

		for r in self.rows:
			r.hide()
		self.skyCanvas.delete(ALL)

		self.palette_tab.clear()
		self.stars_tab.clear()

	def update_title(self) -> None:
		file_path = self.file
		if not file_path and self.is_file_open():
			file_path = 'Untitled.spk'
		if not file_path:
			self.title('PySPK %s' % LONG_VERSION)
		else:
			self.title('PySPK %s (%s)' % (LONG_VERSION, file_path))

	def mark_edited(self, edited: bool = True) -> None:
		self.edited = edited
		self.editstatus['state'] = NORMAL if edited else DISABLED

	def new(self) -> None:
		if self.check_saved() == CheckSaved.cancelled:
			return
		self.clear()
		self.spk = SPK.SPK()
		self.reload_list()
		self.update_stars()
		self.file = None
		self.status.set('Editing new Parallax.')
		self.update_title()
		self.mark_edited(False)
		self.action_states()

	def open(self, file: str | None = None) -> None:
		if self.check_saved() == CheckSaved.cancelled:
			return
		if file is None:
			file = self.config_.last_path.spk.select_open(self)
			if not file:
				return
		spk = SPK.SPK()
		try:
			spk.load_file(file)
		except PyMSError as e:
			ErrorDialog(self, e)
			return
		self.clear()
		self.spk = spk
		if len(self.spk.layers):
			self.layer.set(0)
		self.reload_list()
		if len(self.spk.images):
			self.selected_image = self.spk.images[0]
		self.palette_tab.reload_palette()
		self.update_stars()
		self.file = file
		self.update_title()
		self.status.set('Load Successful!')
		self.mark_edited(False)
		self.action_states()

	def iimport(self) -> None:
		if self.check_saved() == CheckSaved.cancelled:
			return
		filepath = self.config_.last_path.bmp.select_open(self)
		if not filepath:
			return
		t = LayerCountDialog(self)
		layer_count = t.result.get()
		if not layer_count:
			return
		spk = SPK.SPK()
		try:
			spk.interpret_file(filepath, layer_count)
		except PyMSError as e:
			ErrorDialog(self, e)
			return
		self.clear()
		self.spk = spk
		if len(self.spk.layers):
			self.layer.set(0)
		self.reload_list()
		if len(self.spk.images):
			self.selected_image = self.spk.images[0]
		self.palette_tab.reload_palette()
		self.update_stars()
		self.file = None
		self.update_title()
		self.status.set('Import Successful!')
		self.mark_edited(False)
		self.action_states()

	def save(self) -> CheckSaved:
		return self.saveas(file_path=self.file)

	def saveas(self, file_path: str | None = None) -> CheckSaved:
		if not self.spk:
			return CheckSaved.saved
		if not file_path:
			file_path = self.config_.last_path.spk.select_save(self)
			if not file_path:
				return CheckSaved.cancelled
		elif not check_allow_overwrite_internal_file(file_path):
			return CheckSaved.cancelled
		try:
			self.spk.save_file(file_path)
		except PyMSError as e:
			ErrorDialog(self, e)
			return CheckSaved.cancelled
		self.file = file_path
		self.update_title()
		self.status.set('Save Successful!')
		self.mark_edited(False)
		return CheckSaved.saved

	def export(self) -> None:
		if not self.spk:
			return
		filepath = self.config_.last_path.bmp.select_save(self)
		if not filepath:
			return
		try:
			self.spk.decompile_file(filepath, self.platform_wpe)
			self.status.set('Export Successful!')
		except PyMSError as e:
			ErrorDialog(self, e)

	def close(self) -> None:
		if self.check_saved() == CheckSaved.cancelled:
			return
		self.clear()
		self.status.set('Load or create a Parallax SPK.')
		self.editstatus['state'] = DISABLED
		self.action_states()

	def register_registry(self) -> None:
		try:
			register_registry('PySPK', 'spk', '')
		except PyMSError as e:
			ErrorDialog(self, e)

	def help(self) -> None:
		HelpDialog(self, self.config_.windows.help, 'Help/Programs/PySPK.md')

	def about(self) -> None:
		AboutDialog(self, 'PySPK', LONG_VERSION, [
			('FaRTy1billion','File Specs and SPKEdit')
		])

	def load_settings(self) -> None:
		self.config_.windows.main.load(self)
		self.autovis.set(self.config_.auto.visibility.value)
		self.autolock.set(self.config_.auto.lock.value)

	def save_settings(self) -> None:
		self.config_.windows.main.save(self)
		self.config_.auto.visibility.value = self.autovis.get()
		self.config_.auto.lock.value = self.autolock.get()
		self.config_.save()

	def exit(self) -> None:
		if self.check_saved() == CheckSaved.cancelled:
			return
		self.save_settings()
		self.destroy()
