
from .Tool import Tool
from .LayerRow import LayerRow
from .PaletteTab import PaletteTab
from .StarsTab import StarsTab
from .PreviewDialog import PreviewDialog
from .LayerCountDialog import LayerCountDialog

from ..FileFormats import SPK
from ..FileFormats import Palette
from ..FileFormats import GRP

from ..Utilities.utils import WIN_REG_AVAILABLE, register_registry
from ..Utilities.UIKit import *
from ..Utilities.Settings import Settings
from ..Utilities.analytics import ga, GAScreen
from ..Utilities.trace import setup_trace
from ..Utilities.Toolbar import Toolbar
from ..Utilities import Assets
from ..Utilities.StatusBar import StatusBar
from ..Utilities.Notebook import Notebook
from ..Utilities.MPQHandler import MPQHandler
from ..Utilities.UpdateDialog import UpdateDialog
from ..Utilities.PyMSError import PyMSError
from ..Utilities.ErrorDialog import ErrorDialog
from ..Utilities.SettingsDialog import SettingsDialog
from ..Utilities.AboutDialog import AboutDialog
from ..Utilities.HelpDialog import HelpDialog
from ..Utilities.FileType import FileType
from ..Utilities.fileutils import check_allow_overwrite_internal_file

LONG_VERSION = 'v%s' % Assets.version('PySPK')

MOUSE_DOWN = 0
MOUSE_MOVE = 1
MOUSE_UP = 2

MODIFIER_NONE = 0
MODIFIER_SHIFT = 1
MODIFIER_CTRL = 2

class PySPK(MainWindow):
	def __init__(self, guifile=None):
		self.settings = Settings('PySPK', '1')
		self.settings.settings.files.set_defaults({
			'platformwpe':'MPQ:tileset\\platform.wpe'
		})

		#Window
		MainWindow.__init__(self)
		self.set_icon('PySPK')
		self.protocol('WM_DELETE_WINDOW', self.exit)
		ga.set_application('PySPK', Assets.version('PySPK'))
		ga.track(GAScreen('PySPK'))
		setup_trace('PySPK', self)

		self.minsize(870, 547)
		self.maxsize(1000, 547)

		self.spk = None
		self.file = None
		self.edited = False

		self.update_title()

		self.platformwpe = None

		self.images = {}
		self.star_map = {}
		self.item_map = {}

		self.selected_image = None
		self.item_place_image = None
		self.selecting_start = None
		self.item_selecting_box = None
		self.selected_stars = []
		self.item_selection_boxs = []

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
		self.tool.set(Tool.Select)

		self.load_settings()

		#Toolbar
		self.toolbar = Toolbar(self)
		self.toolbar.add_button(Assets.get_image('new'), self.new, 'New', Ctrl.n)
		self.toolbar.add_gap()
		self.toolbar.add_button(Assets.get_image('open'), self.open, 'Open', Ctrl.o)
		self.toolbar.add_button(Assets.get_image('importc'), self.iimport, 'Import from BMP', Ctrl.i)
		self.toolbar.add_gap()
		self.toolbar.add_button(Assets.get_image('save'), self.save, 'Save', Ctrl.s, enabled=False, tags='file_open')
		self.toolbar.add_button(Assets.get_image('saveas'), self.saveas, 'Save As', Ctrl.Alt.a, enabled=False, tags='file_open')
		self.toolbar.add_button(Assets.get_image('exportc'), self.export, 'Export to BMP', Ctrl.e, enabled=False, tags=('file_open', 'has_layers'))
		self.toolbar.add_gap()
		self.toolbar.add_button(Assets.get_image('close'), self.close, 'Close', Ctrl.w, enabled=False, tags='file_open')
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('fwp'), self.preview, 'Preview', Ctrl.l, enabled=False, tags='file_open')
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('asc3topyai'), self.mpqsettings, 'Manage Settings', Ctrl.m)
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('register'), self.register, 'Set as default *.spk editor (Windows Only)', enabled=WIN_REG_AVAILABLE)
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
		self.rows = []
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
		self.palette_tab = PaletteTab(notebook, self)
		notebook.add_tab(self.palette_tab, 'Palette')
		self.stars_tab = StarsTab(notebook, self)
		notebook.add_tab(self.stars_tab, 'Stars')
		notebook.grid(row=1,column=0, stick=NSEW, padx=(2,0), pady=(4,0))

		leftframe.grid_columnconfigure(0, weight=1)
		leftframe.grid_rowconfigure(1, weight=1)
		leftframe.grid(row=0, column=0, padx=2, pady=2, sticky=NSEW)
		frame.grid_columnconfigure(0, weight=1, minsize=128)

		rightframe = Frame(frame, bd=1, relief=SUNKEN)
		self.skyCanvas = Canvas(rightframe, background='#000000', highlightthickness=0, width=SPK.SPK.LAYER_SIZE[0], height=SPK.SPK.LAYER_SIZE[1])
		self.skyCanvas.pack(fill=BOTH)
		self.skyCanvas.focus_set()
		self.skyCanvas.bind(Mouse.Motion, lambda e,m=0: self.mouse_move(e,m))
		self.skyCanvas.bind(Shift.Motion, lambda e,m=MODIFIER_SHIFT: self.mouse_move(e,m))
		self.skyCanvas.bind(Cursor.Leave, self.mouse_leave)
		self.bind(Key.Up, lambda _: self.move_stars((0, -1)))
		self.bind(Key.Down, lambda _: self.move_stars((0, 1)))
		self.bind(Key.Left, lambda _: self.move_stars((-1, 0)))
		self.bind(Key.Right, lambda _: self.move_stars((1, 0)))
		self.bind(Key.Delete, lambda _: self.delete_stars())
		self.bind(Key.Backspace, lambda _: self.delete_stars())
		rightframe.grid(row=0, column=1, padx=2, pady=2, sticky=NSEW)
		frame.pack(fill=X)
		mouse_events = (
			(Mouse.Click_Left, MOUSE_DOWN),
			(Mouse.Drag_Left, MOUSE_MOVE),
			(ButtonRelease.Click_Left, MOUSE_UP),
		)
		mouse_modifiers = (
			(None,0),
			(Modifier.Shift,MODIFIER_SHIFT),
			(Modifier.Ctrl,MODIFIER_CTRL)
		)
		for base_event,etype in mouse_events:
			for event_mod,mod in mouse_modifiers:
				event = base_event
				if event_mod:
					event = event_mod + event
				self.skyCanvas.bind(event, lambda e,t=etype,m=mod: self.mouse_event(e,t,m))

		#Statusbar
		self.status = StringVar()
		self.status.set('Load or create a Parallax SPK.')
		self.edit_status = StringVar()
		statusbar = StatusBar(self)
		statusbar.add_label(self.status, width=35)
		self.editstatus = statusbar.add_icon(Assets.get_image('save'))
		statusbar.add_label(self.edit_status, weight=1)
		statusbar.pack(side=BOTTOM, fill=X)

		self.mpqhandler = MPQHandler(self.settings.get('mpqs',[]))
		if (not 'mpqs' in self.settings or not len(self.settings['mpqs'])) and self.mpqhandler.add_defaults():
			self.settings['mpqs'] = self.mpqhandler.mpq_paths()
		e = self.open_files()

		if guifile:
			self.open(file=guifile)

		UpdateDialog.check_update(self, 'PySPK')

		if e:
			self.mpqsettings(err=e)

	def add_layer(self):
		layer = SPK.SPKLayer()
		self.spk.layers.append(layer)
		l = len(self.spk.layers)-1
		self.layer.set(l)
		self.rows[l].show()
		self.action_states()
		self.edit()

	def remove_layer(self):
		layer = self.layer.get()
		if layer > -1 and (not len(self.spk.layers[layer].stars) or MessageBox.askyesno(parent=self, title='Delete Layer', message="Are you sure you want to delete the layer?")):
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

	def move_layer(self, delta):
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

	def open_files(self):
		self.mpqhandler.open_mpqs()
		err = None
		try:
			platformwpe = Palette.Palette()
			platformwpe.load_file(self.mpqhandler.get_file(self.settings.settings.files.platformwpe))
		except PyMSError as e:
			err = e
		else:
			self.platformwpe = platformwpe
		self.mpqhandler.close_mpqs()
		return err

	def mpqsettings(self, key=None, err=None):
		data = [
			('Preview Settings',[
				('platform.wpe','The palette which holds the star palette.','platformwpe','WPE')
			])
		]
		SettingsDialog(self, data, (340,430), err, settings=self.settings, mpqhandler=self.mpqhandler)

	def unsaved(self):
		if self.spk and self.edited:
			file = self.file
			if not file:
				file = 'Unnamed.spk'
			save = MessageBox.askquestion(parent=self, title='Save Changes?', message="Save changes to '%s'?" % file, default=MessageBox.YES, type=MessageBox.YESNOCANCEL)
			if save != MessageBox.NO:
				if save == MessageBox.CANCEL:
					return True
				if self.file:
					self.save()
				else:
					self.saveas()

	def is_file_open(self):
		return not not self.spk

	def are_stars_selected(self):
		return len(self.selected_stars) > 0

	def is_layer_selected(self):
		return self.layer.get() > -1

	def is_image_selected(self):
		return not not self.selected_image

	def action_states(self):
		self.toolbar.tag_enabled('file_open', self.is_file_open())
		self.toolbar.tag_enabled('has_layers', self.spk and len(self.spk.layers) > 0)

		self.edit_toolbar.tag_enabled('file_open', self.is_file_open())
		self.edit_toolbar.tag_enabled('can_add_layers', self.spk and len(self.spk.layers) < 5)
		self.edit_toolbar.tag_enabled('layer_selected', self.is_layer_selected())
		self.edit_toolbar.tag_enabled('can_move_up', self.is_layer_selected() and self.layer.get() > 0)
		self.edit_toolbar.tag_enabled('can_move_down', self.is_layer_selected() and self.layer.get() < len(self.spk.layers)-1)

		self.palette_tab.action_states()
		self.stars_tab.action_states()

	def edit(self, n=None):
		self.mark_edited()
		self.action_states()

	def reload_list(self):
		for l,row in enumerate(self.rows):
			if l < len(self.spk.layers):
				row.show()
			else:
				row.hide()

	def layer_updated(self, *args):
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

	def visible_updated(self, *args):
		if not self.is_file_open():
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

	def locked_updated(self, *args):
		if not self.is_file_open():
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

	def autovis_updated(self, *args):
		if not self.is_file_open() or not self.autovis.get():
			return
		self.layer_updated()

	def autolock_updated(self, *args):
		if not self.is_file_open() or not self.autolock.get():
			return
		self.layer_updated()

	def update_zorder(self):
		for l in range(len(self.spk.layers)):
			self.skyCanvas.tag_lower('layer%d' % l)
		self.skyCanvas.lift('selection')

	def get_image(self, spkimage):
		if not spkimage in self.images:
			image = GRP.frame_to_photo(self.platformwpe.palette, spkimage.pixels, None, size=False)
			self.images[spkimage] = image
		return self.images.get(spkimage)

	def update_star(self, star, layer):
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
	def update_canvas(self):
		if not self.is_file_open():
			return
		for l,layer in enumerate(self.spk.layers):
			for star in layer.stars:
				self.update_star(star, l)
		self.update_selection()

	def update_stars(self):
		self.update_canvas()
		self.stars_tab.update_list()

	def update_selection(self):
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
	# 	if star == None:
	# 		star = self.selected_stars[0]
	# 	if star and star.widget:
	# 		StarSettings(self, star)

	def move_stars(self, delta):
		if not len(self.selected_stars):
			return
		for star in self.selected_stars:
			star.x = max(0,star.x + delta[0])
			star.y = max(0,star.y + delta[1])
		self.update_canvas()
		self.stars_tab.update_list()
		self.edit()

	def delete_stars(self):
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

	def select_event(self, event, button_event, modifier):
		if button_event == MOUSE_DOWN:
			self.selecting_start = (event.x,event.y)
		elif button_event == MOUSE_MOVE:
			if self.item_selecting_box == None:
				self.item_selecting_box = self.skyCanvas.create_rectangle(event.x,event.y, event.x,event.y, outline='#FF0000')
			else:
				self.skyCanvas.itemconfig(self.item_selecting_box, state=NORMAL)
			self.skyCanvas.coords(self.item_selecting_box, self.selecting_start[0],self.selecting_start[1], event.x,event.y)
		else:
			x,y = event.x,event.y
			if self.selecting_start != None:
				x,y = self.selecting_start
			self.skyCanvas.itemconfig(self.item_selecting_box, state=HIDDEN)
			items = self.skyCanvas.find_overlapping(x,y, event.x,event.y)
			if modifier == MODIFIER_NONE:
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
	def move_event(self, event, button_event, modifier):
		if button_event == MOUSE_DOWN:
			self.last_pos = (event.x,event.y)
		else:
			dx,dy = event.x-self.last_pos[0],event.y-self.last_pos[1]
			self.move_stars((dx,dy))
			self.last_pos = (event.x,event.y)
	def draw_event(self, event, button_event, modifier):
		if button_event == MOUSE_UP \
				and self.selected_image \
				and len(self.spk.layers) \
				and self.layer.get() > -1 \
				and not self.locked.get() & (1 << self.layer.get()):
			star = SPK.SPKStar()
			star.image = self.selected_image
			star.x = max(0,event.x - star.image.width/2)
			star.y = max(0,event.y - star.image.height/2)
			self.spk.layers[self.layer.get()].stars.append(star)
			self.update_star(star, self.layer.get())
			self.update_zorder()
			self.stars_tab.update_list()
			if not self.visible.get() & (1 << self.layer.get()):
				self.visible.set(self.visible.get() | (1 << self.layer.get()))
			self.edit()
	def mouse_event(self, event, button_event, modifier):
		if not self.is_file_open():
			return
		f = [self.select_event,self.move_event,self.draw_event][self.tool.get()]
		f(event, button_event, modifier)

	def mouse_move(self, event, modifier):
		if self.tool.get() == Tool.Draw and self.layer.get() > -1 and self.selected_image:
			x,y = event.x,event.y
			if modifier == MODIFIER_SHIFT:
				x += self.selected_image.width/2
				y += self.selected_image.height/2
			else:
				x = max(self.selected_image.width/2,x)
				y = max(self.selected_image.height/2,y)
			if not self.item_place_image:
				image = self.get_image(self.selected_image)
				self.item_place_image = self.skyCanvas.create_image(x,y, image=image)
			else:
				self.skyCanvas.coords(self.item_place_image, x,y)
	def mouse_leave(self, event):
		if self.item_place_image:
			self.skyCanvas.delete(self.item_place_image)
			self.item_place_image = None

	def preview(self):
		PreviewDialog(self)

	def clear(self):
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

	def update_title(self):
		file_path = self.file
		if not file_path and self.is_file_open():
			file_path = 'Untitled.spk'
		if not file_path:
			self.title('PySPK %s' % LONG_VERSION)
		else:
			self.title('PySPK %s (%s)' % (LONG_VERSION, file_path))

	def mark_edited(self, edited=True):
		self.edited = edited
		self.editstatus['state'] = NORMAL if edited else DISABLED

	def new(self, key=None):
		if not self.unsaved():
			self.clear()
			self.spk = SPK.SPK()
			self.reload_list()
			self.update_stars()
			self.file = None
			self.status.set('Editing new Parallax.')
			self.update_title()
			self.mark_edited(False)
			self.action_states()

	def open(self, key=None, file=None):
		if not self.unsaved():
			if file == None:
				file = self.settings.lastpath.spk.select_open_file(self, title='Open Parallax SPK', filetypes=[FileType.spk()])
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

	def iimport(self, key=None):
		if not self.unsaved():
			filepath = self.settings.lastpath.bmp.select_open_file(self, key='import', title='Import BMP', filetypes=[FileType.bmp()])
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

	def save(self, key=None):
		self.saveas(file_path=self.file)

	def saveas(self, key=None, file_path=None):
		if not file_path:
			file_path = self.settings.lastpath.spk.select_save_file(self, title='Save Parallax SPK As', filetypes=[FileType.spk()])
			if not file_path:
				return
		elif not check_allow_overwrite_internal_file(file_path):
			return
		try:
			self.spk.save_file(file_path)
		except PyMSError as e:
			ErrorDialog(self, e)
		self.file = file_path
		self.update_title()
		self.status.set('Save Successful!')
		self.mark_edited(False)

	def export(self, key=None):
		filepath = self.settings.lastpath.bmp.select_save_file(self, key='export', title='Export BMP', filetypes=[FileType.bmp()])
		if not filepath:
			return True
		try:
			self.spk.decompile_file(filepath, self.platformwpe)
			self.status.set('Export Successful!')
		except PyMSError as e:
			ErrorDialog(self, e)

	def close(self, key=None):
		if not self.unsaved():
			self.clear()
			self.status.set('Load or create a Parallax SPK.')
			self.editstatus['state'] = DISABLED
			self.action_states()

	def register(self, e=None):
		try:
			register_registry('PySPK', 'spk', '')
		except PyMSError as e:
			ErrorDialog(self, e)

	def help(self, e=None):
		HelpDialog(self, self.settings, 'Help/Programs/PySPK.md')

	def about(self, key=None):
		AboutDialog(self, 'PySPK', LONG_VERSION, [
			('FaRTy1billion','File Specs and SPKEdit')
		])

	def load_settings(self):
		self.settings.windows.load_window_size('main', self)
		self.autovis.set(self.settings.get('autovis', False))
		self.autolock.set(self.settings.get('autolock', True))

	def save_settings(self):
		self.settings.windows.save_window_size('main', self)
		self.settings.autovis = self.autovis.get()
		self.settings.autolock = self.autolock.get()
		self.settings.save()

	def exit(self, e=None):
		if self.unsaved():
			return
		self.save_settings()
		self.destroy()
