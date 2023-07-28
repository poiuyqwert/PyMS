
from __future__ import annotations

from .Delegates import MainDelegate, NodeDelegate
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
from ..Utilities import Assets
from ..Utilities.MPQHandler import MPQHandler
from ..Utilities.UpdateDialog import UpdateDialog
from ..Utilities.InternalErrorDialog import InternalErrorDialog
from ..Utilities.PyMSError import PyMSError
from ..Utilities.SettingsDialog import SettingsDialog
from ..Utilities.ErrorDialog import ErrorDialog
from ..Utilities.AboutDialog import AboutDialog
from ..Utilities.HelpDialog import HelpDialog
from ..Utilities.fileutils import check_allow_overwrite_internal_file
from ..Utilities.CheckSaved import CheckSaved

import time
from enum import Enum

from typing import Callable, cast

LONG_VERSION = 'v%s' % Assets.version('PyBIN')

FRAME_DELAY = 67

class MouseEvent(Enum):
	down = 0
	move = 1
	up = 2

class EditEvent(Enum):
	none = 0
	move = 1
	resize_left = 2
	resize_top = 3
	resize_right = 4
	resize_bottom = 5

	@staticmethod
	def of(x1: int, y1: int, x2: int, y2: int, mouseX: int, mouseY: int, resizable: bool = True) -> list[EditEvent]:
		event: list[EditEvent] = []
		nx1 = (x1 if x1 < x2 else x2)
		ny1 = (y1 if y1 < y2 else y2)
		nx2 = (x2 if x2 > x1 else x1)
		ny2 = (y2 if y2 > y1 else y1)
		d = 2 * resizable
		if nx1-d <= mouseX <= nx2+d and ny1-d <= mouseY <= ny2+d:
			event.append(EditEvent.move)
			if resizable:
				dist_left = abs(x1 - mouseX)
				dist_right = abs(x2 - mouseX)
				if dist_left < dist_right and dist_left <= d:
					event = [EditEvent.resize_left,EditEvent.none]
				elif dist_right < dist_left and dist_right <= d:
					event = [EditEvent.resize_right,EditEvent.none]
				dist_top = abs(y1 - mouseY)
				dist_bot = abs(y2 - mouseY)
				if dist_top < dist_bot and dist_top <= d:
					if len(event) == 1:
						event = [EditEvent.none,EditEvent.resize_top]
					else:
						event[1] = EditEvent.resize_top
				elif dist_bot < dist_top and dist_bot <= d:
					if len(event) == 1:
						event = [EditEvent.none,EditEvent.resize_bottom]
					else:
						event[1] = EditEvent.resize_bottom
		return event

class ClickModifier(Enum):
	none = 0
	shift = 1
	ctrl = 2

class PyBIN(MainWindow, MainDelegate, NodeDelegate):
	def __init__(self, guifile: str | None = None) -> None:

		#Window
		MainWindow.__init__(self)
		self.set_icon('PyBIN')
		self.protocol('WM_DELETE_WINDOW', self.exit)
		ga.set_application('PyBIN', Assets.version('PyBIN'))
		ga.track(GAScreen('PyBIN'))
		setup_trace('PyBIN', self)

		self.settings = Settings('PyBIN', '1')
		Theme.load_theme(self.settings.get('theme'), self)

		self.bin: DialogBIN.DialogBIN | None = None
		self.file: str | None = None
		self.edited = False
		self.dialog: WidgetNode | None = None
		self.widget_map: dict[str, WidgetNode] = {}

		self.update_title()

		self.tfont: PCX.PCX | None = None
		self.dlggrp: GRP.GRP | None = None
		self.tilegrp: GRP.GRP | None = None
		self.dialog_assets: dict[int, PILImage.Image] = {}
		self.dialog_frames: dict[int, PILImage.Image] = {}

		self.selected_node: WidgetNode | None = None

		self.old_cursor: str | None = None
		self.edit_node: WidgetNode | None = None
		self.current_event: list[EditEvent] = []
		self.mouse_offset = [0,0]
		self.event_moved = False

		self.background: PCX.PCX | None = None
		self.background_image: Image | None = None

		self.item_background: Canvas.Item | None = None # type: ignore[name-defined]
		self.item_selection_box: Canvas.Item | None = None # type: ignore[name-defined]

		#Toolbar
		self.toolbar = Toolbar(self)
		self.toolbar.add_button(Assets.get_image('new'), self.new, 'New', Ctrl.n)
		self.toolbar.add_gap()
		self.toolbar.add_button(Assets.get_image('open'), self.open, 'Open', Ctrl.o)
		self.toolbar.add_button(Assets.get_image('import'), self.iimport, 'Import from TXT', Ctrl.i)
		self.toolbar.add_gap()
		def save() -> None:
			self.save()
		self.toolbar.add_button(Assets.get_image('save'), save, 'Save', Ctrl.s, enabled=False, tags='file_open')
		def save_as() -> None:
			self.saveas()
		self.toolbar.add_button(Assets.get_image('saveas'), save_as, 'Save As', Ctrl.Alt.a, enabled=False, tags='file_open')
		self.toolbar.add_button(Assets.get_image('export'), self.export, 'Export to TXT', Ctrl.e, enabled=False, tags='file_open')
		self.toolbar.add_gap()
		self.toolbar.add_button(Assets.get_image('close'), self.close, 'Close', Ctrl.w, enabled=False, tags='file_open')
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('asc3topyai'), self.mpqsettings, 'Manage Settings', Ctrl.m)
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('register'), self.register_registry, 'Set as default *.bin editor (Windows Only)', enabled=WIN_REG_AVAILABLE)
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

		self.last_tick: int | None = None
		self.tick_alarm: str | None = None

		self.type_menu = Menu(self, tearoff=0)
		type_fields = (
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
		def add_new_node_callback(node_type: int) -> Callable[[], None]:
			def add_new_node() -> None:
				self.add_new_node(node_type)
			return add_new_node
		for info in type_fields:
			if info:
				self.type_menu.add_command(label=info[0], command=add_new_node_callback(info[1]))
			else:
				self.type_menu.add_separator()

		self.scr_enabled = BooleanVar()

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
		self.widgetTree.bind(Mouse.Click_Left(), self.list_select)
		self.widgetTree.bind(Mouse.Drag_Left(), self.list_drag)
		self.widgetTree.bind(ButtonRelease.Click_Left(), self.list_drop)
		self.widgetTree.bind(Double.Click_Left(), self.list_double_click)

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
		preview_fields = (
			('Images','show_images',self.show_images),
			('Text','show_text',self.show_text),
			('SMKs','show_smks',self.show_smks),
			('Hidden','show_hidden',self.show_hidden),
			('Dialog','show_dialog',self.show_dialog)
		)
		def toggle_setting_callback(setting_name: str, variable: BooleanVar) -> Callable[[], None]:
			def toggle_setting() -> None:
				self.toggle_setting(setting_name, variable)
			return toggle_setting
		for i,(name,setting_name,variable) in enumerate(preview_fields):
			check = Checkbutton(widgetsframe, text=name, variable=variable, command=toggle_setting_callback(setting_name,variable))
			check.grid(row=i // 2, column=i % 2, sticky=W)
		widgetsframe.grid_columnconfigure(0, weight=1)
		widgetsframe.grid_columnconfigure(1, weight=1)
		widgetsframe.grid(row=0, column=0, sticky=NSEW, padx=5)
		smkframe = LabelFrame(self.preview_settings_frame, text='SMKs')
		smk_fields = (
			('Animated','show_animated',self.show_animated),
			('Hovers','show_hover_smks',self.show_hover_smks)
		)
		for i,(name,setting_name,variable) in enumerate(smk_fields):
			check = Checkbutton(smkframe, text=name, variable=variable, command=toggle_setting_callback(setting_name,variable))
			check.grid(row=i // 2, column=i % 2, sticky=W)
		smkframe.grid_columnconfigure(0, weight=1)
		smkframe.grid_columnconfigure(1, weight=1)
		smkframe.grid(row=1, column=0, sticky=NSEW, padx=5)
		boundsframe = LabelFrame(self.preview_settings_frame, text='Bounds')
		bounds_fields = (
			('Widgets','show_bounds_widget',self.show_bounds_widget),
			('Groups','show_bounds_group',self.show_bounds_group),
			('Text','show_bounds_text',self.show_bounds_text),
			('Responsive','show_bounds_responsive',self.show_bounds_responsive)
		)
		for i,(name,setting_name,variable) in enumerate(bounds_fields):
			check = Checkbutton(boundsframe, text=name, variable=variable, command=toggle_setting_callback(setting_name,variable))
			check.grid(row=i // 2, column=i % 2, sticky=W)
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
		self.widgetCanvas = Canvas(bdframe, background='#000000', highlightthickness=0, width=640, height=480, theme_tag='preview') # type: ignore[call-arg]
		self.widgetCanvas.pack()
		self.widgetCanvas.focus_set()
		bdframe.pack(side=TOP)
		rightframe.grid(row=0, column=1, padx=(2,5), pady=2, sticky=NSEW)
		frame.grid_columnconfigure(1, weight=0, minsize=640)
		frame.grid_rowconfigure(0, weight=1, minsize=480)
		frame.pack(fill=BOTH, expand=1)
		self.widgetCanvas.bind(Mouse.Motion(), self.mouse_motion)
		self.widgetCanvas.bind(Cursor.Leave(), lambda e: self.edit_status.set(''))
		def canvas_double_click_callback(click_modifier: ClickModifier) -> Callable[[Event], None]:
			def canvas_double_click(event: Event) -> None:
				self.canvas_double_click(event, click_modifier)
			return canvas_double_click
		self.widgetCanvas.bind(Double.Click_Left(), canvas_double_click_callback(ClickModifier.none))
		self.widgetCanvas.bind(Ctrl.Double.Click_Left(), canvas_double_click_callback(ClickModifier.ctrl))

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
		for base_event,etype in mouse_events:
			for event_mod,mod in mouse_modifiers:
				event = base_event
				if event_mod:
					event = event_mod + event
				self.widgetCanvas.bind(event(), mouse_event_callback(etype,mod))

		self.bind(Key.Return(), self.list_double_click)

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
		geometry = Geometry.of(self)
		self.minsize(geometry.size.width, geometry.size.height)
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

	def tick(self, start: bool = False) -> None:
		if not self.tick_alarm or not start:
			return
		if self.bin:
			now = int(time.time() * 1000)
			if self.last_tick is None:
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

	def stop_tick(self) -> None:
		if self.tick_alarm is None:
			return
		cancel = self.tick_alarm
		self.tick_alarm = None
		self.after_cancel(cancel)

	def scr_toggled(self) -> None:
		assert self.bin is not None
		self.bin.remastered = self.scr_enabled.get()

	def toggle_preview_settings(self) -> None:
		show = not self.show_preview_settings.get()
		self.show_preview_settings.set(show)
		if show:
			self.widgets_toolbar.update_icon('settings_toggle', Assets.get_image('arrow'))
			self.preview_settings_frame.grid(sticky=EW)
		else:
			self.widgets_toolbar.update_icon('settings_toggle', Assets.get_image('arrowup'))
			self.preview_settings_frame.grid_remove()

	def add_node(self) -> None:
		self.type_menu.post(*self.winfo_pointerxy())

	def add_new_node(self, ctrl_type: int) -> None:
		if not self.bin:
			return
		parent = self.dialog
		index = 0
		if self.selected_node:
			if self.selected_node.children is not None:
				parent = self.selected_node
			else:
				parent = self.selected_node.parent
				if parent and parent.children is not None:
					index = parent.children.index(self.selected_node)
		if not parent:
			return
		node = None
		if ctrl_type == -1:
			node = WidgetNode(self)
		else:
			x1,y1,x2,y2 = parent.bounding_box()
			widget = DialogBIN.BINWidget(ctrl_type)
			widget.width = 201
			widget.height = 101
			widget.x1 = x1 + (x2-x1-(widget.width-1)) // 2
			widget.y1 = y1 + (y2-y1-(widget.height-1)) // 2
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
		self.refresh_nodes()
		self.refresh_preview()
		self.select_node(node)
		self.mark_edited()

	def remove_node(self) -> None:
		if not self.bin or not self.selected_node:
			return
		self.selected_node.remove_display()
		if self.selected_node.widget:
			self.bin.widgets.remove(self.selected_node.widget)
			if self.selected_node.widget.type >= DialogBIN.BINWidget.TYPE_HTML and not self.bin.remastered:
				self.scr_enabled.set(False)
			self.action_states()
		self.selected_node.remove_from_parent()
		self.selected_node = None
		self.update_selection_box()
		self.refresh_nodes()
		self.mark_edited()

	def move_node(self, delta: int) -> None:
		if not self.selected_node or not self.selected_node.parent or self.selected_node.parent.children is None:
			return
		index = self.selected_node.parent.children.index(self.selected_node)
		dest = index + delta
		if 0 <= dest <= len(self.selected_node.parent.children):
			self.selected_node.parent.children.insert(dest, self.selected_node)
			del self.selected_node.parent.children[index + (dest < index)]
			self.refresh_nodes()
			self.action_states()
			self.update_zorder()
			self.mark_edited()

	def update_background(self) -> None:
		if self.bin and self.show_theme_index.get() and not self.background:
			try:
				path = 'MPQ:' + DialogBIN.THEME_ASSETS_INFO[self.show_theme_index.get()-1]['path'] + 'backgnd.pcx'
				background = PCX.PCX()
				background.load_file(self.mpqhandler.load_file(path))
			except:
				InternalErrorDialog.capture(self, 'PyBIN')
			else:
				self.background = background
		elif not self.show_theme_index.get() and self.background:
			self.background = None
		delete = True
		if self.bin and self.show_background.get() and self.background:
			if not self.background_image:
				self.background_image = cast(Image, GRP.frame_to_photo(self.background.palette, self.background, -1, size=False))
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

	def load_dlggrp(self) -> None:
		dlggrp = None
		check = ['MPQ:glue\\palmm\\dlg.grp']
		if self.show_theme_index.get():
			path = 'MPQ:' + DialogBIN.THEME_ASSETS_INFO[self.show_theme_index.get()-1]['path'] + 'dlg.grp'
			check.insert(0, path)
		for path in check:
			try:
				dlggrp = GRP.GRP()
				dlggrp.load_file(self.mpqhandler.load_file(path), uncompressed=True)
			except:
				InternalErrorDialog.capture(self, 'PyBIN')
			else:
				break
		self.dlggrp = dlggrp
		self.dialog_assets = {}
		# if self.bin:
		# 	for widget in self.flattened_nodes():
		# 		pass
			# self.refresh_preview()

	def load_tilegrp(self) -> None:
		tilegrp = None
		check = ['MPQ:glue\\palmm\\tile.grp']
		if self.show_theme_index.get():
			path = 'MPQ:' + DialogBIN.THEME_ASSETS_INFO[self.show_theme_index.get()-1]['path'] + 'tile.grp'
			check.insert(0, path)
		for path in check:
			try:
				tilegrp = GRP.GRP()
				tilegrp.load_file(self.mpqhandler.load_file(path))
			except:
				InternalErrorDialog.capture(self, 'PyBIN')
			else:
				break
		self.tilegrp = tilegrp
		self.dialog_frames = {}
		# if self.bin:
		# 	for widget in self.flattened_nodes():
		# 		pass
			# self.refresh_preview()

	def load_tfont(self) -> None:
		tfont = None
		check = ['MPQ:glue\\title\\tfont.pcx']
		if self.show_theme_index.get():
			path = 'MPQ:' + DialogBIN.THEME_ASSETS_INFO[self.show_theme_index.get()-1]['path'] + 'tfont.pcx'
			check.insert(0, path)
		for path in check:
			try:
				tfont = PCX.PCX()
				tfont.load_file(self.mpqhandler.load_file(path))
			except:
				tfont = None
			else:
				break
		self.tfont = tfont
		if self.bin:
			for widget in self.flattened_nodes():
				widget.string = None
				widget.item_string_images = None
			# self.refresh_preview()

	def change_theme(self, n: int) -> None:
		index = self.show_theme_index.get()-1
		if index != self.settings.preview.get('theme_id'):
			self.settings.preview.theme_id = index
			self.background = None
			self.background_image = None
			self.update_background()
			self.load_dlggrp()
			self.load_tilegrp()
			self.load_tfont()
			self.refresh_preview()

	def open_files(self) -> (Exception | None):
		self.mpqhandler.open_mpqs()
		err = None
		try:
			tfontgam = PCX.PCX()
			font10 = FNT.FNT()
			font14 = FNT.FNT()
			font16 = FNT.FNT()
			font16x = FNT.FNT()

			tfontgam.load_file(self.mpqhandler.load_file(self.settings.settings.files.get('tfontgam', 'MPQ:game\\tfontgam.pcx')))
			path = self.settings.settings.files.get('font10', 'MPQ:font\\font10.fnt')
			try:
				font10.load_file(self.mpqhandler.load_file(path, False))
			except:
				font10.load_file(self.mpqhandler.load_file(path, True))
			path = self.settings.settings.files.get('font14', 'MPQ:font\\font14.fnt')
			try:
				font14.load_file(self.mpqhandler.load_file(path, False))
			except:
				font14.load_file(self.mpqhandler.load_file(path, True))
			path = self.settings.settings.files.get('font16', 'MPQ:font\\font16.fnt')
			try:
				font16.load_file(self.mpqhandler.load_file(path, False))
			except:
				font16.load_file(self.mpqhandler.load_file(path, True))
			path = self.settings.settings.files.get('font16x', 'MPQ:font\\font16x.fnt')
			try:
				font16x.load_file(self.mpqhandler.load_file(path, False))
			except:
				font16x.load_file(self.mpqhandler.load_file(path, True))
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

	def mpqsettings(self, key: Event | None = None, err: Exception | None = None) -> None:
		data = [
			('Preview Settings',[
				('tfontgam.pcx','The special palette which holds text colors.','tfontgam','PCX'),
				('font10.fnt','Size 10 font','font10','FNT'),
				('font14.fnt','Size 14 font','font14','FNT'),
				('font16.fnt','Size 16 font','font16','FNT'),
				('font16x.fnt','Size 16x font','font16x','FNT'),
			]),
			('Theme',)
		]
		SettingsDialog(self, data, (550,430), err, settings=self.settings, mpqhandler=self.mpqhandler)

	def check_saved(self) -> CheckSaved:
		if not self.bin or not self.edited:
			return CheckSaved.saved
		file = self.file
		if not file:
			file = 'Unnamed.bin'
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
		return not not self.bin

	def has_selected_node(self) -> bool:
		return self.selected_node is not None

	def action_states(self) -> None:
		is_file_open = self.is_file_open()
		self.toolbar.tag_enabled('file_open', is_file_open)

		selection_is_dialog = (self.selected_node and self.selected_node.widget and self.selected_node.widget.type == DialogBIN.BINWidget.TYPE_DIALOG)
		can_move_up = False
		can_move_down = False
		if self.selected_node and not not self.selected_node.parent and not self.selected_node.parent.children is None:
			index = self.selected_node.parent.children.index(self.selected_node)
			can_move_up = (index > 0)
			can_move_down = (index < len(self.selected_node.parent.children)-1)
		self.widgets_toolbar.tag_enabled('file_open', is_file_open)
		self.widgets_toolbar.tag_enabled('node_selected', self.has_selected_node())
		self.widgets_toolbar.tag_enabled('dialog_not_selected', not selection_is_dialog)
		self.widgets_toolbar.tag_enabled('can_move_up', can_move_up)
		self.widgets_toolbar.tag_enabled('can_move_down', can_move_down)

		# self.scr_check['state'] = NORMAL if is_file_open and not self.bin.remastered_required() else DISABLED

	def setup_nodes(self) -> None:
		if not self.bin:
			return
		for widget in self.bin.widgets:
			node = WidgetNode(self, widget)
			if self.dialog is None:
				self.dialog = node
			else:
				self.dialog.add_child(node)

	def flattened_nodes(self, include_groups: bool = True) -> list[WidgetNode]:
		nodes: list[WidgetNode] = []
		def add_node(node: WidgetNode) -> None:
			if node.widget or include_groups:
				nodes.append(node)
			if node.children is not None:
				for child in node.children:
					add_node(child)
		if self.dialog:
			add_node(self.dialog)
		return nodes

	def update_zorder(self) -> None:
		for node in self.flattened_nodes():
			node.lift()
		if self.item_selection_box:
			self.widgetCanvas.lift(self.item_selection_box)

	def toggle_setting(self, setting_name: str, variable: BooleanVar) -> None:
		self.settings.preview[setting_name] = variable.get()
		self.refresh_preview()

	def update_selection_box(self) -> None:
		if self.selected_node:
			x1,y1,x2,y2 = self.selected_node.bounding_box()
			if self.item_selection_box:
				self.widgetCanvas.coords(self.item_selection_box, x1,y1, x2,y2)
			else:
				self.item_selection_box = self.widgetCanvas.create_rectangle(x1,y1, x2,y2, width=1, outline='#ff6961')
		elif self.item_selection_box:
			self.widgetCanvas.delete(self.item_selection_box)
			self.item_selection_box = None

	def update_list_selection(self) -> None:
		if self.selected_node and self.selected_node.index:
			self.widgetTree.select(self.selected_node.index)
			self.widgetTree.see(self.selected_node.index)
		else:
			self.widgetTree.select(None)

	def edit_node_settings(self, node: WidgetNode | None = None) -> None:
		if node is None:
			node = self.selected_node
		if node and node.widget:
			WidgetSettings(self, node, self)

	def canvas_double_click(self, e: Event, m: ClickModifier):
		if not self.dialog:
			return
		prefer_selection = (m == ClickModifier.ctrl)
		def check_clicked(node: WidgetNode, x: int, y: int) -> (WidgetNode | None):
			found = None
			x1,y1,x2,y2 = node.bounding_box()
			if node.widget:
				x1 = node.widget.x1
				y1 = node.widget.y1
				x2 = node.widget.x2
				y2 = node.widget.y2
			event = EditEvent.of(x1,y1,x2,y2, x,y, False)
			if event:
				found = node
				if node.children is not None and (not prefer_selection or node != self.selected_node):
					for child in reversed(node.children):
						found_child = check_clicked(child, x,y)
						if found_child is not None:
							found = found_child
			return found
		node = check_clicked(self.dialog, e.x,e.y)
		if node:
			self.edit_node_settings(node)

	def list_double_click(self, event: Event) -> None:
		selected = self.widgetTree.cur_selection()
		if not selected or selected[0] < 0:
			return
		list_index = self.widgetTree.index(selected[0])
		if not list_index:
			return
		node = self.widget_map.get(list_index)
		if node:
			self.edit_node_settings(node)

	def select_node(self, node: WidgetNode | None) -> None:
		self.selected_node = node
		self.update_selection_box()
		self.update_list_selection()
		self.action_states()

	def list_select(self, event: Event) -> None:
		selected = self.widgetTree.cur_selection()
		if not selected or selected[0] < 0:
			return
		list_index = self.widgetTree.index(selected[0])
		if not list_index:
			return
		self.selected_node = self.widget_map[list_index]
		self.update_selection_box()
		self.action_states()

	def list_drag(self, event: Event) -> None:
		# todo: Not started on node?
		if not self.selected_node:
			return
		if self.selected_node.widget and self.selected_node.widget.type == DialogBIN.BINWidget.TYPE_DIALOG:
			return
		index = self.widgetTree.index("@%d,%d" % (event.x, event.y))
		self.widgetTree.highlight(index)

	def list_drop(self, event: Event) -> None:
		# todo: Not started on node?
		if not self.selected_node:
			return
		if self.selected_node.widget and self.selected_node.widget.type == DialogBIN.BINWidget.TYPE_DIALOG:
			return
		self.widgetTree.highlight(None)
		index,below = self.widgetTree.lookup_coords(event.x, event.y)
		if index is None or index == self.selected_node.index:
			return
		highlight = self.widget_map[index]
		if self.selected_node.children is not None:
			check = highlight.parent
			while check:
				if check == self.selected_node:
					return
				check = check.parent
		if highlight.children is not None:
			highlight.add_child(self.selected_node)
		elif highlight.parent and highlight.parent.children is not None:
			highlight.parent.add_child(self.selected_node, highlight.parent.children.index(highlight) + below)
		self.refresh_nodes()
		self.refresh_preview()
		self.mark_edited()

	def edit_event(self, x: int, y: int, node: WidgetNode | None = None, prefer_selection: bool = False) -> tuple[WidgetNode | None, list[EditEvent]]:
		if node is None:
			node = self.dialog
		if node is None:
			return (None, [])
		found_node: WidgetNode | None = None
		found_event: list[EditEvent] = []
		x1,y1,x2,y2 = node.bounding_box()
		if node.widget:
			x1 = node.widget.x1
			y1 = node.widget.y1
			x2 = node.widget.x2
			y2 = node.widget.y2
		event = EditEvent.of(x1,y1,x2,y2, x,y, node.widget is not None)
		if event:
			found_node = node
			found_event = event
		if node.children is not None and (not prefer_selection or node != self.selected_node):
			for child in reversed(node.children):
				found_child = self.edit_event(x,y, node=child, prefer_selection=prefer_selection)
				if found_child[0] is not None:
					found_node,found_event = found_child
					break
		return (found_node, found_event)

	def mouse_motion(self, event: Event) -> None:
		if not self.bin:
			return
		if self.old_cursor is None:
			self.old_cursor = self.widgetCanvas.cget('cursor')
		cursor = [self.old_cursor]
		node,mouse_event = self.edit_event(event.x,event.y)
		if node is not None:
			if node.widget:
				if node.widget.x1 > node.widget.x2:
					if EditEvent.resize_left in mouse_event:
						mouse_event[mouse_event.index(EditEvent.resize_left)] = EditEvent.resize_right
					elif EditEvent.resize_right in mouse_event:
						mouse_event[mouse_event.index(EditEvent.resize_right)] = EditEvent.resize_left
				if node.widget.y1 > node.widget.y2:
					if EditEvent.resize_top in mouse_event:
						mouse_event[mouse_event.index(EditEvent.resize_top)] = EditEvent.resize_bottom
					elif EditEvent.resize_bottom in mouse_event:
						mouse_event[mouse_event.index(EditEvent.resize_bottom)] = EditEvent.resize_top
			if mouse_event[0] == EditEvent.move:
				cursor.extend(['crosshair','fleur','size'])
			elif mouse_event[0] == EditEvent.resize_left:
				cursor.extend(['left_side','size_we','resizeleft','resizeleftright'])
			elif mouse_event[0] == EditEvent.resize_right:
				cursor.extend(['right_side','size_we','resizeright','resizeleftright'])
			if len(mouse_event) == 2:
				if mouse_event[1] == EditEvent.resize_top:
					cursor.extend(['top_side','size_ns','resizeup','resizeupdown'])
				elif mouse_event[1] == EditEvent.resize_bottom:
					cursor.extend(['bottom_side','size_ns','resizedown','resizeupdown'])
				if mouse_event[0] == EditEvent.resize_left and mouse_event[1] == EditEvent.resize_top:
					cursor.extend(['top_left_corner','size_nw_se','resizetopleft'])
				elif mouse_event[0] == EditEvent.resize_right and mouse_event[1] == EditEvent.resize_top:
					cursor.extend(['top_right_corner','size_ne_sw','resizetopright'])
				elif mouse_event[0] == EditEvent.resize_left and mouse_event[1] == EditEvent.resize_bottom:
					cursor.extend(['bottom_left_corner','size_ne_sw','resizebottomleft'])
				elif mouse_event[0] == EditEvent.resize_right and mouse_event[1] == EditEvent.resize_bottom:
					cursor.extend(['bottom_right_corner','size_nw_se','resizebottomright'])
			if node.widget:
				self.edit_status.set('Edit Widget: ' + node.get_name())
			else:
				self.edit_status.set('Edit ' + node.get_name())
		else:
			self.edit_status.set('')
		self.widgetCanvas.apply_cursor(cursor) # type: ignore[attr-defined]

	def mouse_event(self, event: Event, mouse_event: MouseEvent, modifier: ClickModifier) -> None:
		RESTRICT_TO_WINDOW = True
		if self.bin:
			x = event.x
			y = event.y
			if mouse_event == MouseEvent.down:
				node,edit_event = self.edit_event(event.x,event.y, prefer_selection=(modifier == ClickModifier.ctrl))
				self.select_node(node)
				if node:
					self.edit_node = node
					self.current_event = edit_event
					self.event_moved = False
					if edit_event[0] == EditEvent.move:
						x1,y1,x2,y2 = node.bounding_box()
						self.mouse_offset = [x1 - x, y1 - y]
			if self.edit_node:
				if mouse_event == MouseEvent.move:
					self.event_moved = True
				x1,y1,x2,y2 = self.edit_node.bounding_box()
				if self.current_event[0] == EditEvent.move:
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
					def offset_node(node: WidgetNode, delta_x: int, delta_y) -> None:
						if node.widget:
							node.widget.x1 += delta_x
							node.widget.y1 += delta_y
							node.widget.x2 += delta_x
							node.widget.y2 += delta_y
						if node.children is not None:
							for child in node.children:
								offset_node(child, delta_x,delta_y)
						node.update_display()
						if node == self.selected_node:
							self.update_selection_box()
					offset_node(self.edit_node, dx,dy)
					if dx or dy:
						self.mark_edited()
				elif self.event_moved:
					assert self.edit_node.widget is not None
					rdx2,rdy2 = 0,0
					if EditEvent.resize_left in self.current_event:
						rdx2 = self.edit_node.widget.x1 - x
						self.edit_node.widget.x1 = x
					elif EditEvent.resize_right in self.current_event:
						rdx2 = x - self.edit_node.widget.x2
						self.edit_node.widget.x2 = x
					if EditEvent.resize_top in self.current_event:
						rdy2 = self.edit_node.widget.y1 - y
						self.edit_node.widget.y1 = y
					elif EditEvent.resize_bottom in self.current_event:
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
				while check.parent and check.parent.widget is None:
					check.parent.update_display()
					check = check.parent
				if mouse_event == MouseEvent.up:
					self.edit_node = None
					self.current_event = []
					self.mouse_offset = [0, 0]

	def clear(self) -> None:
		self.bin = None
		self.file = None
		self.edited = False
		self.dialog = None
		self.widget_map.clear()

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

	def update_title(self) -> None:
		file_path = self.file
		if not file_path and self.is_file_open():
			file_path = 'Untitled.bin'
		if not file_path:
			self.title('PyBIN %s' % LONG_VERSION)
		else:
			self.title('PyBIN %s (%s)' % (LONG_VERSION, file_path))

	def new(self, key: Event | None = None) -> None:
		if self.check_saved() == CheckSaved.cancelled:
			return
		if not self.tfont:
			self.load_tfont()
		if not self.dlggrp:
			self.load_dlggrp()
		if not self.tilegrp:
			self.load_tilegrp()
		self.clear()
		self.bin = DialogBIN.DialogBIN()
		self.setup_nodes()
		self.refresh_nodes()
		self.refresh_preview()
		self.file = None
		self.status.set('Editing new Dialog.')
		self.update_title()
		self.mark_edited(False)
		self.action_states()
		self.tick(True)

	def open(self, key: Event | None = None, file: str | None = None) -> None:
		if self.check_saved() == CheckSaved.cancelled:
			return
		if file is None:
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
		self.refresh_nodes()
		self.refresh_preview()
		self.file = file
		self.update_title()
		self.scr_enabled.set(self.bin.remastered)
		self.status.set('Load Successful!')
		self.mark_edited(False)
		self.select_node(self.dialog)
		self.action_states()
		self.tick(True)

	def iimport(self, key: Event | None = None) -> None:
		if self.check_saved() == CheckSaved.cancelled:
			return
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
		self.refresh_nodes()
		self.refresh_preview()
		self.file = file
		self.update_title()
		self.scr_enabled.set(self.bin.remastered)
		self.status.set('Import Successful!')
		self.mark_edited(False)
		self.action_states()
		self.tick(True)

	def save(self, key: Event | None = None) -> CheckSaved:
		return self.saveas(file_path=self.file)

	def saveas(self, key: Event | None = None, file_path: str | None = None) -> CheckSaved:
		if not self.bin:
			return CheckSaved.saved
		if not file_path:
			file_path = self.settings.lastpath.bin.select_save_file(self, title='Save Dialog BIN As', filetypes=[FileType.bin_dialog()])
			if not file_path:
				return CheckSaved.cancelled
		elif not check_allow_overwrite_internal_file(file_path):
			return CheckSaved.cancelled
		try:
			self.bin.save_file(file_path)
		except PyMSError as e:
			ErrorDialog(self, e)
			return CheckSaved.cancelled
		self.status.set('Save Successful!')
		self.mark_edited(False)
		self.file = file_path
		self.update_title()
		return CheckSaved.saved

	def export(self, key: Event | None = None) -> None:
		if not self.bin:
			return
		file = self.settings.lastpath.txt.select_save_file(self, key='export', title='Export TXT', filetypes=[FileType.txt()])
		if not file:
			return
		try:
			self.bin.decompile_file(file)
			self.status.set('Export Successful!')
		except PyMSError as e:
			ErrorDialog(self, e)

	def close(self, key: Event | None = None) -> None:
		if self.check_saved() == CheckSaved.cancelled:
			return
		self.clear()
		self.status.set('Load or create a Dialog BIN.')
		self.mark_edited(False)
		self.scr_enabled.set(False)
		self.action_states()

	def register_registry(self, e: Event | None = None) -> None:
		try:
			register_registry('PyBIN', 'bin', 'Dialog')
		except PyMSError as e:
			ErrorDialog(self, e)

	def help(self, e: Event | None = None) -> None:
		HelpDialog(self, self.settings, 'Help/Programs/PyBIN.md')

	def about(self, key: Event | None = None) -> None:
		AboutDialog(self, 'PyBIN', LONG_VERSION, [
			('FaRTy1billion','File Specs and BinEdit2')
		])

	def load_settings(self) -> None:
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

	def save_settings(self) -> None:
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

	def exit(self, e: Event | None = None) -> None:
		if self.check_saved() == CheckSaved.cancelled:
			return
		self.settings.windows.save_window_size('main', self)
		self.save_settings()
		self.settings.save()
		self.stop_tick()
		self.destroy()

	# MainDelegate
	def get_bin(self) -> (DialogBIN.DialogBIN | None):
		return self.bin

	def get_settings(self) -> Settings:
		return self.settings

	def get_mpqhandler(self) -> MPQHandler:
		return self.mpqhandler

	def get_scr_enabled(self) -> bool:
		return self.scr_enabled.get()

	def mark_edited(self, edited: bool = True) -> None:
		self.edited = edited
		self.editstatus['state'] = NORMAL if edited else DISABLED
		self.action_states()

	def refresh_preview(self) -> None:
		if not self.bin:
			return
		# self.widgetCanvas.delete(ALL)
		self.update_background()
		reorder = False
		for node in self.flattened_nodes():
			reorder = node.update_display() or reorder
		self.update_selection_box()
		if reorder:
			self.update_zorder()

	def refresh_smks(self) -> None:
		pass

	def refresh_nodes(self) -> None:
		self.widget_map = {}
		self.widgetTree.delete(ALL)
		if not self.dialog:
			return
		def list_node(at_index: str, node: WidgetNode) -> None:
			group = None
			if node.children is not None:
				group = True
			index = self.widgetTree.insert(at_index, node.get_name(), group)
			if not index:
				return
			node.index = index
			if node == self.selected_node:
				self.widgetTree.select(index)
				self.widgetTree.see(index)
			self.widget_map[index] = node
			if node.children is not None:
				for child in reversed(node.children):
					list_node(node.index + '.-1', child)
		list_node('-1', self.dialog)

	# NodeDelegate

	def get_dialog_asset(self, asset_id: int) -> (PILImage.Image | None):
		asset = None
		if self.dlggrp and self.background:
			if asset_id in self.dialog_assets:
				asset = self.dialog_assets[asset_id]
			else:
				asset = GRP.image_to_pil(self.dlggrp.images[asset_id], self.background.palette, image_bounds=self.dlggrp.images_bounds[asset_id])
				self.dialog_assets[asset_id] = asset
		return asset

	def get_dialog_frame(self, frame_id: int) -> (PILImage.Image | None):
		frame = None
		if self.tilegrp and self.background:
			if frame_id in self.dialog_frames:
				frame = self.dialog_frames[frame_id]
			else:
				frame = GRP.image_to_pil(self.tilegrp.images[frame_id], self.background.palette, image_bounds=self.tilegrp.images_bounds[frame_id])
				self.dialog_frames[frame_id] = frame
		return frame

	def get_show_hidden(self) -> bool:
		return self.show_hidden.get()

	def get_show_dialog(self) -> bool:
		return self.show_dialog.get()

	def get_show_smks(self) -> bool:
		return self.show_smks.get()

	def get_show_animated(self) -> bool:
		return self.show_animated.get()

	def get_show_images(self) -> bool:
		return self.show_images.get()

	def get_show_text(self) -> bool:
		return self.show_text.get()

	def get_show_bounds_widget(self) -> bool:
		return self.show_bounds_widget.get()

	def get_show_bounds_group(self) -> bool:
		return self.show_bounds_group.get()

	def get_show_bounds_text(self) -> bool:
		return self.show_bounds_text.get()

	def get_show_bounds_responsive(self) -> bool:
		return self.show_bounds_responsive.get()

	def get_font(self, flags: int) -> FNT.FNT:
		if flags & DialogBIN.BINWidget.FLAG_FONT_SIZE_10:
			return self.font10
		elif flags & DialogBIN.BINWidget.FLAG_FONT_SIZE_14:
			return self.font14
		elif flags & DialogBIN.BINWidget.FLAG_FONT_SIZE_16:
			return self.font16
		elif flags & DialogBIN.BINWidget.FLAG_FONT_SIZE_16x:
			return self.font16x
		else:
			return self.font10

	def get_tfontgam(self) -> PCX.PCX:
		return self.tfontgam

	def get_tfont(self) -> (PCX.PCX | None):
		return self.tfont

	def node_render_image_create(self, x: int, y: int, image: ImageTk.PhotoImage, anchor: Anchor) -> Canvas.Item: # type: ignore[name-defined]
		return self.widgetCanvas.create_image(x, y, image=image, anchor=anchor)

	def node_render_image_update(self, item: Canvas.Item, x: int, y: int, image: ImageTk.PhotoImage | None) -> None: # type: ignore[name-defined]
		if image:
			self.widgetCanvas.itemconfigure(item, image=image)
		self.widgetCanvas.coords(item, x, y)

	def node_render_rect_create(self, x1: int, y1: int, x2: int, y2: int, color: str) -> Canvas.Item: # type: ignore[name-defined]
		return self.widgetCanvas.create_rectangle(x1, y1, x2, y2, width=1, outline=color)

	def node_render_rect_update(self, item: Canvas.Item, x1: int, y1: int, x2: int, y2: int) -> None: # type: ignore[name-defined]
		self.widgetCanvas.coords(item, x1, y1, x2, y2)

	def node_render_lift(self, item: Canvas.Item) -> None: # type: ignore[name-defined]
		self.widgetCanvas.lift(item)

	def node_render_delete(self, item: Canvas.Item) -> None: # type: ignore[name-defined]
		self.widgetCanvas.delete(item)

	def capture_exception(self) -> None:
		InternalErrorDialog.capture(self, 'PyBIN')
