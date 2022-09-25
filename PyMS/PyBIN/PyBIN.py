
from .WidgetNode import WidgetNode
from .WidgetSettings import WidgetSettings

from ..FileFormats import DialogBIN
from ..FileFormats import PCX
from ..FileFormats import GRP
from ..FileFormats import FNT

from ..Utilities.utils import WIN_REG_AVAILABLE, register_registry
from ..Utilities.UIKit import *
from ..Utilities.analytics import ga, GAScreen
from ..Utilities.trace import setup_trace
from ..Utilities.Settings import Settings
from ..Utilities.Toolbar import Toolbar
from ..Utilities import Assets
from ..Utilities.Tooltip import Tooltip
from ..Utilities.TreeList import TreeList
from ..Utilities.DropDown import DropDown
from ..Utilities.StatusBar import StatusBar
from ..Utilities.MPQHandler import MPQHandler
from ..Utilities.UpdateDialog import UpdateDialog
from ..Utilities.InternalErrorDialog import InternalErrorDialog
from ..Utilities.PyMSError import PyMSError
from ..Utilities.SettingsDialog import SettingsDialog
from ..Utilities.ErrorDialog import ErrorDialog
from ..Utilities.AboutDialog import AboutDialog
from ..Utilities.HelpDialog import HelpDialog
from ..Utilities.FileType import FileType
from ..Utilities.fileutils import check_allow_overwrite_internal_file

import time

LONG_VERSION = 'v%s' % Assets.version('PyBIN')

FRAME_DELAY = 67

MOUSE_DOWN = 0
MOUSE_MOVE = 1
MOUSE_UP = 2

EDIT_NONE = 0
EDIT_MOVE = 1
EDIT_RESIZE_LEFT = 2
EDIT_RESIZE_TOP = 3
EDIT_RESIZE_RIGHT = 4
EDIT_RESIZE_BOTTOM = 5

MODIFIER_SHIFT = 1
MODIFIER_CTRL = 2

def edit_event(x1,y1,x2,y2, mouseX,mouseY, resizable=True):
	event = []
	nx1 = (x1 if x1 < x2 else x2)
	ny1 = (y1 if y1 < y2 else y2)
	nx2 = (x2 if x2 > x1 else x1)
	ny2 = (y2 if y2 > y1 else y1)
	d = 2 * resizable
	if nx1-d <= mouseX <= nx2+d and ny1-d <= mouseY <= ny2+d:
		event.append(EDIT_MOVE)
		if resizable:
			dist_left = abs(x1 - mouseX)
			dist_right = abs(x2 - mouseX)
			if dist_left < dist_right and dist_left <= d:
				event = [EDIT_RESIZE_LEFT,EDIT_NONE]
			elif dist_right < dist_left and dist_right <= d:
				event = [EDIT_RESIZE_RIGHT,EDIT_NONE]
			dist_top = abs(y1 - mouseY)
			dist_bot = abs(y2 - mouseY)
			if dist_top < dist_bot and dist_top <= d:
				if len(event) == 1:
					event = [EDIT_NONE,EDIT_RESIZE_TOP]
				else:
					event[1] = EDIT_RESIZE_TOP
			elif dist_bot < dist_top and dist_bot <= d:
				if len(event) == 1:
					event = [EDIT_NONE,EDIT_RESIZE_BOTTOM]
				else:
					event[1] = EDIT_RESIZE_BOTTOM
	return event

class PyBIN(MainWindow):
	def __init__(self, guifile=None):

		#Window
		MainWindow.__init__(self)
		self.set_icon('PyBIN')
		self.protocol('WM_DELETE_WINDOW', self.exit)
		ga.set_application('PyBIN', Assets.version('PyBIN'))
		ga.track(GAScreen('PyBIN'))
		setup_trace('PyBIN', self)

		self.settings = Settings('PyBIN', '1')

		self.bin = None
		self.file = None
		self.edited = False
		self.dialog = None
		self.widget_map = None

		self.update_title()

		self.tfont = None
		self.dlggrp = None
		self.tilegrp = None
		self.dialog_assets = {}
		self.dialog_frames = {}

		self.selected_node = None

		self.old_cursor = None
		self.edit_node = None
		self.current_event = []
		self.mouse_offset = [0,0]
		self.event_moved = False

		self.background = None
		self.background_image = None

		self.item_background = None
		self.item_selection_box = None

		#Toolbar
		self.toolbar = Toolbar(self)
		self.toolbar.add_button(Assets.get_image('new'), self.new, 'New', Ctrl.n)
		self.toolbar.add_gap()
		self.toolbar.add_button(Assets.get_image('open'), self.open, 'Open', Ctrl.o)
		self.toolbar.add_button(Assets.get_image('import'), self.iimport, 'Import from TXT', Ctrl.i)
		self.toolbar.add_gap()
		self.toolbar.add_button(Assets.get_image('save'), self.save, 'Save', Ctrl.s, enabled=False, tags='file_open')
		self.toolbar.add_button(Assets.get_image('saveas'), self.saveas, 'Save As', Ctrl.Alt.a, enabled=False, tags='file_open')
		self.toolbar.add_button(Assets.get_image('export'), self.export, 'Export to TXT', Ctrl.e, enabled=False, tags='file_open')
		self.toolbar.add_gap()
		self.toolbar.add_button(Assets.get_image('close'), self.close, 'Close', Ctrl.w, enabled=False, tags='file_open')
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('asc3topyai'), self.mpqsettings, 'Manage Settings', Ctrl.m)
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('register'), self.register, 'Set as default *.bin editor (Windows Only)', enabled=WIN_REG_AVAILABLE)
		self.toolbar.add_button(Assets.get_image('help'), self.help, 'Help', Key.F4)
		self.toolbar.add_button(Assets.get_image('about'), self.about, 'About PyBIN')
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('exit'), self.exit, 'Exit', Shortcut.Exit)
		self.toolbar.pack(side=TOP, padx=1, pady=1, fill=X)

		self.show_preview_settings = BooleanVar()
		self.show_images = BooleanVar()
		self.show_text = BooleanVar()
		self.show_smks = BooleanVar()
		self.show_hidden = BooleanVar()
		self.show_dialog = BooleanVar()
		self.show_animated = BooleanVar()
		self.show_hover_smks = BooleanVar()
		self.show_background = BooleanVar()
		self.show_theme_index = IntVar()
		self.show_bounds_widget = BooleanVar()
		self.show_bounds_group = BooleanVar()
		self.show_bounds_text = BooleanVar()
		self.show_bounds_responsive = BooleanVar()
		self.load_settings()

		self.last_tick = None
		self.tick_alarm = None

		self.type_menu = Menu(self, tearoff=0)
		fields = (
			(DialogBIN.BINWidget.TYPE_NAMES[DialogBIN.BINWidget.TYPE_DEFAULT_BTN], DialogBIN.BINWidget.TYPE_DEFAULT_BTN),
			(DialogBIN.BINWidget.TYPE_NAMES[DialogBIN.BINWidget.TYPE_BUTTON], DialogBIN.BINWidget.TYPE_BUTTON),
			(DialogBIN.BINWidget.TYPE_NAMES[DialogBIN.BINWidget.TYPE_OPTION_BTN], DialogBIN.BINWidget.TYPE_OPTION_BTN),
			(DialogBIN.BINWidget.TYPE_NAMES[DialogBIN.BINWidget.TYPE_CHECKBOX], DialogBIN.BINWidget.TYPE_CHECKBOX),
			(DialogBIN.BINWidget.TYPE_NAMES[DialogBIN.BINWidget.TYPE_IMAGE], DialogBIN.BINWidget.TYPE_IMAGE),
			(DialogBIN.BINWidget.TYPE_NAMES[DialogBIN.BINWidget.TYPE_SLIDER], DialogBIN.BINWidget.TYPE_SLIDER),
			(DialogBIN.BINWidget.TYPE_NAMES[DialogBIN.BINWidget.TYPE_UNK], DialogBIN.BINWidget.TYPE_UNK),
			(DialogBIN.BINWidget.TYPE_NAMES[DialogBIN.BINWidget.TYPE_TEXTBOX], DialogBIN.BINWidget.TYPE_TEXTBOX),
			(DialogBIN.BINWidget.TYPE_NAMES[DialogBIN.BINWidget.TYPE_LABEL_LEFT_ALIGN], DialogBIN.BINWidget.TYPE_LABEL_LEFT_ALIGN),
			(DialogBIN.BINWidget.TYPE_NAMES[DialogBIN.BINWidget.TYPE_LABEL_RIGHT_ALIGN], DialogBIN.BINWidget.TYPE_LABEL_RIGHT_ALIGN),
			(DialogBIN.BINWidget.TYPE_NAMES[DialogBIN.BINWidget.TYPE_LABEL_CENTER_ALIGN], DialogBIN.BINWidget.TYPE_LABEL_CENTER_ALIGN),
			(DialogBIN.BINWidget.TYPE_NAMES[DialogBIN.BINWidget.TYPE_LISTBOX], DialogBIN.BINWidget.TYPE_LISTBOX),
			(DialogBIN.BINWidget.TYPE_NAMES[DialogBIN.BINWidget.TYPE_COMBOBOX], DialogBIN.BINWidget.TYPE_COMBOBOX),
			(DialogBIN.BINWidget.TYPE_NAMES[DialogBIN.BINWidget.TYPE_HIGHLIGHT_BTN], DialogBIN.BINWidget.TYPE_HIGHLIGHT_BTN),
			(DialogBIN.BINWidget.TYPE_NAMES[DialogBIN.BINWidget.TYPE_HTML] + ' (SC:R)', DialogBIN.BINWidget.TYPE_HTML),
			None,
			('Group',-1),
		)
		for info in fields:
			if info:
				self.type_menu.add_command(label=info[0], command=lambda t=info[1]: self.add_new_node(t))
			else:
				self.type_menu.add_separator()

		self.scr_enabled = IntVar()

		frame = Frame(self)
		leftframe = Frame(frame)
		titleframe = Frame(leftframe)
		Label(titleframe, text='Widgets:', anchor=W).pack(side=LEFT)
		self.scr_check = Checkbutton(titleframe, text='SC:R', variable=self.scr_enabled, command=lambda: self.scr_toggled(), state=DISABLED)
		Tooltip(self.scr_check, 'StarCraft: Remastered compatibility (Automatically enabled when using SC:R widgets)')
		self.scr_check.pack(side=RIGHT, padx=(0,20))
		titleframe.grid(row=0, column=0, sticky=EW)

		self.widgetTree = TreeList(leftframe)
		self.widgetTree.grid(row=1, column=0, padx=1, pady=1, sticky=NSEW)
		self.widgetTree.bind(Mouse.Click_Left, self.list_select)
		self.widgetTree.bind(Mouse.Drag_Left, self.list_drag)
		self.widgetTree.bind(ButtonRelease.Click_Left, self.list_drop)
		self.widgetTree.bind(Double.Click_Left, self.list_double_click)

		self.widgets_toolbar = Toolbar(leftframe)
		self.widgets_toolbar.add_button(Assets.get_image('add'), self.add_node, 'Add Widget', enabled=False, tags='file_open')
		self.widgets_toolbar.add_button(Assets.get_image('remove'), self.remove_node, 'Remove Selected', enabled=False, tags=('node_selected', 'dialog_not_selected'))
		self.widgets_toolbar.add_button(Assets.get_image('edit'), self.edit_node_settings, 'Edit Widget', enabled=False, tags='node_selected')
		self.widgets_toolbar.add_spacer(2, flexible=True)
		self.widgets_toolbar.add_button(Assets.get_image('arrow'), self.toggle_preview_settings, 'Toggle Preview Settings', identifier='settings_toggle')
		self.widgets_toolbar.add_spacer(2, flexible=True)
		self.widgets_toolbar.add_button(Assets.get_image('up'), lambda: self.move_node(-1), 'Move Widget Up', enabled=False, tags='can_move_up')
		self.widgets_toolbar.add_button(Assets.get_image('down'), lambda: self.move_node(2), 'Move Widget Down', enabled=False, tags='can_move_down')
		self.widgets_toolbar.grid(row=2, column=0, padx=1, pady=1, sticky=EW)

		self.preview_settings_frame = LabelFrame(leftframe, text='Preview Settings')
		widgetsframe = LabelFrame(self.preview_settings_frame, text='Widget')
		fields = (
			('Images','show_images',self.show_images),
			('Text','show_text',self.show_text),
			('SMKs','show_smks',self.show_smks),
			('Hidden','show_hidden',self.show_hidden),
			('Dialog','show_dialog',self.show_dialog)
		)
		for i,(name,setting_name,variable) in enumerate(fields):
			check = Checkbutton(widgetsframe, text=name, variable=variable, command=lambda n=setting_name,v=variable: self.toggle_setting(n,v))
			check.grid(row=i / 2, column=i % 2, sticky=W)
		widgetsframe.grid_columnconfigure(0, weight=1)
		widgetsframe.grid_columnconfigure(1, weight=1)
		widgetsframe.grid(row=0, column=0, sticky=NSEW, padx=5)
		smkframe = LabelFrame(self.preview_settings_frame, text='SMKs')
		fields = (
			('Animated','show_animated',self.show_animated),
			('Hovers','show_hover_smks',self.show_hover_smks)
		)
		for i,(name,setting_name,variable) in enumerate(fields):
			check = Checkbutton(smkframe, text=name, variable=variable, command=lambda n=setting_name,v=variable: self.toggle_setting(n,v))
			check.grid(row=i / 2, column=i % 2, sticky=W)
		smkframe.grid_columnconfigure(0, weight=1)
		smkframe.grid_columnconfigure(1, weight=1)
		smkframe.grid(row=1, column=0, sticky=NSEW, padx=5)
		boundsframe = LabelFrame(self.preview_settings_frame, text='Bounds')
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
		boundsframe.grid(row=2, column=0, sticky=NSEW, padx=5)
		themeframe = LabelFrame(self.preview_settings_frame, text='Theme')
		themes = ['None']
		for t in range(DialogBIN.THEME_ASSETS_MAIN_MENU,DialogBIN.THEME_ASSETS_NONE):
			theme = DialogBIN.THEME_ASSETS_INFO[t]
			themes.append('%s (%s)' % (theme['name'],theme['path']))
		DropDown(themeframe, self.show_theme_index, themes, self.change_theme).grid(row=0, column=0, padx=5, sticky=EW)
		Checkbutton(themeframe, text='Background', variable=self.show_background, command=lambda: self.toggle_setting('show_background',self.show_background)).grid(row=1, column=0, sticky=W)
		themeframe.grid_columnconfigure(0, weight=1)
		# themeframe.grid_columnconfigure(1, weight=1)
		themeframe.grid(row=3, column=0, sticky=NSEW, padx=5)
		self.preview_settings_frame.grid_columnconfigure(0, weight=1)
		self.preview_settings_frame.grid(row=3, column=0, padx=1,pady=1, ipady=3, sticky=NSEW)
		if not self.show_preview_settings.get():
			self.preview_settings_frame.grid_remove()
		leftframe.grid_rowconfigure(1, weight=1)
		leftframe.grid_columnconfigure(0, weight=1)
		leftframe.grid(row=0, column=0, padx=2, pady=2, sticky=NSEW)
		frame.grid_columnconfigure(0, weight=1, minsize=128)

		rightframe = Frame(frame)
		Label(rightframe, text='Canvas:', anchor=W).pack(side=TOP, fill=X)
		bdframe = Frame(rightframe, borderwidth=1, relief=SUNKEN)
		self.widgetCanvas = Canvas(bdframe, background='#000000', highlightthickness=0, width=640, height=480)
		self.widgetCanvas.pack()
		self.widgetCanvas.focus_set()
		bdframe.pack(side=TOP)
		rightframe.grid(row=0, column=1, padx=(2,5), pady=2, sticky=NSEW)
		frame.grid_columnconfigure(1, weight=0, minsize=640)
		frame.grid_rowconfigure(0, weight=1, minsize=480)
		frame.pack(fill=BOTH, expand=1)
		self.widgetCanvas.bind(Mouse.Motion, self.mouse_motion)
		self.widgetCanvas.bind(Cursor.Leave, lambda e: self.edit_status.set(''))
		self.widgetCanvas.bind(Double.Click_Left, lambda e,m=0: self.canvas_double_click(e,m))
		self.widgetCanvas.bind(Ctrl.Double.Click_Left, lambda e,m=MODIFIER_CTRL: self.canvas_double_click(e,m))

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
				self.widgetCanvas.bind(event, lambda e,t=etype,m=mod: self.mouse_event(e,t,m))

		self.bind(Key.Return, self.list_double_click)

		#Statusbar
		self.status = StringVar()
		self.status.set('Load or create a Dialog BIN.')
		self.edit_status = StringVar()
		statusbar = StatusBar(self)
		statusbar.add_label(self.status, width=35)
		self.editstatus = statusbar.add_icon(Assets.get_image('save'))
		statusbar.add_label(self.edit_status, weight=1)
		statusbar.pack(side=BOTTOM, fill=X)

		self.update_idletasks()
		w,h,_,_,_ = parse_geometry(self.winfo_geometry())
		self.minsize(w,h)
		self.settings.windows.load_window_size('main', self)

		self.mpqhandler = MPQHandler(self.settings.settings.get('mpqs',[]))
		if not len(self.mpqhandler.mpq_paths()) and self.mpqhandler.add_defaults():
			self.settings.settings.mpqs = self.mpqhandler.mpq_paths()
		e = self.open_files()

		if guifile:
			self.open(file=guifile)

		UpdateDialog.check_update(self, 'PyBIN')

		if e:
			self.mpqsettings(err=e)

	def tick(self, start=False):
		if self.tick_alarm or start:
			if self.bin:
				now = int(time.time() * 1000)
				if self.last_tick == None:
					self.last_tick = now
				dt = now - self.last_tick
				self.last_tick = now
				for node in self.flattened_nodes():
					node.tick(dt)
					node.update_video()
				self.widgetCanvas.update_idletasks()
				self.tick_alarm = self.after(FRAME_DELAY,self.tick)
			else:
				self.tick_alarm = None

	def stop_tick(self):
		if self.tick_alarm != None:
			cancel = self.tick_alarm
			self.tick_alarm = None
			self.after_cancel(cancel)

	def scr_toggled(self):
		self.bin.remastered = self.scr_enabled.get()

	def toggle_preview_settings(self):
		show = not self.show_preview_settings.get()
		self.show_preview_settings.set(show)
		if show:
			self.widgets_toolbar.update_icon('settings_toggle', Assets.get_image('arrow'))
			self.preview_settings_frame.grid(sticky=EW)
		else:
			self.widgets_toolbar.update_icon('settings_toggle', Assets.get_image('arrowup'))
			self.preview_settings_frame.grid_remove()

	def add_node(self):
		self.type_menu.post(*self.winfo_pointerxy())

	def add_new_node(self, ctrl_type):
		parent = self.dialog
		index = 0
		if self.selected_node:
			if self.selected_node.children != None:
				parent = self.selected_node
			else:
				parent = self.selected_node.parent
				index = parent.children.index(self.selected_node)
		node = None
		if ctrl_type == -1:
			node = WidgetNode(self)
		else:
			x1,y1,x2,y2 = parent.bounding_box()
			widget = DialogBIN.BINWidget(ctrl_type)
			widget.width = 201
			widget.height = 101
			widget.x1 = x1 + (x2-x1-(widget.width-1)) / 2
			widget.y1 = y1 + (y2-y1-(widget.height-1)) / 2
			widget.x2 = widget.x1 + widget.width-1
			widget.y2 = widget.y1 + widget.height-1
			if widget.flags & DialogBIN.BINWidget.FLAG_RESPONSIVE:
				widget.responsive_x1 = 0
				widget.responsive_y1 = 0
				widget.responsive_x2 = widget.width-1
				widget.responsive_y2 = widget.height-1
			self.bin.widgets.append(widget)
			node = WidgetNode(self, widget)
			if ctrl_type >= DialogBIN.BINWidget.TYPE_HTML:
				self.scr_enabled.set(True)
		parent.add_child(node, index)
		self.reload_list()
		self.reload_canvas()
		self.select_node(node)
		self.mark_edited()

	def remove_node(self):
		self.selected_node.remove_display()
		if self.selected_node.widget:
			self.bin.widgets.remove(self.selected_node.widget)
			if self.selected_node.widget.type >= DialogBIN.BINWidget.TYPE_HTML and not self.bin.remastered:
				self.scr_enabled.set(False)
			self.action_states()
		self.selected_node.remove_from_parent()
		self.selected_node = None
		self.update_selection_box()
		self.reload_list()
		self.mark_edited()

	def move_node(self, delta):
		index = self.selected_node.parent.children.index(self.selected_node)
		dest = index + delta
		if 0 <= dest <= len(self.selected_node.parent.children):
			self.selected_node.parent.children.insert(dest, self.selected_node)
			del self.selected_node.parent.children[index + (dest < index)]
			self.reload_list()
			self.action_states()
			self.update_zorder()
			self.mark_edited()

	def update_background(self):
		if self.bin and self.show_theme_index.get() and not self.background:
			try:
				path = 'MPQ:' + DialogBIN.THEME_ASSETS_INFO[self.show_theme_index.get()-1]['path'] + 'backgnd.pcx'
				background = PCX.PCX()
				background.load_file(self.mpqhandler.get_file(path))
			except:
				InternalErrorDialog.capture(self, 'PyBIN')
			else:
				self.background = background
		elif not self.show_theme_index.get() and self.background:
			self.background = None
		delete = True
		if self.bin and self.show_background.get() and self.background:
			if not self.background_image:
				self.background_image = GRP.frame_to_photo(self.background.palette, self.background, -1, size=False)
			if self.background_image:
				delete = False
				if self.item_background:
					self.widgetCanvas.itemconfigure(self.item_background, image=self.background_image)
				else:
					self.item_background = self.widgetCanvas.create_image(0,0, image=self.background_image, anchor=NW)
					self.widgetCanvas.lower(self.item_background)
		if self.item_background and delete:
			self.widgetCanvas.delete(self.item_background)
			self.item_background = None

	def load_dlggrp(self):
		dlggrp = None
		check = ['MPQ:glue\\palmm\\dlg.grp']
		if self.show_theme_index.get():
			path = 'MPQ:' + DialogBIN.THEME_ASSETS_INFO[self.show_theme_index.get()-1]['path'] + 'dlg.grp'
			check.insert(0, path)
		for path in check:
			try:
				dlggrp = GRP.GRP()
				dlggrp.load_file(self.mpqhandler.get_file(path), uncompressed=True)
			except:
				InternalErrorDialog.capture(self, 'PyBIN')
			else:
				break
		self.dlggrp = dlggrp
		self.dialog_assets = {}
		# if self.bin:
		# 	for widget in self.flattened_nodes():
		# 		pass
			# self.reload_canvas()

	def dialog_asset(self, asset_id):
		asset = None
		if self.dlggrp and self.background:
			if asset_id in self.dialog_assets:
				asset = self.dialog_assets[asset_id]
			else:
				asset = GRP.image_to_pil(self.dlggrp.images[asset_id], self.background.palette, image_bounds=self.dlggrp.images_bounds[asset_id])
				self.dialog_assets[asset_id] = asset
		return asset

	def load_tilegrp(self):
		tilegrp = None
		check = ['MPQ:glue\\palmm\\tile.grp']
		if self.show_theme_index.get():
			path = 'MPQ:' + DialogBIN.THEME_ASSETS_INFO[self.show_theme_index.get()-1]['path'] + 'tile.grp'
			check.insert(0, path)
		for path in check:
			try:
				tilegrp = GRP.GRP()
				tilegrp.load_file(self.mpqhandler.get_file(path))
			except:
				InternalErrorDialog.capture(self, 'PyBIN')
			else:
				break
		self.tilegrp = tilegrp
		self.dialog_frames = {}
		# if self.bin:
		# 	for widget in self.flattened_nodes():
		# 		pass
			# self.reload_canvas()

	def dialog_frame(self, frame_id):
		frame = None
		if self.tilegrp and self.background:
			if frame_id in self.dialog_frames:
				frame = self.dialog_frames[frame_id]
			else:
				frame = GRP.image_to_pil(self.tilegrp.images[frame_id], self.background.palette, image_bounds=self.tilegrp.images_bounds[frame_id])
				self.dialog_frames[frame_id] = frame
		return frame

	def load_tfont(self):
		tfont = None
		check = ['MPQ:glue\\title\\tfont.pcx']
		if self.show_theme_index.get():
			path = 'MPQ:' + DialogBIN.THEME_ASSETS_INFO[self.show_theme_index.get()-1]['path'] + 'tfont.pcx'
			check.insert(0, path)
		for path in check:
			try:
				tfont = PCX.PCX()
				tfont.load_file(self.mpqhandler.get_file(path))
			except:
				tfont = None
			else:
				break
		self.tfont = tfont
		if self.bin:
			for widget in self.flattened_nodes():
				widget.string = None
				widget.item_string_images = None
			# self.reload_canvas()

	def change_theme(self, n):
		index = self.show_theme_index.get()-1
		if index != self.settings.preview.get('theme_id'):
			self.settings.preview.theme_id = index
			self.background = None
			self.background_image = None
			self.update_background()
			self.load_dlggrp()
			self.load_tilegrp()
			self.load_tfont()
			self.reload_canvas()

	def open_files(self):
		self.mpqhandler.open_mpqs()
		err = None
		try:
			tfontgam = PCX.PCX()
			font10 = FNT.FNT()
			font14 = FNT.FNT()
			font16 = FNT.FNT()
			font16x = FNT.FNT()

			tfontgam.load_file(self.mpqhandler.get_file(self.settings.settings.files.get('tfontgam', 'MPQ:game\\tfontgam.pcx')))
			path = self.settings.settings.files.get('font10', 'MPQ:font\\font10.fnt')
			try:
				font10.load_file(self.mpqhandler.get_file(path, False))
			except:
				font10.load_file(self.mpqhandler.get_file(path, True))
			path = self.settings.settings.files.get('font14', 'MPQ:font\\font14.fnt')
			try:
				font14.load_file(self.mpqhandler.get_file(path, False))
			except:
				font14.load_file(self.mpqhandler.get_file(path, True))
			path = self.settings.settings.files.get('font16', 'MPQ:font\\font16.fnt')
			try:
				font16.load_file(self.mpqhandler.get_file(path, False))
			except:
				font16.load_file(self.mpqhandler.get_file(path, True))
			path = self.settings.settings.files.get('font16x', 'MPQ:font\\font16x.fnt')
			try:
				font16x.load_file(self.mpqhandler.get_file(path, False))
			except:
				font16x.load_file(self.mpqhandler.get_file(path, True))
		except PyMSError as e:
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
		SettingsDialog(self, data, (340,430), err, settings=self.settings, mpqhandler=self.mpqhandler)

	def unsaved(self):
		if self.bin and self.edited:
			file = self.file
			if not file:
				file = 'Unnamed.bin'
			save = MessageBox.askquestion(parent=self, title='Save Changes?', message="Save changes to '%s'?" % file, default=MessageBox.YES, type=MessageBox.YESNOCANCEL)
			if save != MessageBox.NO:
				if save == MessageBox.CANCEL:
					return True
				if self.file:
					self.save()
				else:
					self.saveas()

	def is_file_open(self):
		return not not self.bin

	def has_selected_node(self):
		return self.selected_node != None

	def action_states(self):
		is_file_open = self.is_file_open()
		self.toolbar.tag_enabled('file_open', is_file_open)

		has_selected_node = self.has_selected_node()
		selection_is_dialog = (has_selected_node and self.selected_node.widget and self.selected_node.widget.type == DialogBIN.BINWidget.TYPE_DIALOG)
		can_move_up = False
		can_move_down = False
		if has_selected_node and not not self.selected_node.parent:
			index = self.selected_node.parent.children.index(self.selected_node)
			can_move_up = (index > 0)
			can_move_down = (index < len(self.selected_node.parent.children)-1)
		self.widgets_toolbar.tag_enabled('file_open', is_file_open)
		self.widgets_toolbar.tag_enabled('node_selected', has_selected_node)
		self.widgets_toolbar.tag_enabled('dialog_not_selected', not selection_is_dialog)
		self.widgets_toolbar.tag_enabled('can_move_up', can_move_up)
		self.widgets_toolbar.tag_enabled('can_move_down', can_move_down)

		# self.scr_check['state'] = NORMAL if is_file_open and not self.bin.remastered_required() else DISABLED

	def mark_edited(self, edited=True):
		self.edited = edited
		self.editstatus['state'] = NORMAL if edited else DISABLED
		self.action_states()

	def setup_nodes(self):
		for widget in self.bin.widgets:
			node = WidgetNode(self, widget)
			if self.dialog == None:
				self.dialog = node
			else:
				self.dialog.add_child(node)

	def flattened_nodes(self, include_groups=True):
		nodes = []
		def add_node(node):
			if node.widget or include_groups:
				nodes.append(node)
			if node.children:
				for child in node.children:
					add_node(child)
		if self.dialog:
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
			if node == self.selected_node:
				self.widgetTree.select(node.index)
				self.widgetTree.see(node.index)
			self.widget_map[node.index] = node
			if node.children:
				for child in reversed(node.children):
					list_node(node.index + '.-1', child)
		list_node('-1', self.dialog)

	def update_zorder(self):
		for node in self.flattened_nodes():
			node.lift()
		if self.item_selection_box:
			self.widgetCanvas.lift(self.item_selection_box)

	def reload_canvas(self):
		if self.bin:
			# self.widgetCanvas.delete(ALL)
			self.update_background()
			reorder = False
			for node in self.flattened_nodes():
				reorder = node.update_display() or reorder
			self.update_selection_box()
			if reorder:
				self.update_zorder()

	def toggle_setting(self, setting_name, variable):
		self.settings.preview[setting_name] = variable.get()
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
			self.widgetTree.see(self.selected_node.index)
		else:
			self.widgetTree.select(None)

	def edit_node_settings(self, node=None):
		if node == None:
			node = self.selected_node
		if node and node.widget:
			WidgetSettings(self, node)

	def canvas_double_click(self, e, m):
		if self.bin:
			prefer_selection = (m == MODIFIER_CTRL)
			def check_clicked(node, x,y):
				found = None
				x1,y1,x2,y2 = node.bounding_box()
				if node.widget:
					x1 = node.widget.x1
					y1 = node.widget.y1
					x2 = node.widget.x2
					y2 = node.widget.y2
				event = edit_event(x1,y1,x2,y2, x,y, False)
				if event:
					found = node
					if node.children and (not prefer_selection or node != self.selected_node):
						for child in reversed(node.children):
							found_child = check_clicked(child, x,y)
							if found_child != None:
								found = found_child
				return found
			node = check_clicked(self.dialog, e.x,e.y)
			if node:
				self.edit_node_settings(node)

	def list_double_click(self, event):
		selected = self.widgetTree.cur_selection()
		if selected and selected[0] > -1:
			list_index = self.widgetTree.index(selected[0])
			node = self.widget_map.get(list_index)
			if node:
				self.edit_node_settings(node)

	def select_node(self, node):
		self.selected_node = node
		self.update_selection_box()
		self.update_list_selection()
		self.action_states()

	def list_select(self, event):
		selected = self.widgetTree.cur_selection()
		if selected and selected[0] > -1:
			list_index = self.widgetTree.index(selected[0])
			self.selected_node = self.widget_map[list_index]
			self.update_selection_box()
			self.action_states()

	def list_drag(self, event):
		# todo: Not started on node?
		if self.selected_node and (not self.selected_node.widget or self.selected_node.widget.type != DialogBIN.BINWidget.TYPE_DIALOG):
			index = self.widgetTree.index("@%d,%d" % (event.x, event.y))
			self.widgetTree.highlight(index)

	def list_drop(self, event):
		# todo: Not started on node?
		if self.selected_node and (not self.selected_node.widget or self.selected_node.widget.type != DialogBIN.BINWidget.TYPE_DIALOG):
			self.widgetTree.highlight(None)
			index,below = self.widgetTree.lookup_coords(event.x, event.y)
			if index and index != self.selected_node.index:
				highlight = self.widget_map[index]
				if self.selected_node.children:
					check = highlight.parent
					while check:
						if check == self.selected_node:
							return
						check = check.parent
				if highlight.children != None:
					highlight.add_child(self.selected_node)
				else:
					highlight.parent.add_child(self.selected_node, highlight.parent.children.index(highlight) + below)
				self.reload_list()
				self.reload_canvas()
				self.mark_edited()

	def edit_event(self, x,y, node=None, prefer_selection=False):
		if node == None:
			node = self.dialog
		found = [None,[]]
		x1,y1,x2,y2 = node.bounding_box()
		if node.widget:
			x1 = node.widget.x1
			y1 = node.widget.y1
			x2 = node.widget.x2
			y2 = node.widget.y2
		event = edit_event(x1,y1,x2,y2, x,y, node.widget != None)
		if event:
			found[0] = node
			found[1] = event
		if node.children and (not prefer_selection or node != self.selected_node):
			for child in reversed(node.children):
				found_child = self.edit_event(x,y, node=child, prefer_selection=prefer_selection)
				if found_child[0] != None:
					found = found_child
					break
		return found

	def mouse_motion(self, event):
		if self.bin:
			if self.old_cursor == None:
				self.old_cursor = self.widgetCanvas.cget('cursor')
			cursor = [self.old_cursor]
			node,mouse_event = self.edit_event(event.x,event.y)
			if node != None:
				if node.widget:
					if node.widget.x1 > node.widget.x2:
						if EDIT_RESIZE_LEFT in mouse_event:
							mouse_event[mouse_event.index(EDIT_RESIZE_LEFT)] = EDIT_RESIZE_RIGHT
						elif EDIT_RESIZE_RIGHT in mouse_event:
							mouse_event[mouse_event.index(EDIT_RESIZE_RIGHT)] = EDIT_RESIZE_LEFT
					if node.widget.y1 > node.widget.y2:
						if EDIT_RESIZE_TOP in mouse_event:
							mouse_event[mouse_event.index(EDIT_RESIZE_TOP)] = EDIT_RESIZE_BOTTOM
						elif EDIT_RESIZE_BOTTOM in mouse_event:
							mouse_event[mouse_event.index(EDIT_RESIZE_BOTTOM)] = EDIT_RESIZE_TOP
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
		RESTRICT_TO_WINDOW = True
		if self.bin:
			x = event.x
			y = event.y
			if button_event == MOUSE_DOWN:
				node,mouse_event = self.edit_event(event.x,event.y, prefer_selection=(modifier == MODIFIER_CTRL))
				self.select_node(node)
				if node:
					self.edit_node = node
					self.current_event = mouse_event
					self.event_moved = False
					if mouse_event[0] == EDIT_MOVE:
						x1,y1,x2,y2 = node.bounding_box()
						self.mouse_offset = [x1 - x, y1 - y]
			if self.edit_node:
				if button_event == MOUSE_MOVE:
					self.event_moved = True
				x1,y1,x2,y2 = self.edit_node.bounding_box()
				if self.current_event[0] == EDIT_MOVE:
					dx = (x + self.mouse_offset[0]) - x1
					dy = (y + self.mouse_offset[1]) - y1
					x1 += dx
					y1 += dy
					x2 += dx
					y2 += dy
					if RESTRICT_TO_WINDOW:
						w = x2-x1
						h = y2-y1
						rx1,ry1,rx2,ry2 = (0,0,640,480) #self.dialog.widget.bounding_box()
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
						if node.children:
							for child in node.children:
								offset_node(child, delta_x,delta_y)
						node.update_display()
						if node == self.selected_node:
							self.update_selection_box()
					offset_node(self.edit_node, dx,dy)
					if dx or dy:
						self.mark_edited()
				elif self.event_moved:
					rdx2,rdy2 = 0,0
					if EDIT_RESIZE_LEFT in self.current_event:
						rdx2 = self.edit_node.widget.x1 - x
						self.edit_node.widget.x1 = x
					elif EDIT_RESIZE_RIGHT in self.current_event:
						rdx2 = x - self.edit_node.widget.x2
						self.edit_node.widget.x2 = x
					if EDIT_RESIZE_TOP in self.current_event:
						rdy2 = self.edit_node.widget.y1 - y
						self.edit_node.widget.y1 = y
					elif EDIT_RESIZE_BOTTOM in self.current_event:
						rdy2 = y - self.edit_node.widget.y2
						self.edit_node.widget.y2 = y
					if rdx2 > 0:
						self.edit_node.widget.responsive_x2 += rdx2
					elif self.edit_node.widget.x1+self.edit_node.widget.responsive_x1+self.edit_node.widget.responsive_x2 > self.edit_node.widget.x2:
						self.edit_node.widget.responsive_x2 = self.edit_node.widget.x2-self.edit_node.widget.x1-self.edit_node.widget.responsive_x1
					if rdy2 > 0:
						self.edit_node.widget.responsive_y2 += rdy2
					elif self.edit_node.widget.y1+self.edit_node.widget.responsive_y1+self.edit_node.widget.responsive_y2 > self.edit_node.widget.y2:
						self.edit_node.widget.responsive_y2 = self.edit_node.widget.y2-self.edit_node.widget.y1-self.edit_node.widget.responsive_y1
					self.edit_node.widget.width = abs(self.edit_node.widget.x2-self.edit_node.widget.x1) + 1
					self.edit_node.widget.height = abs(self.edit_node.widget.y2-self.edit_node.widget.y1) + 1
					self.edit_node.widget.responsive_width = abs(self.edit_node.widget.responsive_x2-self.edit_node.widget.responsive_x1) + 1
					self.edit_node.widget.responsive_height = abs(self.edit_node.widget.responsive_y2-self.edit_node.widget.responsive_y1) + 1
					self.edit_node.update_display()
					if self.edit_node == self.selected_node:
						self.update_selection_box()
					self.mark_edited()
				check = self.edit_node
				while check.parent and check.parent.widget == None:
					check.parent.update_display()
					check = check.parent
				if button_event == MOUSE_UP:
					self.edit_node = None
					self.current_event = []
					self.mouse_offset = [0, 0]

	def clear(self):
		self.bin = None
		self.file = None
		self.edited = False
		self.dialog = None
		self.widget_map = None

		self.update_title()

		self.selected_node = None
		self.old_cursor = None
		self.edit_node = None
		self.current_event = []
		self.mouse_offset = [0,0]

		self.background = None
		self.background_image = None

		self.item_background = None
		self.item_selection_box = None

		self.widgetTree.delete(ALL)
		self.widgetCanvas.delete(ALL)

	def update_title(self):
		file_path = self.file
		if not file_path and self.is_file_open():
			file_path = 'Untitled.bin'
		if not file_path:
			self.title('PyBIN %s' % LONG_VERSION)
		else:
			self.title('PyBIN %s (%s)' % (LONG_VERSION, file_path))

	def new(self, key=None):
		if not self.unsaved():
			if not self.tfont:
				self.load_tfont()
			if not self.dlggrp:
				self.load_dlggrp()
			if not self.tilegrp:
				self.load_tilegrp()
			self.clear()
			self.bin = DialogBIN.DialogBIN()
			self.setup_nodes()
			self.reload_list()
			self.reload_canvas()
			self.file = None
			self.status.set('Editing new Dialog.')
			self.update_title()
			self.mark_edited(False)
			self.action_states()
			self.tick(True)

	def open(self, key=None, file=None):
		if not self.unsaved():
			if file == None:
				file = self.settings.lastpath.bin.select_open_file(self, title='Open Dialog BIN', filetypes=[FileType.bin_dialog()])
				if not file:
					return
			dbin = DialogBIN.DialogBIN()
			try:
				dbin.load_file(file)
			except PyMSError as e:
				ErrorDialog(self, e)
				return
			if not self.tfont:
				self.load_tfont()
			if not self.dlggrp:
				self.load_dlggrp()
			if not self.tilegrp:
				self.load_tilegrp()
			self.clear()
			self.bin = dbin
			self.setup_nodes()
			self.reload_list()
			self.reload_canvas()
			self.file = file
			self.update_title()
			self.scr_enabled.set(self.bin.remastered)
			self.status.set('Load Successful!')
			self.mark_edited(False)
			self.select_node(self.dialog)
			self.action_states()
			self.tick(True)

	def iimport(self, key=None):
		if not self.unsaved():
			file = self.settings.lastpath.txt.select_open_file(self, key='import', title='Import TXT', filetypes=[FileType.txt()])
			if not file:
				return
			dbin = DialogBIN.DialogBIN()
			try:
				dbin.interpret_file(file)
			except PyMSError as e:
				ErrorDialog(self, e)
				return
			if not self.tfont:
				self.load_tfont()
			if not self.dlggrp:
				self.load_dlggrp()
			if not self.tilegrp:
				self.load_tilegrp()
			self.clear()
			self.bin = dbin
			self.setup_nodes()
			self.reload_list()
			self.reload_canvas()
			self.file = file
			self.update_title()
			self.scr_enabled.set(self.bin.remastered)
			self.status.set('Import Successful!')
			self.mark_edited(False)
			self.action_states()
			self.tick(True)

	def save(self, key=None):
		self.saveas(file_path=self.file)

	def saveas(self, key=None, file_path=None):
		if not file_path:
			file_path = self.settings.lastpath.bin.select_save_file(self, title='Save Dialog BIN As', filetypes=[FileType.bin_dialog()])
			if not file_path:
				return
		elif not check_allow_overwrite_internal_file(file_path):
			return
		try:
			self.bin.save_file(file_path)
		except PyMSError as e:
			ErrorDialog(self, e)
			return
		self.status.set('Save Successful!')
		self.mark_edited(False)
		self.file = file_path
		self.update_title()

	def export(self, key=None):
		file = self.settings.lastpath.txt.select_save_file(self, key='export', title='Export TXT', filetypes=[FileType.txt()])
		if not file:
			return True
		try:
			self.bin.decompile_file(file)
			self.status.set('Export Successful!')
		except PyMSError as e:
			ErrorDialog(self, e)

	def close(self, key=None):
		if not self.unsaved():
			self.clear()
			self.status.set('Load or create a Dialog BIN.')
			self.mark_edited(False)
			self.scr_enabled.set(False)
			self.action_states()

	def register(self, e=None):
		try:
			register_registry('PyBIN', 'bin', 'Dialog')
		except PyMSError as e:
			ErrorDialog(self, e)

	def help(self, e=None):
		HelpDialog(self, self.settings, 'Help/Programs/PyBIN.md')

	def about(self, key=None):
		AboutDialog(self, 'PyBIN', LONG_VERSION, [
			('FaRTy1billion','File Specs and BinEdit2')
		])

	def load_settings(self):
		self.show_preview_settings.set(self.settings.preview.get('show_settings',True))
		self.show_images.set(self.settings.preview.get('show_images',True))
		self.show_text.set(self.settings.preview.get('show_text',True))
		self.show_smks.set(self.settings.preview.get('show_smks',True))
		self.show_hidden.set(self.settings.preview.get('show_hidden',True))
		self.show_dialog.set(self.settings.preview.get('show_dialog',False))
		self.show_animated.set(self.settings.preview.get('show_animated',False))
		self.show_hover_smks.set(self.settings.preview.get('show_hover_smks',False))
		self.show_background.set(self.settings.preview.get('show_background',False))
		self.show_theme_index.set(self.settings.preview.get('theme_id',-1) + 1)
		self.show_bounds_widget.set(self.settings.preview.get('show_bounds_widget',True))
		self.show_bounds_group.set(self.settings.preview.get('show_bounds_group',True))
		self.show_bounds_text.set(self.settings.preview.get('show_bounds_text',True))
		self.show_bounds_responsive.set(self.settings.preview.get('show_bounds_responsive',True))

	def save_settings(self):
		self.settings.preview.show_settings = self.show_preview_settings.get()
		self.settings.preview.show_images = self.show_images.get()
		self.settings.preview.show_text = self.show_text.get()
		self.settings.preview.show_smks = self.show_smks.get()
		self.settings.preview.show_hidden = self.show_hidden.get()
		self.settings.preview.show_dialog = self.show_dialog.get()
		self.settings.preview.show_animated = self.show_animated.get()
		self.settings.preview.show_hover_smks = self.show_hover_smks.get()
		self.settings.preview.show_background = self.show_background.get()
		self.settings.preview.theme_id = self.show_theme_index.get()-1
		self.settings.preview.show_bounds_widget = self.show_bounds_widget.get()
		self.settings.preview.show_bounds_group = self.show_bounds_group.get()
		self.settings.preview.show_bounds_text = self.show_bounds_text.get()
		self.settings.preview.show_bounds_responsive = self.show_bounds_responsive.get()

	def exit(self, e=None):
		if not self.unsaved():
			self.settings.windows.save_window_size('main', self)
			self.save_settings()
			self.settings.save()
			self.stop_tick()
			self.destroy()
