from Libs.utils import *
from Libs.setutils import *
from Libs.trace import setup_trace
from Libs.SpecialLists import TreeList
from Libs import DialogBIN, FNT, PCX

from Tkinter import *

from thread import start_new_thread
import optparse, os, webbrowser, sys

VERSION = (0,1)
LONG_VERSION = 'v%s.%s-DEV' % VERSION

MOUSE_DOWN = 0
MOUSE_MOVE = 1
MOUSE_UP = 2

EDIT_MOVE = 0
EDIT_RESIZE_LEFT = 1
EDIT_RESIZE_TOP = 2
EDIT_RESIZE_RIGHT = 3
EDIT_RESIZE_BOTTOM = 4

MODIFIER_SHIFT = 1
MODIFIER_CTRL = 2

def edit_event(x1,y1,x2,y2, mouseX,mouseY, resizable=True):
	event = []
	d = 5 * resizable
	if x1-d <= mouseX <= x2+d and y1-d <= mouseY <= y2+d:
		event.append(EDIT_MOVE)
		if resizable:
			dist_left = abs(x1 - mouseX)
			dist_right = abs(x2 - mouseX)
			if dist_left < dist_right and dist_left <= 5:
				event[0] = EDIT_RESIZE_LEFT
			elif dist_right < dist_left and dist_right <= 5:
				event[0] = EDIT_RESIZE_RIGHT
			dist_top = abs(y1 - mouseY)
			dist_bot = abs(y2 - mouseY)
			if dist_top < dist_bot and dist_top <= 5:
				event.append(EDIT_RESIZE_TOP)
			elif dist_bot < dist_top and dist_bot <= 5:
				event.append(EDIT_RESIZE_BOTTOM)
	return event

class StringPreview:
	# GLYPH_CACHE = {}

	def __init__(self, text, font, palette, align=0):
		self.text = text
		self.font = font
		self.palette = palette
		self.align = align
		self.glyphs = None

	def get_glyphs(self):
		if self.glyphs == None:
			self.glyphs = []
			color = 2
			for c in self.text:
				a = ord(c)
				if a >= self.font.start and a < self.font.start + len(self.font.letters):
					a -= self.font.start
					self.glyphs.append(FNT.letter_to_photo(self.palette, self.font.letters[a], color))
				elif a in FNT.COLOR_CODES and not color in FNT.COLOR_OVERPOWER:
					color = a
		return self.glyphs

	def get_positions(self, x1,y1,x2,y2):
		positions = []
		position = [x1,y1]
		size = [x2-x1,y2-y1]
		line = []
		line_width = [0]
		word = []
		word_width = [0]
		def add_line():
			if line:
				o = 0
				if self.align & DialogBIN.BINWidget.FLAG_TEXT_ALIGN_CENTER:
					o = int((size[0] - line_width[0]) / 2.0)
				elif self.align & DialogBIN.BINWidget.FLAG_TEXT_ALIGN_RIGHT:
					o = size[0] - line_width[0]
				for w in line:
					positions.append((position[0] + o, position[1]))
					o += w
				del line[:]
				line_width[0] = 0
			position[1] += self.font.height
		def add_word():
			line.extend(word)
			line_width[0] += word_width[0]
			word_width[0] = 0
			del word[:]
		for c in self.text:
			a = ord(c)
			if a >= self.font.start and a < self.font.start + len(self.font.letters):
				a -= self.font.start
				w = self.font.sizes[a][0]
				if c == ' ' and w == 0:
					w = 0
					count = 0
					for l in xrange(len(self.font.letters)):
						if l != a:
							w += self.font.sizes[l][0]
							count += 1
					w = int(round(w / float(count)))
					self.font.sizes[a][0] = w
				word.append(w)
				word_width[0] += w
			if c == ' ':
				if line and line_width[0] + word_width[0] >= size[0]:
					add_line()
				add_word()
				if line_width[0] >= size[0]:
					add_line()
			elif c in '\r\n':
				add_line()

		if word:
			add_word()
		if line:
			add_line()
		return positions

class WidgetNode:
	def __init__(self, widget):
		self.widget = widget
		self.parent = None
		self.name = None
		self.index = None
		if widget and widget.type != DialogBIN.BINWidget.TYPE_DIALOG:
			self.children = None
		else:
			self.children = []

		self.string = None
		self.photo = None

		self.item_bounds = None
		self.item_text_bounds = None
		self.item_responsive_bounds = None
		self.item_string_images = None
		self.item_image = None

	def get_name(self):
		name = 'Group'
		if self.widget:
			name = DialogBIN.BINWidget.TYPE_NAMES[self.widget.type]
		if self.name:
			name = '%s (%s)' % self.name
		return name

	def add_child(self, node):
		self.children.append(node)
		if node.parent:
			node.parent.children.remove(node)
		node.parent = self

	def bounding_box(self):
		if self.widget:
			return self.widget.bounding_box()
		bounding_box = [sys.maxint,sys.maxint,0,0]
		for node in self.children:
			x1,y1,x2,y2 = node.bounding_box()
			if x1 < bounding_box[0]:
				bounding_box[0] = x1
			if y1 < bounding_box[1]:
				bounding_box[1] = y1
			if x2 > bounding_box[2]:
				bounding_box[2] = x2
			if y2 > bounding_box[3]:
				bounding_box[3] = y2
		return bounding_box

	def update_image(self, toplevel):
		reorder = False
		SHOW_IMAGES = toplevel.show_images.get()
		if SHOW_IMAGES and self.widget and self.widget.type == DialogBIN.BINWidget.TYPE_IMAGE and self.widget.flags & DialogBIN.BINWidget.FLAG_VISIBLE:
			photo_change = False
			if self.photo == None:
				photo_change = True
				pcx = PCX.PCX()
				try:
					pcx.load_file(toplevel.mpqhandler.get_file('MPQ:' + self.widget.string))
				except:
					raise
					pass
				else:
					trans = ((self.widget.flags & DialogBIN.BINWidget.FLAG_TRANSPARENCY) == DialogBIN.BINWidget.FLAG_TRANSPARENCY)
					self.photo = GRP.frame_to_photo(pcx.palette, pcx, -1, size=False, trans=trans)
			if self.photo:
				x1,y1,x2,y2 = self.bounding_box()
				if self.item_image:
					if photo_change:
						toplevel.widgetCanvas.configure(self.item_image, image=self.photo)
					toplevel.widgetCanvas.coords(self.item_image, x1,y1)
				else:
					self.item_image = toplevel.widgetCanvas.create_image(x1,y1, image=self.photo, anchor=NW)
					reorder = True
		elif self.item_image:
			toplevel.widgetCanvas.delete(self.item_image)
			self.item_image = None
		return reorder

	def update_text(self, toplevel):
		reorder = False
		SHOW_TEXT = toplevel.show_text.get()
		if SHOW_TEXT and self.widget and self.widget.display_text() and self.widget.flags & DialogBIN.BINWidget.FLAG_VISIBLE:
			x1,y1,x2,y2 = self.widget.text_box()
			if self.item_string_images:
				positions = self.string.get_positions(x1,y1, x2,y2)
				for item,position in zip(self.item_string_images,positions):
					toplevel.widgetCanvas.coords(item, *position)
			else:
				if self.string == None:
					font = toplevel.font10
					if self.widget.flags & DialogBIN.BINWidget.FLAG_FONT_SIZE_14:
						font = toplevel.font14
					elif self.widget.flags & DialogBIN.BINWidget.FLAG_FONT_SIZE_16:
						font = toplevel.font16
					elif self.widget.flags & DialogBIN.BINWidget.FLAG_FONT_SIZE_16x:
						font = toplevel.font16x
					self.string = StringPreview(self.widget.display_text(), font, toplevel.tfontgam, align=self.widget.flags & DialogBIN.BINWidget.FLAGS_TEXT_ALIGN)
				self.item_string_images = []
				glyphs = self.string.get_glyphs()
				positions = self.string.get_positions(x1,y1, x2,y2)
				for glyph,position in zip(glyphs,positions):
					self.item_string_images.append(toplevel.widgetCanvas.create_image(position[0],position[1], image=glyph, anchor=NW))
				reorder = True
		elif self.item_string_images:
			for item in self.item_string_images:
				toplevel.widgetCanvas.delete(item)
			self.item_string_images = None
		return reorder

	def update_bounds(self, toplevel):
		reorder = False
		SHOW_BOUNDING_BOX = toplevel.show_bounds_widget.get()
		SHOW_GROUP_BOUNDS = toplevel.show_bounds_group.get()
		if SHOW_BOUNDING_BOX and (self.widget or SHOW_GROUP_BOUNDS):
			x1,y1,x2,y2 = self.bounding_box()
			if self.item_bounds:
				toplevel.widgetCanvas.coords(self.item_bounds, x1,y1, x2,y2)
			else:
				self.item_bounds = toplevel.widgetCanvas.create_rectangle(x1,y1, x2,y2, width=1, outline='#0080ff' if self.widget else '#505050')
				reorder = True
		elif self.item_bounds:
			toplevel.widgetCanvas.delete(self.item_bounds)
			self.item_bounds = None
		return reorder

	def update_text_bounds(self, toplevel):
		reorder = False
		SHOW_TEXT_BOUNDS = toplevel.show_bounds_text.get()
		if SHOW_TEXT_BOUNDS and self.widget and self.widget.display_text():
			x1,y1,x2,y2 = self.widget.text_box()
			if self.item_text_bounds:
				toplevel.widgetCanvas.coords(self.item_text_bounds, x1,y1, x2,y2)
			else:
				self.item_text_bounds = toplevel.widgetCanvas.create_rectangle(x1,y1, x2,y2, width=1, outline='#F0F0F0')
				reorder = True
		elif self.item_text_bounds:
			toplevel.widgetCanvas.delete(self.item_text_bounds)
			self.item_text_bounds = None
		return reorder

	def update_responsive_bounds(self, toplevel):
		reorder = False
		SHOW_RESPONSIVE_BOUNDS = toplevel.show_bounds_responsive.get()
		if self.widget and self.widget.type == DialogBIN.BINWidget.TYPE_HIGHLIGHT_BTN and SHOW_RESPONSIVE_BOUNDS: # Show Responsive Box
			x1,y1,x2,y2 = self.widget.responsive_box()
			if self.item_responsive_bounds:
				toplevel.widgetCanvas.coords(self.item_responsive_bounds, x1,y1, x2,y2)
			else:
				self.item_responsive_bounds = toplevel.widgetCanvas.create_rectangle(x1,y1, x2,y2, width=1, outline='#00ff80')
				reorder = True
		elif self.item_responsive_bounds:
			toplevel.widgetCanvas.delete(self.item_responsive_bounds)
			self.item_responsive_bounds = None
		return reorder

	def update_display(self, toplevel):
		reorder = False
		reorder = self.update_image(toplevel) or reorder
		reorder = self.update_text(toplevel) or reorder
		reorder = self.update_bounds(toplevel) or reorder
		reorder = self.update_text_bounds(toplevel) or reorder
		reorder = self.update_responsive_bounds(toplevel) or reorder
		return reorder

	def lift(self, toplevel):
		if self.item_image:
			toplevel.widgetCanvas.lift(self.item_image)
		if self.item_string_images:
			for item in self.item_string_images:
				toplevel.widgetCanvas.lift(item)
		if self.item_bounds:
			toplevel.widgetCanvas.lift(self.item_bounds)
		if self.item_text_bounds:
			toplevel.widgetCanvas.lift(self.item_text_bounds)
		if self.item_responsive_bounds:
			toplevel.widgetCanvas.lift(self.item_responsive_bounds)

class PyBIN(Tk):
	def __init__(self, guifile=None):
		self.settings = loadsettings('PyBIN',
			{
				'tfontgam':'MPQ:game\\tfontgam.pcx',
				'font10':'MPQ:font\\font10.fnt',
				'font14':'MPQ:font\\font14.fnt',
				'font16':'MPQ:font\\font16.fnt',
				'font16x':'MPQ:font\\font16x.fnt',
			}
		)

		#Window
		Tk.__init__(self)
		self.title('PyBIN %s' % LONG_VERSION)
		try:
			self.icon = os.path.join(BASE_DIR,'Images','PyGOT.ico')
			self.wm_iconbitmap(self.icon)
		except:
			self.icon = '@%s' % os.path.join(BASE_DIR, 'Images','PyGOT.xbm')
			self.wm_iconbitmap(self.icon)
		self.protocol('WM_DELETE_WINDOW', self.exit)
		setup_trace(self, 'PyBIN')
		self.minsize(850, 539)
		self.maxsize(1080, 539)
		# self.resizable(True, False)
		if 'window' in self.settings:
			loadsize(self, self.settings, 'window', True)

		self.bin = None
		self.file = None
		self.edited = False
		self.dialog = None
		self.widget_map = None

		self.selected_node = None
		self.old_cursor = None
		self.edit_node = None
		self.current_event = []
		self.mouse_offset = [0,0]
		self.item_selection_box = None

		#Toolbar
		buttons = [
			('new', self.new, 'New (Ctrl+N)', NORMAL, 'Ctrl+N'),
			2,
			('open', self.open, 'Open (Ctrl+O)', NORMAL, 'Ctrl+O'),
			('import', self.iimport, 'Import from TXT (Ctrl+I)', NORMAL, 'Ctrl+I'),
			2,
			('save', self.save, 'Save (Ctrl+S)', DISABLED, 'Ctrl+S'),
			('saveas', self.saveas, 'Save As (Ctrl+Alt+A)', DISABLED, 'Ctrl+Alt+A'),
			('export', self.export, 'Export to TXT (Ctrl+E)', DISABLED, 'Ctrl+E'),
			2,
			('close', self.close, 'Close (Ctrl+W)', DISABLED, 'Ctrl+W'),
			10,
			('asc3topyai', self.mpqsettings, 'Manage Settings (Ctrl+M)', NORMAL, 'Ctrl+M'),
			10,
			('register', self.register, 'Set as default *.bin editor (Windows Only)', [DISABLED,NORMAL][win_reg], ''),
			('help', self.help, 'Help (F1)', NORMAL, 'F1'),
			('about', self.about, 'About PyBIN', NORMAL, ''),
			10,
			('exit', self.exit, 'Exit (Alt+F4)', NORMAL, 'Alt+F4'),
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

		self.show_images = BooleanVar()
		self.show_images.set(self.settings.get('show_images',True))
		self.show_text = BooleanVar()
		self.show_text.set(self.settings.get('show_text',True))
		self.show_smks = BooleanVar()
		self.show_smks.set(self.settings.get('show_smks',True))
		self.show_animated = BooleanVar()
		self.show_animated.set(self.settings.get('show_animated',False))
		self.show_bounds_widget = BooleanVar()
		self.show_bounds_widget.set(self.settings.get('show_bounds_widget',True))
		self.show_bounds_group = BooleanVar()
		self.show_bounds_group.set(self.settings.get('show_bounds_group',True))
		self.show_bounds_text = BooleanVar()
		self.show_bounds_text.set(self.settings.get('show_bounds_text',True))
		self.show_bounds_responsive = BooleanVar()
		self.show_bounds_responsive.set(self.settings.get('show_bounds_responsive',True))

		frame = Frame(self)
		leftframe = Frame(frame)
		Label(leftframe, text='Widgets:', anchor=W).pack(side=TOP, fill=X)
		self.widgetTree = TreeList(leftframe)
		self.widgetTree.pack(side=TOP, padx=1, pady=1, fill=BOTH, expand=1)
		self.widgetTree.bind('<Button-1>', self.list_select)
		flagframe = LabelFrame(leftframe, text='Preview:')
		fields = (
			('Images','show_images',self.show_images, NORMAL),
			('Text','show_text',self.show_text, NORMAL),
			('SMKs','show_smks',self.show_smks, DISABLED),
			('Animated','show_animated',self.show_animated, DISABLED)
		)
		for i,(name,setting_name,variable,state) in enumerate(fields):
			check = Checkbutton(flagframe, text=name, variable=variable, command=lambda n=setting_name,v=variable: self.toggle_setting(n,v))
			check['state'] = state
			check.grid(row=i / 2, column=i % 2, sticky=W)
		boundsframe = LabelFrame(flagframe, text='Bounds')
		fields = (
			('Widgets','show_bounds_widget',self.show_bounds_widget, NORMAL),
			('Groups','show_bounds_group',self.show_bounds_group, NORMAL),
			('Text','show_bounds_text',self.show_bounds_text, NORMAL),
			('Responsive','show_bounds_responsive',self.show_bounds_responsive, NORMAL)
		)
		for i,(name,setting_name,variable,state) in enumerate(fields):
			check = Checkbutton(boundsframe, text=name, variable=variable, command=lambda n=setting_name,v=variable: self.toggle_setting(n,v))
			check['state'] = state
			check.grid(row=i / 2, column=i % 2, sticky=W)
		boundsframe.grid_columnconfigure(0, weight=1)
		boundsframe.grid_columnconfigure(1, weight=1)
		boundsframe.grid(row=2, column=0, columnspan=2, sticky=NSEW, padx=5, pady=5)
		flagframe.grid_columnconfigure(0, weight=1)
		flagframe.grid_columnconfigure(1, weight=1)
		flagframe.pack(side=BOTTOM, padx=1, pady=1, fill=X)
		leftframe.grid(row=0, column=0, padx=2, pady=2, sticky=NSEW)
		frame.grid_columnconfigure(0, weight=1, minsize=128)

		rightframe = Frame(frame, bd=1, relief=SUNKEN)
		self.widgetCanvas = Canvas(rightframe, background='#000000', highlightthickness=0, width=640, height=480)
		self.widgetCanvas.pack(fill=BOTH)
		self.widgetCanvas.focus_set()
		rightframe.grid(row=0, column=1, padx=2, pady=2, sticky=NSEW)
		frame.grid_columnconfigure(1, weight=0, minsize=640)
		frame.pack(fill=X)
		self.widgetCanvas.bind('<Motion>', self.mouse_motion)
		self.widgetCanvas.bind('<Leave>', lambda e: self.edit_status.set(''))
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
				self.widgetCanvas.bind(name % n, lambda e,t=etype,m=mod: self.mouse_event(e,t,m))

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
		self.status.set('Load or create a Dialog BIN.')
		statusbar.pack(side=BOTTOM, fill=X)

		self.mpqhandler = MPQHandler(self.settings.get('mpqs',[]))
		if not 'mpqs' in self.settings:
			self.mpqhandler.add_defaults()
		e = self.open_files()

		if guifile:
			self.open(file=guifile)

		start_new_thread(check_update, (self,))

		if e:
			self.mpqsettings(err=e)

	def open_files(self):
		self.mpqhandler.open_mpqs()
		err = None
		try:
			tfontgam = PCX.PCX()
			font10 = FNT.FNT()
			font14 = FNT.FNT()
			font16 = FNT.FNT()
			font16x = FNT.FNT()
			tfontgam.load_file(self.mpqhandler.get_file(self.settings['tfontgam']))
			try:
				font10.load_file(self.mpqhandler.get_file(self.settings['font10'], False))
			except:
				font10.load_file(self.mpqhandler.get_file(self.settings['font10'], True))
			try:
				font14.load_file(self.mpqhandler.get_file(self.settings['font14'], False))
			except:
				font14.load_file(self.mpqhandler.get_file(self.settings['font14'], True))
			try:
				font16.load_file(self.mpqhandler.get_file(self.settings['font16'], False))
			except:
				font16.load_file(self.mpqhandler.get_file(self.settings['font16'], True))
			try:
				font16x.load_file(self.mpqhandler.get_file(self.settings['font16x'], False))
			except:
				font16x.load_file(self.mpqhandler.get_file(self.settings['font16x'], True))
		except PyMSError, e:
			err = e
		else:
			self.tfontgam = tfontgam
			self.font10 = font10
			self.font14 = font14
			self.font16 = font16
			self.font16x = font16x
		self.mpqhandler.close_mpqs()
		return err

	def mpqsettings(self, key=None, err=None):
		data = [
			('Preview Settings',[
				('tfontgam.pcx','The special palette which holds text colors.','tfontgam','PCX'),
				('font10.fnt','Size 10 font','font10','FNT'),
				('font14.fnt','Size 14 font','font14','FNT'),
				('font16.fnt','Size 16 font','font16','FNT'),
				('font16x.fnt','Size 16x font','font16x','FNT'),
			])
		]
		SettingsDialog(self, data, (340,430), err)

	def scroll(self, e):
		if e.delta > 0:
			self.listbox.yview('scroll', -2, 'units')
		else:
			self.listbox.yview('scroll', 2, 'units')

	def move(self, e, listbox, offset):
		index = 0
		if offset == END:
			index = listbox.size()-2
		elif offset not in [0,END] and listbox.curselection():
			print listbox.curselection()
			index = max(min(listbox.size()-1, int(listbox.curselection()[0]) + offset),0)
		listbox.select_clear(0,END)
		listbox.select_set(index)
		listbox.see(index)
		return "break"

	def unsaved(self):
		if self.bin and self.edited:
			file = self.file
			if not file:
				file = 'Unnamed.bin'
			save = askquestion(parent=self, title='Save Changes?', message="Save changes to '%s'?" % file, default=YES, type=YESNOCANCEL)
			if save != 'no':
				if save == 'cancel':
					return True
				if self.file:
					self.save()
				else:
					self.saveas()

	def select_file(self, title, open=True, ext='.bin', filetypes=[('StarCraft Dialogs','*.bin'),('All Files','*')]):
		path = self.settings.get('lastpath', BASE_DIR)
		file = [tkFileDialog.asksaveasfilename,tkFileDialog.askopenfilename][open](parent=self, title=title, defaultextension=ext, filetypes=filetypes, initialdir=path)
		if file:
			self.settings['lastpath'] = os.path.dirname(file)
		return file

	def action_states(self):
		file = [NORMAL,DISABLED][not self.bin]
		for btn in ['save','saveas','export','close']:
			self.buttons[btn]['state'] = file

	def edit(self, n=None):
		self.edited = True
		self.editstatus['state'] = NORMAL
		self.action_states()

	def setup_nodes(self):
		for widget in self.bin.widgets:
			if self.dialog == None:
				self.dialog = WidgetNode(widget)
				test = self.dialog
			else:
				node = WidgetNode(widget)
				# self.dialog.add_child(node)
				if len(test.children) == 4:
					group = WidgetNode(None)
					test.add_child(group)
					test = group
				test.add_child(node)

	def flattened_nodes(self, include_groups=True):
		nodes = []
		def add_node(node):
			if node.widget or include_groups:
				nodes.append(node)
			if node.children:
				for child in node.children:
					add_node(child)
		add_node(self.dialog)
		return nodes

	def reload_list(self):
		self.widget_map = {}
		self.widgetTree.delete(ALL)
		def list_node(index, node):
			group = None
			if node.children != None:
				group = True
			node.index = self.widgetTree.insert(index, node.get_name(), group)
			self.widget_map[node.index] = node
			if node.children:
				for child in node.children:
					list_node(node.index + '.-1', child)
		list_node('-1', self.dialog)

	def update_zorder(self):
		for node in self.flattened_nodes():
			node.lift(self)
		if self.item_selection_box:
			self.widgetCanvas.lift(self.item_selection_box)

	def reload_canvas(self):
		if self.bin:
			# self.widgetCanvas.delete(ALL)
			reorder = False
			for node in self.flattened_nodes():
				reorder = node.update_display(self) or reorder
			if reorder:
				self.update_zorder()

	def toggle_setting(self, setting_name, variable):
		self.settings[setting_name] = variable.get()
		self.reload_canvas()

	def update_selection_box(self):
		if self.selected_node:
			x1,y1,x2,y2 = self.selected_node.bounding_box()
			if self.item_selection_box:
				self.widgetCanvas.coords(self.item_selection_box, x1,y1, x2,y2)
			else:
				self.item_selection_box = self.widgetCanvas.create_rectangle(x1,y1, x2,y2, width=1, outline='#ff6961')
		elif self.item_selection_box:
			self.widgetCanvas.delete(self.item_selection_box)
			self.item_selection_box = None

	def update_list_selection(self):
		if self.selected_node:
			self.widgetTree.select(self.selected_node.index)
		else:
			self.widgetTree.select(None)

	def select_node(self, node):
		self.selected_node = node
		self.update_selection_box()
		self.update_list_selection()

	def list_select(self, event):
		selected = self.widgetTree.cur_selection()
		if selected and selected[0] > -1:
			list_index = self.widgetTree.index(selected[0])
			node = self.widget_map.get(list_index)
			if node:
				self.selected_node = node
				self.update_selection_box()

	def edit_event(self, x,y, node=None, prefer_selection=False):
		if node == None:
			node = self.dialog
		found = [None,[]]
		x1,y1,x2,y2 = node.bounding_box()
		event = edit_event(x1,y1,x2,y2, x,y, node.widget != None)
		if event:
			found[0] = node
			found[1] = event
			if node.children and (not prefer_selection or node != self.selected_node):
				for child in node.children:
					found_child = self.edit_event(x,y, node=child, prefer_selection=prefer_selection)
					if found_child[0] != None:
						found = found_child
						break
		return found

	def mouse_motion(self, event):
		if self.bin:
			cursor = [self.old_cursor]
			node,mouse_event = self.edit_event(event.x,event.y)
			if node != None:
				if mouse_event[0] == EDIT_MOVE:
					cursor.extend(['crosshair','fleur','size'])
				elif mouse_event[0] == EDIT_RESIZE_LEFT:
					cursor.extend(['left_side','size_we','resizeleft','resizeleftright'])
				elif mouse_event[0] == EDIT_RESIZE_RIGHT:
					cursor.extend(['right_side','size_we','resizeright','resizeleftright'])
				if len(mouse_event) == 2:
					if mouse_event[1] == EDIT_RESIZE_TOP:
						cursor.extend(['top_side','size_ns','resizeup','resizeupdown'])
					elif mouse_event[1] == EDIT_RESIZE_BOTTOM:
						cursor.extend(['bottom_side','size_ns','resizedown','resizeupdown'])
					if mouse_event[0] == EDIT_RESIZE_LEFT and mouse_event[1] == EDIT_RESIZE_TOP:
						cursor.extend(['top_left_corner','size_nw_se','resizetopleft'])
					elif mouse_event[0] == EDIT_RESIZE_RIGHT and mouse_event[1] == EDIT_RESIZE_TOP:
						cursor.extend(['top_right_corner','size_ne_sw','resizetopright'])
					elif mouse_event[0] == EDIT_RESIZE_LEFT and mouse_event[1] == EDIT_RESIZE_BOTTOM:
						cursor.extend(['bottom_left_corner','size_ne_sw','resizebottomleft'])
					elif mouse_event[0] == EDIT_RESIZE_RIGHT and mouse_event[1] == EDIT_RESIZE_BOTTOM:
						cursor.extend(['bottom_right_corner','size_nw_se','resizebottomright'])
				if node.widget:
					self.edit_status.set('Edit Widget: ' + node.get_name())
				else:
					self.edit_status.set('Edit ' + node.get_name())
			else:
				self.edit_status.set('')
			apply_cursor(self.widgetCanvas, cursor)

	def mouse_event(self, event, button_event, modifier):
		RESTRICT_TO_DIALOG = True
		if self.bin:
			x = event.x
			y = event.y
			if button_event == MOUSE_DOWN:
	 			node,mouse_event = self.edit_event(event.x,event.y, prefer_selection=(modifier == MODIFIER_CTRL))
	 			if node:
	 				self.select_node(node)
		 			self.edit_node = node
		 			self.current_event = mouse_event
		 			if mouse_event[0] == EDIT_MOVE:
		 				x1,y1,x2,y2 = node.bounding_box()
		 				self.mouse_offset = [x1 - x, y1 - y]
		 	if self.edit_node:
		 		x1,y1,x2,y2 = self.edit_node.bounding_box()
		 		if self.current_event[0] == EDIT_MOVE:
	 				dx = (x + self.mouse_offset[0]) - x1
					dy = (y + self.mouse_offset[1]) - y1
					x1 += dx
					y1 += dy
					x2 += dx
					y2 += dy
					if RESTRICT_TO_DIALOG:
						w = x2-x1
						h = y2-y1
						rx1,ry1,rx2,ry2 = self.dialog.widget.bounding_box()
						rw = rx2-rx1
						rh = ry2-rx1
						if w < rw:
							if x1 < rx1:
								dx += rx1-x1
							elif x2 > rx2:
								dx += rx2-x2
						if h < rh:
							if y1 < ry1:
								dy += ry1-y1
							elif y2 > ry2:
								dy += ry2-y2
					def offset_node(node, delta_x,delta_y):
			 			if node.widget:
							node.widget.x1 += delta_x
							node.widget.y1 += delta_y
							node.widget.x2 += delta_x
							node.widget.y2 += delta_y
							node.update_display(self)
							if node == self.selected_node:
								self.update_selection_box()
						if node.children:
							for child in node.children:
								offset_node(child, delta_x,delta_y)
							if not node.widget:
								node.update_display(self)
								if node == self.selected_node:
									self.update_selection_box()
					offset_node(self.edit_node, dx,dy)
					check = self.edit_node
					while check.parent.widget == None:
						check.parent.update_display(self)
						check = check.parent

	def new(self, key=None):
		if not self.unsaved():
			self.bin = DialogBIN.DialogBIN()
			self.setup_nodes()
			self.reload_list()
			self.reload_canvas()
			self.file = None
			self.status.set('Editing new Dialog.')
			self.title('PyBIN %s (Unnamed.bin)' % LONG_VERSION)
			self.edited = False
			self.editstatus['state'] = DISABLED
			self.action_states()

	def open(self, key=None, file=None):
		if not self.unsaved():
			if file == None:
				file = self.select_file('Open Dialog BIN')
				if not file:
					return
			dbin = DialogBIN.DialogBIN()
			try:
				dbin.load_file(file)
			except PyMSError, e:
				ErrorDialog(self, e)
				return
			self.bin = dbin
			self.setup_nodes()
			self.reload_list()
			self.reload_canvas()
			self.title('PyBIN %s (%s)' % (LONG_VERSION,file))
			self.file = file
			self.status.set('Load Successful!')
			self.edited = False
			self.editstatus['state'] = DISABLED
			self.action_states()

	def iimport(self, key=None):
		if not self.unsaved():
			file = self.select_file('Import TXT', True, '*.txt', [('Text Files','*.txt'),('All Files','*')])
			if not file:
				return
			dbin = DialogBIN.DialogBIN()
			try:
				dbin.interpret_file(file)
			except PyMSError, e:
				ErrorDialog(self, e)
				return
			self.bin = abin
			self.title('PyBIN %s (%s)' % (LONG_VERSION,file))
			self.file = file
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
			self.bin.compile_file(self.file)
			self.status.set('Save Successful!')
			self.edited = False
			self.editstatus['state'] = DISABLED
		except PyMSError, e:
			ErrorDialog(self, e)

	def saveas(self, key=None):
		if key and self.buttons['saveas']['state'] != NORMAL:
			return
		file = self.select_file('Save Dialog BIN As', False)
		if not file:
			return True
		self.file = file
		self.save()

	def export(self, key=None):
		if key and self.buttons['export']['state'] != NORMAL:
			return
		file = self.select_file('Export TXT', False, '*.txt', [('Text Files','*.txt'),('All Files','*')])
		if not file:
			return True
		try:
			self.bin.decompile_file(file)
			self.status.set('Export Successful!')
		except PyMSError, e:
			ErrorDialog(self, e)

	def close(self, key=None):
		if key and self.buttons['close']['state'] != NORMAL:
			return
		if not self.unsaved():
			self.bin = None
			self.title('PyBIN %s' % LONG_VERSION)
			self.file = None
			self.status.set('Load or create a Dialog BIN.')
			self.edited = False
			self.editstatus['state'] = DISABLED
			self.reset()
			self.action_states()

	def register(self, e=None):
		try:
			register_registry('PyBIN','','bin',os.path.join(BASE_DIR, 'PyBIN.pyw'),os.path.join(BASE_DIR,'Images','PyGOT.ico'))
		except PyMSError, e:
			ErrorDialog(self, e)

	def help(self, e=None):
		webbrowser.open('file:///%s' % os.path.join(BASE_DIR, 'Docs', 'PyBIN.html'))

	def about(self, key=None):
		AboutDialog(self, 'PyBIN', LONG_VERSION)

	def exit(self, e=None):
		if not self.unsaved():
			savesize(self, self.settings)
			try:
				f = file(os.path.join(BASE_DIR,'Settings','PyBIN.txt'),'w')
				f.write(pprint(self.settings))
				f.close()
			except:
				pass
			self.destroy()

def main():
	import sys
	if not sys.argv or (len(sys.argv) == 1 and os.path.basename(sys.argv[0]).lower() in ['','pybin.py','pybin.pyw','pybin.exe']):
		gui = PyBIN()
		gui.mainloop()
	else:
		p = optparse.OptionParser(usage='usage: PyBIN [options] <inp> [out]', version='PyBIN %s' % LONG_VERSION)
		# p.add_option('-d', '--decompile', action='store_true', dest='convert', help="Decompile a GOT file [default]", default=True)
		# p.add_option('-c', '--compile', action='store_false', dest='convert', help="Compile a GOT file")
		# p.add_option('-t', '--trig', help="Used to compile a TRG file to a GOT compatable TRG file")
		# p.add_option('-r', '--reference', action='store_true', help="When decompiling, put a reference for settings at the top of the file [default: Off]", default=False)
		p.add_option('--gui', help="Opens a file with the GUI", default='')
		opt, args = p.parse_args()
		if opt.gui:
			gui = PyBIN(opt.gui)
			gui.mainloop()
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