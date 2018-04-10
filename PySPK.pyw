from Libs.utils import *
from Libs.setutils import *
from Libs.trace import setup_trace
from Libs import SPK, BMP, PAL, GRP
from Libs.analytics import *
from Tkinter import *
from tkMessageBox import *
from PIL import Image as PILImage

try:
	from PIL import ImageTk
except:
	import ImageTk

from thread import start_new_thread
import optparse, os, webbrowser, sys, time

LONG_VERSION = 'v%s-DEV' % VERSIONS['PySPK']

MOUSE_DOWN = 0
MOUSE_MOVE = 1
MOUSE_UP = 2

MODIFIER_NONE = 0
MODIFIER_SHIFT = 1
MODIFIER_CTRL = 2

TOOL_SELECT = 0
TOOL_MOVE = 1
TOOL_DRAW = 2

class PreviewDialog(PyMSDialog):
	MAP_WIDTH = 32*256
	MAP_HEIGHT = 32*256
	def __init__(self, parent):
		self.items = {}
		self.last_x = None
		self.last_y = None
		PyMSDialog.__init__(self, parent, 'Parallax Preview', center=False)

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
		self.canvas.bind('<MouseWheel>', scroll_map)
		self.bind('<Up>', lambda e: scroll_map(None, False,1))
		self.bind('<Down>', lambda e: scroll_map(None, False,-1))
		self.bind('<Left>', lambda e: scroll_map(None, True,1))
		self.bind('<Right>', lambda e: scroll_map(None, True,-1))

		loadsize(self, self.parent.settings, 'preview', size=False)

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
		savesize(self, self.parent.settings, 'preview')
		PyMSDialog.cancel(self)

class LayersDialog(PyMSDialog):
	def __init__(self, parent):
		self.result = IntegerVar(5, [1,5])
		PyMSDialog.__init__(self, parent, 'How many layers?')

	def widgetize(self):
		Label(self, text='How many layers are contained in the BMP?').pack(padx=5, pady=5)
		Entry(self, textvariable=self.result).pack(padx=5, fill=X)

		buttons = Frame(self)
		ok = Button(buttons, text='Ok', width=10, command=self.ok)
		ok.pack(side=LEFT, padx=3, pady=3)
		Button(buttons, text='Cancel', width=10, command=self.cancel).pack(padx=3, pady=3)
		buttons.pack()

		return ok

	def cancel(self):
		self.result.check = False
		self.result.set(0)
		PyMSDialog.cancel(self)

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
		self.starsCanvas.bind('<MouseWheel>', scroll_palette)
		self.starsCanvas.bind('<Button-1>', self.palette_select)
		self.starsCanvas.pack(side=LEFT, fill=Y, expand=1)
		scrollbar = Scrollbar(scrollframe, command=self.starsCanvas.yview)
		self.starsCanvas.config(yscrollcommand=scrollbar.set)
		scrollbar.pack(side=LEFT, fill=Y, expand=1)
		scrollframe.pack(side=TOP, padx=2, fill=Y, expand=1)
		self.buttons = {}
		f = Frame(self)
		buttons = (
			('select', None, LEFT, 'Select (m)', TOOL_SELECT, 'm'),
			('arrows', None, LEFT, 'Move (v)', TOOL_MOVE, 'v'),
			('pencil', None, LEFT, 'Draw (p)', TOOL_DRAW, 'p'),

			('exportc', self.export_image, RIGHT, 'Export Star', -1, None),
			('importc', self.import_image, RIGHT, 'Import Star', -1, None)
		)
		for col,(icon,callback,side,tip,tool,key) in enumerate(buttons):
			image = PhotoImage(file=os.path.join(BASE_DIR,'Images','%s.gif' % icon))
			if tool != -1:
				button = Radiobutton(f, image=image, indicatoron=0, width=20, height=20, variable=self.toplevel.tool, value=tool, state=DISABLED)#, command=lambda e,t=tool: self.change_tool(t))
			else:
				button = Button(f, image=image, width=20, height=20, command=callback, state=DISABLED)
			button.image = image
			button.tooltip = Tooltip(button, tip)
			button.pack(side=side)
			self.buttons[icon] = button
			if key != None:
				def choose_tool(t):
					if toplevel.spk:
						toplevel.tool.set(t)
				toplevel.bind(key, lambda e,t=tool: choose_tool(t))
		f.pack(side=TOP, fill=X, padx=2, pady=(2,0))

	def action_states(self):
		isopen = [NORMAL,DISABLED][not self.toplevel.spk]
		for btn in ['select','arrows','pencil','importc']:
			self.buttons[btn]['state'] = isopen
		self.buttons['exportc']['state'] = [DISABLED,NORMAL][(self.toplevel.selected_image != None)]

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
		if self.toplevel.selected_image:
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
		if self.toplevel.spk and len(self.toplevel.spk.images):
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
		if self.toplevel.selected_image:
			filepath = self.toplevel.select_file('Export Star To...', False, '.bmp', [('256 Color BMP','*.bmp'),('All Files','*')])
			if filepath:
				bmp = BMP.BMP()
				bmp.load_data(self.toplevel.selected_image.pixels, self.toplevel.platformwpe.palette)
				bmp.save_file(filepath)

	def import_image(self, *args):
		filepath = self.toplevel.select_file('Import Star From...', True, '.bmp', [('256 Color BMP','*.bmp'),('All Files','*')])
		if filepath:
			b = BMP.BMP()
			try:
				b.load_file(filepath)
			except PyMSError, e:
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

class StarsTab(NotebookTab):
	def __init__(self, parent, toplevel):
		self.toplevel = toplevel
		NotebookTab.__init__(self, parent)
		listframe = Frame(self, bd=2, relief=SUNKEN)
		scrollbar = Scrollbar(listframe)
		self.listbox = Listbox(listframe, activestyle=DOTBOX, selectmode=MULTIPLE, font=couriernew, width=1, height=1, bd=0, highlightthickness=0, yscrollcommand=scrollbar.set, exportselection=0)
		bind = [
			('<MouseWheel>', self.scroll),
			('<Home>', lambda a,i=0: self.move(a,i)),
			('<End>', lambda a,i=END: self.move(a,i)),
			('<Up>', lambda a,i=-1: self.move(a,i)),
			('<Left>', lambda a,i=-1: self.move(a,i)),
			('<Down>', lambda a,i=1: self.move(a,i)),
			('<Right>', lambda a,i=-1: self.move(a,i)),
			('<Prior>', lambda a,i=-10: self.move(a,i)),
			('<Next>', lambda a,i=10: self.move(a,i)),
		]
		for b in bind:
			listframe.bind(*b)
		self.listbox.bind('<ButtonRelease-1>', self.lbclick)
		scrollbar.bind('<Button-1>',self.lbclick)
		scrollbar.config(command=self.listbox.yview)
		scrollbar.pack(side=RIGHT, fill=Y)
		self.listbox.pack(side=LEFT, fill=BOTH, expand=1)
		listframe.pack(side=TOP, fill=BOTH, padx=2, expand=1)
		self.buttons = {}
		f = Frame(self)
		buttons = (
			('select', None, LEFT, 'Select (m)', TOOL_SELECT, 'm'),
			('arrows', None, LEFT, 'Move (v)', TOOL_MOVE, 'v'),
			('pencil', None, LEFT, 'Draw (p)', TOOL_DRAW, 'p'),

			('down', lambda: self.move_stars(1), RIGHT, 'Move Stars Up', -1, None),
			('up', lambda: self.move_stars(-1), RIGHT, 'Move Stars Down', -1, None)
		)
		for col,(icon,callback,side,tip,tool,key) in enumerate(buttons):
			image = PhotoImage(file=os.path.join(BASE_DIR,'Images','%s.gif' % icon))
			if tool != -1:
				button = Radiobutton(f, image=image, indicatoron=0, width=20, height=20, variable=self.toplevel.tool, value=tool, state=DISABLED)#, command=lambda e,t=tool: self.change_tool(t))
			else:
				button = Button(f, image=image, width=20, height=20, command=callback, state=DISABLED)
			button.image = image
			button.tooltip = Tooltip(button, tip)
			button.pack(side=side)
			self.buttons[icon] = button
			if key != None:
				def choose_tool(t):
					if toplevel.spk:
						toplevel.tool.set(t)
				toplevel.bind(key, lambda e,t=tool: choose_tool(t))
		f.pack(side=TOP, fill=X, padx=2, pady=(2,0))

	def action_states(self):
		isopen = [NORMAL,DISABLED][not self.toplevel.spk]
		for btn in ['select','arrows','pencil']:
			self.buttons[btn]['state'] = isopen
		hassel = [DISABLED,NORMAL][(len(self.toplevel.selected_stars) > 0)]
		for btn in ('up','down'):
			self.buttons[btn]['state'] = hassel

	def scroll(self, e):
		if e.delta > 0:
			self.listbox.yview('scroll', -2, 'units')
		else:
			self.listbox.yview('scroll', 2, 'units')

	def move(self, e, a):
		if a == END:
			a = self.listbox.size()-2
		elif a not in [0,END]:
			a = max(min(self.listbox.size()-1, int(self.listbox.curselection()[0]) + a),0)
		self.listbox.select_clear(0,END)
		self.listbox.select_set(a)
		self.listbox.see(a)

	def lbclick(self, e=None):
		if self.toplevel.spk:
			sel = tuple(int(s) for s in self.listbox.curselection())
			i = 0
			for l,layer in enumerate(self.toplevel.spk.layers):
				if self.toplevel.visible.get() & (1 << l) and not self.toplevel.locked.get() & (1 << l):
					for star in layer.stars:
						if i in sel and not star in self.toplevel.selected_stars:
							self.toplevel.selected_stars.append(star)
						elif star in self.toplevel.selected_stars and not i in sel:
							self.toplevel.selected_stars.remove(star)
						i += 1
			self.toplevel.update_selection()

	def update_list(self):
		miny,maxy = self.listbox.yview()
		s = self.listbox.size()
		self.listbox.delete(0, END)
		if self.toplevel.spk:
			for l,layer in enumerate(self.toplevel.spk.layers):
				if self.toplevel.visible.get() & (1 << l) and not self.toplevel.locked.get() & (1 << l):
					for star in layer.stars:
						self.listbox.insert(END, '(%s,%s) on Layer %d' % (str(star.x).rjust(3),str(star.y).rjust(3),l+1))
						if star in self.toplevel.selected_stars:
							self.listbox.selection_set(END)
			if self.listbox.size():
				s /= float(self.listbox.size())
			else:
				s = 1
			self.listbox.yview_moveto(miny * s)

	def update_selection(self):
		if self.toplevel.spk:
			self.listbox.select_clear(0,END)
			i = 0
			for l,layer in enumerate(self.toplevel.spk.layers):
				if self.toplevel.visible.get() & (1 << l) and not self.toplevel.locked.get() & (1 << l):
					for star in layer.stars:
						if star in self.toplevel.selected_stars:
							self.listbox.select_set(i)
						i += 1
			self.action_states()

	def move_stars(self, delta):
		for layer in self.toplevel.spk.layers:
			if delta > 0:
				r = xrange(len(layer.stars)-1,-1,-1)
			else:
				r = xrange(0,len(layer.stars))
			update = False
			for i in r:
				if layer.stars[i] in self.toplevel.selected_stars:
					o = i + delta
					if o >= 0 and o < len(layer.stars):
						tmp = layer.stars[i]
						layer.stars[i] = layer.stars[o]
						layer.stars[o] = tmp
						update = True
			if update:
				self.update_list()

	def clear(self):
		self.listbox.delete(0, END)

class LayerRow(Frame):
	def __init__(self, parent, selvar=None, visvar=None, lockvar=None, layer=None, **kwargs):
		Frame.__init__(self, parent, **kwargs)
		self.selvar = selvar
		self.visvar = visvar
		self.lockvar = lockvar
		self.layer = layer
		self.visible = BooleanVar()
		self.visible.set(True)
		self.locked = BooleanVar()
		self.locked.set(False)
		image = PhotoImage(file=os.path.join(BASE_DIR,'Images','eye.gif'))
		visbtn = Checkbutton(self, image=image, indicatoron=0, width=20, height=20, variable=self.visible, onvalue=True, offvalue=False, command=self.toggle_vis, highlightthickness=0)
		visbtn.image = image
		visbtn.pack(side=LEFT)
		image = PhotoImage(file=os.path.join(BASE_DIR,'Images','lock.gif'))
		lockbtn = Checkbutton(self, image=image, indicatoron=0, width=20, height=20, variable=self.locked, onvalue=True, offvalue=False, command=self.toggle_lock, highlightthickness=0)
		lockbtn.image = image
		lockbtn.pack(side=LEFT)
		self.label = Label(self, text='Layer %d' % (layer+1))
		self.label.pack(side=LEFT)
		self.selvar.trace('w', self.update_state)
		self.visvar.trace('w', self.update_state)
		self.lockvar.trace('w', self.update_state)
		self.update_state()
		self.bind('<Button-1>', self.select)
		self.label.bind('<Button-1>', self.select)
		self.hide_widget = None # Gross :(

	def update_state(self, *args, **kwargs):
		self.visible.set((self.visvar.get() & (1 << self.layer)) != 0)
		self.locked.set((self.lockvar.get() & (1 << self.layer)) != 0)
		if self.selvar.get() == self.layer:
			self.config(background='SystemHighlight')
			self.label.config(background='SystemHighlight')
		else:
			self.config(background='#FFFFFF')
			self.label.config(background='#FFFFFF')

	def select(self, event):
		self.selvar.set(self.layer)

	def toggle_vis(self):
		if self.visible.get():
			self.visvar.set(self.visvar.get() | (1 << self.layer))
		else:
			self.visvar.set(self.visvar.get() & ~(1 << self.layer))

	def toggle_lock(self):
		if self.locked.get():
			self.lockvar.set(self.lockvar.get() | (1 << self.layer))
		else:
			self.lockvar.set(self.lockvar.get() & ~(1 << self.layer))

	def hide(self):
		if self.hide_widget == None:
			self.hide_widget = Frame(self)
		self.hide_widget.place(in_=self, relwidth=1, relheight=1)

	def show(self):
		if self.hide_widget:
			self.hide_widget.place_forget()

class PySPK(Tk):
	def __init__(self, guifile=None):
		self.settings = loadsettings('PySPK',
			{
				'platformwpe':'MPQ:tileset\\platform.wpe'
			}
		)

		#Window
		Tk.__init__(self)
		self.title('PySPK %s' % LONG_VERSION)
		try:
			self.icon = os.path.join(BASE_DIR,'Images','PyGOT.ico')
			self.wm_iconbitmap(self.icon)
		except:
			self.icon = '@%s' % os.path.join(BASE_DIR, 'Images','PyGOT.xbm')
			self.wm_iconbitmap(self.icon)
		self.protocol('WM_DELETE_WINDOW', self.exit)
		ga.set_application('PySPK', VERSIONS['PySPK'])
		ga.track(GAScreen('PySPK'))
		setup_trace(self, 'PySPK')

		self.minsize(870, 547)
		self.maxsize(1000, 547)
		if 'window' in self.settings:
			loadsize(self, self.settings, 'window', size=False)

		self.spk = None
		self.file = None
		self.edited = False

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
		self.tool.set(TOOL_SELECT)

		self.load_settings()

		#Toolbar
		buttons = [
			('new', self.new, 'New (Ctrl+N)', NORMAL, 'Ctrl+N'),
			2,
			('open', self.open, 'Open (Ctrl+O)', NORMAL, 'Ctrl+O'),
			('importc', self.iimport, 'Import from BMP (Ctrl+I)', NORMAL, 'Ctrl+I'),
			2,
			('save', self.save, 'Save (Ctrl+S)', DISABLED, 'Ctrl+S'),
			('saveas', self.saveas, 'Save As (Ctrl+Alt+A)', DISABLED, 'Ctrl+Alt+A'),
			('exportc', self.export, 'Export to BMP (Ctrl+E)', DISABLED, 'Ctrl+E'),
			2,
			('close', self.close, 'Close (Ctrl+W)', DISABLED, 'Ctrl+W'),
			10,
			('fwp', self.preview, 'Preview (Ctrl+L)', DISABLED, 'Ctrl+L'),
			10,
			('asc3topyai', self.mpqsettings, 'Manage Settings (Ctrl+M)', NORMAL, 'Ctrl+M'),
			10,
			('register', self.register, 'Set as default *.spk editor (Windows Only)', [DISABLED,NORMAL][win_reg], ''),
			('help', self.help, 'Help (F1)', NORMAL, 'F1'),
			('about', self.about, 'About PySPK', NORMAL, ''),
			10,
			('exit', self.exit, 'Exit (Alt+F4)', NORMAL, 'Alt+F4')
		]
		self.buttons = {}
		toolbar = Frame(self)
		for btn in buttons:
			if isinstance(btn, tuple):
				image = PhotoImage(file=os.path.join(BASE_DIR,'Images','%s.gif' % btn[0]))
				button = Button(toolbar, image=image, width=20, height=20, command=btn[1], state=btn[3])
				button.image = image
				button.tooltip = Tooltip(button, btn[2])
				button.pack(side=LEFT)
				self.buttons[btn[0]] = button
				a = btn[4]
				if a:
					if not a.startswith('F'):
						self.bind('<%s%s>' % (a[:-1].replace('Ctrl','Control').replace('+','-'), a[-1].lower()), btn[1])
					else:
						self.bind('<%s>' % a, btn[1])
			else:
				Frame(toolbar, width=btn).pack(side=LEFT)
		toolbar.pack(side=TOP, padx=1, pady=1, fill=X)

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
		btnsframe = Frame(f)
		buttons = (
			('add', self.add_layer, LEFT, 'Add Layer', 0, None),
			('remove', self.remove_layer, LEFT, 'Remove Layer', 0, None),

			('down', lambda: self.move_layer(1), RIGHT, 'Move Layer Down', 0, None),
			('up', lambda: self.move_layer(-1), RIGHT, 'Move Layer Up', 0, None),
			('lock', None, RIGHT, 'Auto-lock', (0,5), self.autolock),
			('eye', None, RIGHT, 'Auto-visibility', 0, self.autovis)
		)
		for col,(icon,callback,side,tip,padx,var) in enumerate(buttons):
			image = PhotoImage(file=os.path.join(BASE_DIR,'Images','%s.gif' % icon))
			if var:
				button = Checkbutton(btnsframe, image=image, indicatoron=0, width=20, height=20, variable=var, state=DISABLED)
			else:
				button = Button(btnsframe, image=image, width=20, height=20, command=callback, state=DISABLED)
			button.tooltip = Tooltip(button, tip)
			button.image = image
			button.pack(side=side, padx=padx)
			self.buttons[icon] = button
		btnsframe.pack(side=TOP, fill=X, padx=2)
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
		self.skyCanvas = Canvas(rightframe, background='#000000', highlightthickness=0, width=SPK.SPK.LAYER_WIDTH, height=SPK.SPK.LAYER_HEIGHT)
		self.skyCanvas.pack(fill=BOTH)
		self.skyCanvas.focus_set()
		self.skyCanvas.bind('<Motion>', lambda e,m=0: self.mouse_move(e,m))
		self.skyCanvas.bind('<Shift-Motion>', lambda e,m=MODIFIER_SHIFT: self.mouse_move(e,m))
		self.skyCanvas.bind('<Leave>', self.mouse_leave)
		bind = (
			('Up', lambda e,d=(0,-1): self.move_stars(d)),
			('Down', lambda e,d=(0,1): self.move_stars(d)),
			('Left', lambda e,d=(-1,0): self.move_stars(d)),
			('Right', lambda e,d=(1,0): self.move_stars(d)),
			('Delete', self.delete_stars),
			('BackSpace', self.delete_stars)
		)
		for k,c in bind:
			self.bind('<%s>' % k, c)
		rightframe.grid(row=0, column=1, padx=2, pady=2, sticky=NSEW)
		frame.pack(fill=X)
		mouse_events = (
			('<%sButton-1>', MOUSE_DOWN),
			('<%sB1-Motion>', MOUSE_MOVE),
			('<%sButtonRelease-1>', MOUSE_UP),
		)
		mouse_modifiers = (
			('',0),
			('Shift-',MODIFIER_SHIFT),
			('Control-',MODIFIER_CTRL)
		)
		for name,etype in mouse_events:
			for n,mod in mouse_modifiers:
				self.skyCanvas.bind(name % n, lambda e,t=etype,m=mod: self.mouse_event(e,t,m))

		#Statusbar
		self.status = StringVar()
		self.edit_status = StringVar()
		statusbar = Frame(self)
		Label(statusbar, textvariable=self.status, bd=1, relief=SUNKEN, width=35, anchor=W).pack(side=LEFT, padx=1)
		image = PhotoImage(file=os.path.join(BASE_DIR,'Images','save.gif'))
		self.editstatus = Label(statusbar, image=image, bd=0, state=DISABLED)
		self.editstatus.image = image
		self.editstatus.pack(side=LEFT, padx=1, fill=Y)
		Label(statusbar, textvariable=self.edit_status, bd=1, relief=SUNKEN, anchor=W).pack(side=LEFT, expand=1, padx=1, fill=X)
		self.status.set('Load or create a Parallax SPK.')
		statusbar.pack(side=BOTTOM, fill=X)

		self.mpqhandler = MPQHandler(self.settings.get('mpqs',[]))
		if (not 'mpqs' in self.settings or not len(self.settings['mpqs'])) and self.mpqhandler.add_defaults():
			self.settings['mpqs'] = self.mpqhandler.mpqs
		e = self.open_files()

		if guifile:
			self.open(file=guifile)

		start_new_thread(check_update, (self, 'PySPK'))

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
		if layer > -1 and (not len(self.spk.layers[layer].stars) or askyesno(parent=self, title='Delete Layer', message="Are you sure you want to delete the layer?")):
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
			platformwpe = PAL.Palette()
			platformwpe.load_file(self.mpqhandler.get_file(self.settings['platformwpe']))
		except PyMSError, e:
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
		SettingsDialog(self, data, (340,430), err)

	def unsaved(self):
		if self.spk and self.edited:
			file = self.file
			if not file:
				file = 'Unnamed.spk'
			save = askquestion(parent=self, title='Save Changes?', message="Save changes to '%s'?" % file, default=YES, type=YESNOCANCEL)
			if save != 'no':
				if save == 'cancel':
					return True
				if self.file:
					self.save()
				else:
					self.saveas()

	def select_file(self, title, open=True, ext='.spk', filetypes=[('StarCraft Parallax','*.spk'),('All Files','*')]):
		path = self.settings.get('lastpath', BASE_DIR)
		self._pyms__window_blocking = True
		file = [tkFileDialog.asksaveasfilename,tkFileDialog.askopenfilename][open](parent=self, title=title, defaultextension=ext, filetypes=filetypes, initialdir=path)
		self._pyms__window_blocking = False
		if file:
			self.settings['lastpath'] = os.path.dirname(file)
		return file

	def action_states(self):
		isopen = [NORMAL,DISABLED][not self.spk]
		for btn in ['save','saveas','close','fwp','eye','lock']:
			self.buttons[btn]['state'] = isopen
		self.buttons['exportc']['state'] = [DISABLED,NORMAL][(not not self.spk and len(self.spk.layers) > 0)]
		self.buttons['add']['state'] = [DISABLED,NORMAL][(not not self.spk and len(self.spk.layers) < 5)]
		layersel = (self.layer.get() > -1)
		self.buttons['remove']['state'] = [DISABLED,NORMAL][layersel]
		self.buttons['up']['state'] = [DISABLED,NORMAL][self.layer.get() > 0]
		self.buttons['down']['state'] = [DISABLED,NORMAL][(layersel and self.layer.get() < len(self.spk.layers)-1)]
 		self.palette_tab.action_states()
 		self.stars_tab.action_states()

	def edit(self, n=None):
		self.edited = True
		self.editstatus['state'] = NORMAL
		self.action_states()

	def reload_list(self):
		for l,row in enumerate(self.rows):
			if l < len(self.spk.layers):
				row.show()
			else:
				row.hide()

	def layer_updated(self, *args):
		layer = self.layer.get()
		if self.spk and layer > -1:
			if self.autovis.get():
				self.visible.set(1 << layer)
			if self.autolock.get():
				self.locked.set((1+2+4+8+16) & ~(1 << layer))
			self.action_states()

	def visible_updated(self, *args):
		if self.spk:
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
		if self.spk:
			locked = self.locked.get()
			updated_sel = False
			for l,layer in enumerate(self.spk.layers):
				for star in layer.stars:
					if star in self.selected_stars:
						updated_sel = True
						self.selected_stars.remove(star)
			self.stars_tab.update_list()
			if updated_sel:
				self.update_selection()

	def autovis_updated(self, *args):
		if self.spk and self.autovis.get():
			self.layer_updated()

	def autolock_updated(self, *args):
		if self.spk and self.autolock.get():
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
		if self.spk:
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

	def edit_star_settings(self, star=None):
		if star == None:
			star = self.selected_stars[0]
		if star and star.widget:
			StarSettings(self, star)

	def move_stars(self, delta):
		if len(self.selected_stars):
			for star in self.selected_stars:
				star.x = max(0,star.x + delta[0])
				star.y = max(0,star.y + delta[1])
			self.update_canvas()
			self.stars_tab.update_list()
			self.edit()

	def delete_stars(self, event):
		if len(self.selected_stars) and askyesno(parent=self, title='Delete Stars', message="Are you sure you want to delete the stars?"):
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
		if self.spk:
			f = [self.select_event,self.move_event,self.draw_event][self.tool.get()]
			f(event, button_event, modifier)

	def mouse_move(self, event, modifier):
		if self.tool.get() == TOOL_DRAW and self.layer.get() > -1 and self.selected_image:
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
		self.edited = False
		
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

	def new(self, key=None):
		if not self.unsaved():
			self.clear()
			self.spk = SPK.SPK()
			self.reload_list()
			self.update_stars()
			self.file = None
			self.status.set('Editing new Parallax.')
			self.title('PySPK %s (Unnamed.spk)' % LONG_VERSION)
			self.edited = False
			self.editstatus['state'] = DISABLED
			self.action_states()

	def open(self, key=None, file=None):
		if not self.unsaved():
			if file == None:
				file = self.select_file('Open Parallax SPK')
				if not file:
					return
			spk = SPK.SPK()
			try:
				spk.load_file(file)
			except PyMSError, e:
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
			self.title('PySPK %s (%s)' % (LONG_VERSION,file))
			self.file = file
			self.status.set('Load Successful!')
			self.edited = False
			self.editstatus['state'] = DISABLED
			self.action_states()

	def iimport(self, key=None):
		if not self.unsaved():
			filepath = self.select_file('Import BMP', True, '*.bmp', [('256 Color BMP','*.bmp'),('All Files','*')])
			if not filepath:
				return
			t = LayersDialog(self)
			layer_count = t.result.get()
			if not layer_count:
				return
			spk = SPK.SPK()
			try:
				spk.interpret_file(filepath, layer_count)
			except PyMSError, e:
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
			self.title('PySPK %s (%s)' % (LONG_VERSION,filepath))
			self.file = None
			self.status.set('Import Successful!')
			self.edited = False
			self.editstatus['state'] = DISABLED
			self.action_states()

	def save(self, key=None):
		if key and self.buttons['save']['state'] != NORMAL:
			return
		if self.file == None:
			self.saveas()
			return
		try:
			self.spk.save_file(self.file)
			self.status.set('Save Successful!')
			self.edited = False
			self.editstatus['state'] = DISABLED
		except PyMSError, e:
			ErrorDialog(self, e)

	def saveas(self, key=None):
		if key and self.buttons['saveas']['state'] != NORMAL:
			return
		file = self.select_file('Save Parallax SPK As', False)
		if not file:
			return True
		self.file = file
		self.save()

	def export(self, key=None):
		if key and self.buttons['export']['state'] != NORMAL:
			return
		filepath = self.select_file('Export BMP', False, '*.bmp', [('256 Color BMP','*.bmp'),('All Files','*')])
		if not filepath:
			return True
		try:
			self.spk.decompile_file(filepath, self.platformwpe)
			self.status.set('Export Successful!')
		except PyMSError, e:
			ErrorDialog(self, e)

	def close(self, key=None):
		if key and self.buttons['close']['state'] != NORMAL:
			return
		if not self.unsaved():
			self.clear()
			self.title('PySPK %s' % LONG_VERSION)
			self.status.set('Load or create a Parallax SPK.')
			self.editstatus['state'] = DISABLED
			self.action_states()

	def register(self, e=None):
		try:
			register_registry('PySPK','','spk',os.path.join(BASE_DIR, 'PySPK.pyw'),os.path.join(BASE_DIR,'Images','PyGOT.ico'))
		except PyMSError, e:
			ErrorDialog(self, e)

	def help(self, e=None):
		webbrowser.open('file:///%s' % os.path.join(BASE_DIR, 'Docs', 'PySPK.html'))

	def about(self, key=None):
		AboutDialog(self, 'PySPK', LONG_VERSION, [
			('FaRTy1billion','File Specs and SPKEdit')
		])

	def load_settings(self):
		self.autovis.set(self.settings.get('autovis', False))
		self.autolock.set(self.settings.get('autolock', True))

	def save_settings(self):
		self.settings['autovis'] = self.autovis.get()
		self.settings['autolock'] = self.autolock.get()

	def exit(self, e=None):
		if not self.unsaved():
			savesize(self, self.settings, 'window')
			self.save_settings()
			savesettings('PySPK', self.settings)
			self.destroy()

def main():
	import sys
	if not sys.argv or (len(sys.argv) == 1 and os.path.basename(sys.argv[0]).lower() in ['','pyspk.py','pyspk.pyw','pyspk.exe']):
		gui = PySPK()
		startup(gui)
	else:
		p = optparse.OptionParser(usage='usage: PySPK [options] <inp> [out]', version='PySPK %s' % LONG_VERSION)
		# p.add_option('-d', '--decompile', action='store_true', dest='convert', help="Decompile a GOT file [default]", default=True)
		# p.add_option('-c', '--compile', action='store_false', dest='convert', help="Compile a GOT file")
		# p.add_option('-t', '--trig', help="Used to compile a TRG file to a GOT compatable TRG file")
		# p.add_option('-r', '--reference', action='store_true', help="When decompiling, put a reference for settings at the top of the file [default: Off]", default=False)
		p.add_option('--gui', help="Opens a file with the GUI", default='')
		opt, args = p.parse_args()
		if opt.gui:
			gui = PySPK(opt.gui)
			startup(gui)
		# else:
		# 	if not len(args) in [1,2]:
		# 		p.error('Invalid amount of arguments')
		# 	path = os.path.dirname(args[0])
		# 	if not path:
		# 		path = os.path.abspath('')
		# 	got = GOT.GOT()
		# 	if len(args) == 1:
		# 		if opt.convert:
		# 			ext = 'txt'
		# 		else:
		# 			ext = 'got'
		# 		args.append('%s%s%s' % (os.path.join(path,os.extsep.join(os.path.basename(args[0]).split(os.extsep)[:-1])), os.extsep, ext))
		# 	try:
		# 		if opt.convert:
		# 			print "Reading GOT '%s'..." % args[0]
		# 			got.load_file(args[0])
		# 			print " - '%s' read successfully\nDecompiling GOT file '%s'..." % (args[0],args[0])
		# 			got.decompile(args[1], opt.reference)
		# 			print " - '%s' written succesfully" % args[1]
		# 		else:
		# 			print "Interpreting file '%s'..." % args[0]
		# 			got.interpret(args[0])
		# 			print " - '%s' read successfully\nCompiling file '%s' to GOT format..." % (args[0],args[0])
		# 			lo.compile(args[1])
		# 			print " - '%s' written succesfully" % args[1]
		# 			if opt.trig:
		# 				print "Reading TRG '%s'..." % args[0]
		# 				trg = TRG.TRG()
		# 				trg.load_file(opt.trig)
		# 				print " - '%s' read successfully" % args[0]
		# 				path = os.path.dirname(opt.trig)
		# 				if not path:
		# 					path = os.path.abspath('')
		# 				file = '%s%s%s' % (os.path.join(path,os.extsep.join(os.path.basename(args[1]).split(os.extsep)[:-1])), os.extsep, 'trg')
		# 				print "Compiling file '%s' to GOT compatable TRG..." % file
		# 				trg.compile(file, True)
		# 				print " - '%s' written succesfully" % file
		# 	except PyMSError, e:
		# 		print repr(e)

if __name__ == '__main__':
	main()