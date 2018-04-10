from Libs.utils import *
from Libs.setutils import *
from Libs.trace import setup_trace
from Libs.SpecialLists import TreeList
from Libs import DialogBIN, FNT, PCX, SMK, GRP
from Libs.analytics import *

from Tkinter import *
from PIL import Image as PILImage
try:
	from PIL import ImageTk
except:
	import ImageTk

from thread import start_new_thread
import optparse, os, webbrowser, sys, time

LONG_VERSION = 'v%s-DEV' % VERSIONS['PyBIN']
PYBIN_SETTINGS = Settings('PyBIN', '1')

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

class SMKSettings(PyMSDialog):
	def __init__(self, parent, smk, widget=None, window_pos=False):
		self.widget = (widget if widget else parent)
		self.smk = smk
		self.window_pos = window_pos

		self.filename = StringVar()
		self.overlay_smk = IntVar()
		self.overlay_x = IntegerVar(range=[0,65535])
		self.overlay_y = IntegerVar(range=[0,65535])

		self.flag_fadein = BooleanVar()
		self.flag_dark = BooleanVar()
		self.flag_repeat = BooleanVar()
		self.flag_hover = BooleanVar()
		self.flag_unk1 = BooleanVar()
		self.flag_unk2 = BooleanVar()
		self.flag_unk3 = BooleanVar()
		self.flag_unk4 = BooleanVar()

		PyMSDialog.__init__(self, parent, 'Edit SMK', center=False)

	def widgetize(self):
		textframe = Frame(self)
		Label(textframe, text='Filename:').pack(side=LEFT)
		Entry(textframe, textvariable=self.filename, font=couriernew).pack(side=LEFT, fill=X, expand=1)
		image = PhotoImage(file=os.path.join(BASE_DIR,'Images','find.gif'))
		button = Button(textframe, image=image, width=20, height=20, command=self.find_smk)
		button.image = image
		button.pack(side=LEFT)
		textframe.grid(row=0,column=0, padx=2,pady=2, sticky=NSEW)

		overlayframe = LabelFrame(self, text='Overlay SMK')
		smkframe = Frame(overlayframe)
		self.smks_dropdown = DropDown(smkframe, self.overlay_smk, ['None'], stay_right=True)
		self.smks_dropdown.pack(side=LEFT, fill=X, expand=1)
		image = PhotoImage(file=os.path.join(BASE_DIR,'Images','edit.gif'))
		button = Button(smkframe, image=image, width=20, height=20, command=self.edit_smk)
		button.image = image
		button.pack(side=LEFT)
		image = PhotoImage(file=os.path.join(BASE_DIR,'Images','add.gif'))
		button = Button(smkframe, image=image, width=20, height=20, command=self.add_smk)
		button.image = image
		button.pack(side=LEFT)
		smkframe.pack(side=TOP, fill=X, expand=1)
		offsetframe = Frame(overlayframe)
		Label(offsetframe, text='Offset X:').pack(side=LEFT)
		Entry(offsetframe, textvariable=self.overlay_x, font=couriernew, width=5).pack(side=LEFT)
		Label(offsetframe, text='Offset Y:').pack(side=LEFT)
		Entry(offsetframe, textvariable=self.overlay_y, font=couriernew, width=5).pack(side=LEFT)
		offsetframe.pack(side=TOP, fill=X, expand=1)
		overlayframe.grid(row=1,column=0, padx=5,pady=0, sticky=NSEW)

		flagsframe = LabelFrame(self, text='Flags')
		Checkbutton(flagsframe, text='Fade In', variable=self.flag_fadein).grid(row=0,column=0, sticky=W)
		Checkbutton(flagsframe, text='Dark', variable=self.flag_dark).grid(row=1,column=0, sticky=W)
		Checkbutton(flagsframe, text='Repeat Forever', variable=self.flag_repeat).grid(row=2,column=0, sticky=W)
		Checkbutton(flagsframe, text='Show on Hover', variable=self.flag_hover).grid(row=3,column=0, sticky=W)
		Checkbutton(flagsframe, text='4', variable=self.flag_unk1).grid(row=0,column=1, sticky=W)
		Checkbutton(flagsframe, text='5', variable=self.flag_unk2).grid(row=1,column=1, sticky=W)
		Checkbutton(flagsframe, text='6', variable=self.flag_unk3).grid(row=2,column=1, sticky=W)
		Checkbutton(flagsframe, text='7', variable=self.flag_unk4).grid(row=3,column=1, sticky=W)
		flagsframe.grid(row=0,column=1, rowspan=2, padx=2,pady=2, sticky=S)

		bottom = Frame(self)
		ok = Button(bottom, text='Ok', width=10, command=self.ok)
		ok.pack(side=LEFT, padx=1, pady=3)
		Button(bottom, text='Update Preview', width=15, command=self.update_preview).pack(side=RIGHT, padx=3, pady=3)
		bottom.grid(row=2,column=0, columnspan=2, pady=3, padx=3, sticky=EW)

		self.grid_columnconfigure(0, weight=1)

		self.minsize(400,160)
		self.maxsize(9999,160)

	def setup_complete(self):
		self.load_settings()
		self.load_properties()

	def load_settings(self):
		PYBIN_SETTINGS.windows.edit.load_window_size('smk', self)
	def save_settings(self):
		PYBIN_SETTINGS.windows.edit.save_window_size('smk', self)

	def load_property_smk(self):
		smks = ['None']
		for smk in self.widget.parent.bin.smks:
			smks.append(smk.filename)
		self.smks_dropdown.setentries(smks)

		self.overlay_smk.set(0 if not self.smk.overlay_smk else self.widget.parent.bin.smks.index(self.smk.overlay_smk)+1)
	def load_properties(self):
		self.filename.set(self.smk.filename)
		self.load_property_smk()
		self.overlay_x.set(self.smk.offset_x)
		self.overlay_y.set(self.smk.offset_y)

		self.flag_fadein.set((self.smk.flags & DialogBIN.BINSMK.FLAG_FADE_IN == DialogBIN.BINSMK.FLAG_FADE_IN))
		self.flag_dark.set((self.smk.flags & DialogBIN.BINSMK.FLAG_DARK == DialogBIN.BINSMK.FLAG_DARK))
		self.flag_repeat.set((self.smk.flags & DialogBIN.BINSMK.FLAG_REPEATS == DialogBIN.BINSMK.FLAG_REPEATS))
		self.flag_hover.set((self.smk.flags & DialogBIN.BINSMK.FLAG_SHOW_ON_HOVER == DialogBIN.BINSMK.FLAG_SHOW_ON_HOVER))
		self.flag_unk1.set((self.smk.flags & DialogBIN.BINSMK.FLAG_UNK1 == DialogBIN.BINSMK.FLAG_UNK1))
		self.flag_unk2.set((self.smk.flags & DialogBIN.BINSMK.FLAG_UNK2 == DialogBIN.BINSMK.FLAG_UNK2))
		self.flag_unk3.set((self.smk.flags & DialogBIN.BINSMK.FLAG_UNK3 == DialogBIN.BINSMK.FLAG_UNK3))
		self.flag_unk4.set((self.smk.flags & DialogBIN.BINSMK.FLAG_UNK4 == DialogBIN.BINSMK.FLAG_UNK4))

	def save_property_smk(self):
		index = self.overlay_smk.get()-1
		self.smk.overlay_smk = (None if index == -1 else self.widget.parent.bin.smks[index])
	def save_properties(self):
		self.smk.filename = self.filename.get()
		self.save_property_smk()
		self.smk.offset_x = self.overlay_x.get()
		self.smk.offset_y = self.overlay_y.get()

		self.smk.flags = 0
		self.smk.flags |= self.flag_fadein.get() * DialogBIN.BINSMK.FLAG_FADE_IN
		self.smk.flags |= self.flag_dark.get() * DialogBIN.BINSMK.FLAG_DARK
		self.smk.flags |= self.flag_repeat.get() * DialogBIN.BINSMK.FLAG_REPEATS
		self.smk.flags |= self.flag_hover.get() * DialogBIN.BINSMK.FLAG_SHOW_ON_HOVER
		self.smk.flags |= self.flag_unk1.get() * DialogBIN.BINSMK.FLAG_UNK1
		self.smk.flags |= self.flag_unk2.get() * DialogBIN.BINSMK.FLAG_UNK2
		self.smk.flags |= self.flag_unk3.get() * DialogBIN.BINSMK.FLAG_UNK3
		self.smk.flags |= self.flag_unk4.get() * DialogBIN.BINSMK.FLAG_UNK4

	def update_preview(self):
		self.save_properties()
		self.update_smks()
		self.widget.parent.reload_canvas()

	def find_smk(self):
		m = MpqSelect(self, self.widget.parent.mpqhandler, 'SMK', '*.smk', 'Select')
		if m.file and m.file.startswith('MPQ:'):
			self.filename.set(m.file[4:])

	def edit_smk(self):
		if self.overlay_smk.get():
			w,h,x,y,f = parse_geometry(self.winfo_geometry())
			SMKSettings(self, self.widget.parent.bin.smks[self.overlay_smk.get()-1], self.widget, (x+20,y+20))

	def add_smk(self):
		smk = DialogBIN.BINSMK()
		self.widget.parent.bin.smks.append(smk)
		self.smk.overlay_smk = smk
		self.update_smks()
		self.edit_smk()

	def update_smks(self):
		self.load_property_smk()
		self.parent.update_smks()

	def ok(self):
		self.save_settings()
		self.update_preview()
		PyMSDialog.ok(self)

	def cancel(self):
		self.ok()

class WidgetSettings(PyMSDialog):
	def __init__(self, parent, node):
		self.node = node

		self.advanced_widgets = []
		self.advanced_shown = True
		self.show_advanced = BooleanVar()

		self.left = IntegerVar(range=[0,65535])
		self.right = IntegerVar(range=[0,65535])
		self.width = IntegerVar(range=[0,65535])
		calc_right = lambda n: self.calculate(self.right,self.left,self.width,1,-1,False)
		self.left.callback = calc_right
		self.width.callback = calc_right
		self.top = IntegerVar(range=[0,65535])
		self.bottom = IntegerVar(range=[0,65535])
		self.height = IntegerVar(range=[0,65535])
		calc_bottom = lambda n: self.calculate(self.left,self.right,self.width,-1,1,False)
		self.top.callback = calc_bottom
		self.height.callback = calc_bottom
		self.string = StringVar()
		self.identifier = IntegerVar(range=[0,65535])
		self.smk = IntVar()
		self.text_offset_x = IntegerVar(range=[0,65535])
		self.text_offset_y = IntegerVar(range=[0,65535])
		self.responsive_left = IntegerVar(range=[0,65535])
		self.responsive_right = IntegerVar(range=[0,65535])
		self.responsive_width = IntegerVar(range=[0,65535])
		calc_right = lambda n: self.calculate(self.responsive_right,self.responsive_left,self.responsive_width,1,-1,False)
		self.responsive_left.callback = calc_right
		self.responsive_width.callback = calc_right
		self.responsive_top = IntegerVar(range=[0,65535])
		self.responsive_bottom = IntegerVar(range=[0,65535])
		self.responsive_height = IntegerVar(range=[0,65535])
		calc_bottom = lambda n: self.calculate(self.responsive_left,self.responsive_right,self.responsive_width,-1,1,False)
		self.responsive_top.callback = calc_bottom
		self.responsive_height.callback = calc_bottom

		self.flag_unk1 = BooleanVar()
		self.flag_disabled = BooleanVar()
		self.flag_unk2 = BooleanVar()
		self.flag_visible = BooleanVar()
		self.flag_responsive = BooleanVar()
		self.flag_unk3 = BooleanVar()
		self.flag_cancel_btn = BooleanVar()
		self.flag_no_hover_snd = BooleanVar()
		self.flag_virtual_hotkey = BooleanVar()
		self.flag_has_hotkey = BooleanVar()
		self.flag_font_size_10 = BooleanVar()
		self.flag_font_size_16 = BooleanVar()
		self.flag_unk4 = BooleanVar()
		self.flag_transparency = BooleanVar()
		self.flag_font_size_16x = BooleanVar()
		self.flag_unk5 = BooleanVar()
		self.flag_font_size_14 = BooleanVar()
		self.flag_unk6 = BooleanVar()
		self.flag_translucent = BooleanVar()
		self.flag_default_btn = BooleanVar()
		self.flag_on_top = BooleanVar()
		self.flag_text_align_center = BooleanVar()
		self.flag_text_align_right = BooleanVar()
		self.flag_text_align_center2 = BooleanVar()
		self.flag_align_top = BooleanVar()
		self.flag_align_middle = BooleanVar()
		self.flag_align_bottom = BooleanVar()
		self.flag_unk7 = BooleanVar()
		self.flag_unk8 = BooleanVar()
		self.flag_unk9 = BooleanVar()
		self.flag_no_click_snd = BooleanVar()
		self.flag_unk10 = BooleanVar()

		PyMSDialog.__init__(self, parent, 'Edit ' + DialogBIN.BINWidget.TYPE_NAMES[node.widget.type], resizable=(False, False))

	def widgetize(self):
		def calc_button(f, calc, orig, offset, direction, fix):
			image = PhotoImage(file=os.path.join(BASE_DIR,'Images','debug.gif'))
			button = Button(f, image=image, width=20, height=20, command=lambda calc=calc,orig=orig,offset=offset,direction=direction,fix=fix: self.calculate(calc,orig,offset,direction,fix))
			button.image = image
			return button
		boundsframe = LabelFrame(self, text="Bounds")
		Label(boundsframe, text='Left:').grid(row=0,column=0, sticky=E)
		Entry(boundsframe, textvariable=self.left, font=couriernew, width=5).grid(row=0,column=1)
		calculate = calc_button(boundsframe, self.left, self.right, self.width, -1, 1)
		calculate.grid(row=0,column=2)
		self.advanced_widgets.append(calculate)
		Label(boundsframe, text='Top:').grid(row=0,column=3, sticky=E)
		Entry(boundsframe, textvariable=self.top, font=couriernew, width=5).grid(row=0,column=4)
		calculate = calc_button(boundsframe, self.top, self.bottom, self.height, -1, 1)
		calculate.grid(row=0,column=5)
		self.advanced_widgets.append(calculate)
		right_label = Label(boundsframe, text='Right:')
		right_label.grid(row=1,column=0, sticky=E)
		self.advanced_widgets.append(right_label)
		right_entry = Entry(boundsframe, textvariable=self.right, font=couriernew, width=5)
		right_entry.grid(row=1,column=1)
		self.advanced_widgets.append(right_entry)
		calculate = calc_button(boundsframe, self.right, self.left, self.width, 1, -1)
		calculate.grid(row=1,column=2)
		self.advanced_widgets.append(calculate)
		bottom_label = Label(boundsframe, text='Bottom:')
		bottom_label.grid(row=1,column=3, sticky=E)
		self.advanced_widgets.append(bottom_label)
		bottom_entry = Entry(boundsframe, textvariable=self.bottom, font=couriernew, width=5)
		bottom_entry.grid(row=1,column=4)
		self.advanced_widgets.append(bottom_entry)
		calculate = calc_button(boundsframe, self.bottom, self.top, self.height, 1, -1)
		calculate.grid(row=1,column=5)
		self.advanced_widgets.append(calculate)
		Label(boundsframe, text='Width:').grid(row=2,column=0, sticky=E)
		Entry(boundsframe, textvariable=self.width, font=couriernew, width=5).grid(row=2,column=1)
		calculate = calc_button(boundsframe, self.width, self.right, self.left, -1, 1)
		calculate.grid(row=2,column=2)
		self.advanced_widgets.append(calculate)
		Label(boundsframe, text='Height:').grid(row=2,column=3, sticky=E)
		Entry(boundsframe, textvariable=self.height, font=couriernew, width=5).grid(row=2,column=4)
		calculate = calc_button(boundsframe, self.height, self.bottom, self.top, -1, 1)
		calculate.grid(row=2,column=5)
		self.advanced_widgets.append(calculate)
		boundsframe.grid(row=0,column=0, padx=5,pady=0, ipadx=2,ipady=2, sticky=N)

		responsiveframe = LabelFrame(self, text="Mouse Response")
		Label(responsiveframe, text='Left:').grid(row=0,column=0, sticky=E)
		Entry(responsiveframe, textvariable=self.responsive_left, font=couriernew, width=5).grid(row=0,column=1)
		calculate = calc_button(responsiveframe, self.responsive_left, self.responsive_right, self.responsive_width, -1, 1)
		calculate.grid(row=0,column=2)
		self.advanced_widgets.append(calculate)
		Label(responsiveframe, text='Top:').grid(row=0,column=3, sticky=E)
		Entry(responsiveframe, textvariable=self.responsive_top, font=couriernew, width=5).grid(row=0,column=4)
		calculate = calc_button(responsiveframe, self.responsive_top, self.responsive_bottom, self.responsive_height, -1, 1)
		calculate.grid(row=0,column=5)
		self.advanced_widgets.append(calculate)
		right_label = Label(responsiveframe, text='Right:')
		right_label.grid(row=1,column=0, sticky=E)
		self.advanced_widgets.append(right_label)
		right_entry = Entry(responsiveframe, textvariable=self.responsive_right, font=couriernew, width=5)
		right_entry.grid(row=1,column=1)
		self.advanced_widgets.append(right_entry)
		calculate = calc_button(responsiveframe, self.responsive_right, self.responsive_left, self.responsive_width, 1, -1)
		calculate.grid(row=1,column=2)
		self.advanced_widgets.append(calculate)
		bottom_label = Label(responsiveframe, text='Bottom:')
		bottom_label.grid(row=1,column=3, sticky=E)
		self.advanced_widgets.append(bottom_label)
		bottom_entry = Entry(responsiveframe, textvariable=self.responsive_bottom, font=couriernew, width=5)
		bottom_entry.grid(row=1,column=4)
		self.advanced_widgets.append(bottom_entry)
		calculate = calc_button(responsiveframe, self.responsive_bottom, self.responsive_top, self.responsive_height, 1, -1)
		calculate.grid(row=1,column=5)
		self.advanced_widgets.append(calculate)
		Label(responsiveframe, text='Width:').grid(row=2,column=0, sticky=E)
		Entry(responsiveframe, textvariable=self.responsive_width, font=couriernew, width=5).grid(row=2,column=1)
		calculate = calc_button(responsiveframe, self.responsive_width, self.responsive_right, self.responsive_left, -1, 1)
		calculate.grid(row=2,column=2)
		self.advanced_widgets.append(calculate)
		Label(responsiveframe, text='Height:').grid(row=2,column=3, sticky=E)
		Entry(responsiveframe, textvariable=self.responsive_height, font=couriernew, width=5).grid(row=2,column=4)
		calculate = calc_button(responsiveframe, self.responsive_height, self.responsive_bottom, self.responsive_top, -1, 1)
		calculate.grid(row=2,column=5)
		self.advanced_widgets.append(calculate)
		Checkbutton(responsiveframe, text='Responds to Mouse', variable=self.flag_responsive).grid(row=3,column=0, columnspan=6)
		responsiveframe.grid(row=0,column=1, padx=5,pady=0, ipadx=2,ipady=2, sticky=N)

		isimage = self.node.widget.type == DialogBIN.BINWidget.TYPE_IMAGE
		stringframe = LabelFrame(self, text="String")
		textframe = Frame(stringframe)
		self.string_label = Label(textframe, text='Image:' if isimage else 'Text:')
		self.string_label.grid(row=0,column=0)
		Entry(textframe, textvariable=self.string, font=couriernew).grid(row=0,column=1, sticky=EW)
		icon = PhotoImage(file=os.path.join(BASE_DIR,'Images','openmpq.gif'))
		findimage = Button(textframe, image=icon, width=20, height=20)#, command=btn[1], state=btn[3])
		findimage.icon = icon
		findimage.grid(row=0, column=2)
		textframe.grid_columnconfigure(1, weight=1)
		textframe.grid(row=0,column=0, columnspan=5, sticky=EW)
		transparent = Checkbutton(textframe, text='Image Transparency', variable=self.flag_transparency)
		transparent.grid(row=1,column=0, columnspan=5, sticky=W)
		offsetframe = LabelFrame(stringframe, text='Offset')
		Label(offsetframe, text='X:').grid(row=0,column=0, sticky=E)
		Entry(offsetframe, textvariable=self.text_offset_x, font=couriernew, width=5).grid(row=0,column=1)
		Label(offsetframe, text='Y:').grid(row=1,column=0, sticky=E)
		Entry(offsetframe, textvariable=self.text_offset_y, font=couriernew, width=5).grid(row=1,column=1)
		offsetframe.grid(row=3,column=0, padx=3,pady=3, ipadx=2,ipady=2, sticky=N)
		hotkeyframe = LabelFrame(stringframe, text='Hotkey')
		Checkbutton(hotkeyframe, text='Normal', variable=self.flag_has_hotkey).grid(row=0,column=0, sticky=W)
		Checkbutton(hotkeyframe, text='Virtual', variable=self.flag_virtual_hotkey).grid(row=1,column=0, sticky=W)
		hotkeyframe.grid(row=3,column=1, padx=3,pady=3, sticky=N)
		horframe = LabelFrame(stringframe, text="Horizontal")
		Checkbutton(horframe, text='Center', variable=self.flag_text_align_center).grid(row=0,column=0, sticky=W)
		Checkbutton(horframe, text='Right', variable=self.flag_text_align_right).grid(row=1,column=0, sticky=W)
		Checkbutton(horframe, text='Center 2', variable=self.flag_text_align_center2).grid(row=2,column=0, sticky=W)
		horframe.grid(row=3,column=2, padx=3,pady=3, sticky=N)
		verframe = LabelFrame(stringframe, text="Vertical")
		Checkbutton(verframe, text='Top', variable=self.flag_align_top).grid(row=0,column=0, sticky=W)
		Checkbutton(verframe, text='Middle', variable=self.flag_align_middle).grid(row=1,column=0, sticky=W)
		Checkbutton(verframe, text='Bottom', variable=self.flag_align_bottom).grid(row=2,column=0, sticky=W)
		verframe.grid(row=3,column=3, padx=3,pady=3, sticky=N)
		fontframe = LabelFrame(stringframe, text='Font')
		Checkbutton(fontframe, text='Size 10', variable=self.flag_font_size_10).grid(row=0,column=0, sticky=W)
		Checkbutton(fontframe, text='Size 14', variable=self.flag_font_size_14).grid(row=1,column=0, sticky=W)
		Checkbutton(fontframe, text='Size 16', variable=self.flag_font_size_16).grid(row=2,column=0, sticky=W)
		Checkbutton(fontframe, text='Size 16x', variable=self.flag_font_size_16x).grid(row=3,column=0, sticky=W)
		fontframe.grid(row=3,column=4, padx=3,pady=3, sticky=N)

		stringframe.grid_columnconfigure(0, weight=1)
		stringframe.grid_columnconfigure(1, weight=1)
		stringframe.grid_columnconfigure(2, weight=1)
		stringframe.grid_columnconfigure(3, weight=1)
		stringframe.grid_columnconfigure(4, weight=1)
		stringframe.grid(row=1,column=0, columnspan=2, padx=5,pady=0, ipadx=2,ipady=2, sticky=NSEW)

		smkframe = LabelFrame(self, text='SMK')
		self.smks_dropdown = DropDown(smkframe, self.smk, ['None'], stay_right=True)
		self.smks_dropdown.grid(row=0, column=0, padx=2,pady=2, sticky=EW)
		image = PhotoImage(file=os.path.join(BASE_DIR,'Images','edit.gif'))
		button = Button(smkframe, image=image, width=20, height=20, command=self.edit_smk)
		button.image = image
		button.grid(row=0, column=1)
		image = PhotoImage(file=os.path.join(BASE_DIR,'Images','add.gif'))
		button = Button(smkframe, image=image, width=20, height=20, command=self.add_smk)
		button.image = image
		button.grid(row=0, column=2)
		Checkbutton(smkframe, text='Translucent', variable=self.flag_translucent).grid(row=1,column=0, columnspan=3)
		smkframe.grid_columnconfigure(0, weight=1)
		smkframe.grid(row=2,column=0, columnspan=2, padx=5,pady=0, ipadx=2,ipady=2, sticky=NSEW)

		otherframe = Frame(self)
		stateframe = LabelFrame(otherframe, text='State')
		Checkbutton(stateframe, text='Visible', variable=self.flag_visible).grid(row=2,column=0, sticky=W)
		Checkbutton(stateframe, text='Disabled', variable=self.flag_disabled).grid(row=3,column=0, sticky=W)
		stateframe.grid(row=0,column=0, padx=2,pady=2, sticky=N)
		soundframe = LabelFrame(otherframe, text='Sounds')
		Checkbutton(soundframe, text='No Hover', variable=self.flag_no_hover_snd).grid(row=2,column=0, sticky=W)
		Checkbutton(soundframe, text='No Click', variable=self.flag_no_click_snd).grid(row=3,column=0, sticky=W)
		soundframe.grid(row=0,column=1, padx=2,pady=2, sticky=N)
		typeframe = LabelFrame(otherframe, text='Btn. Type')
		Checkbutton(typeframe, text='Default', variable=self.flag_default_btn).grid(row=0,column=0, sticky=W)
		Checkbutton(typeframe, text='Cancel', variable=self.flag_cancel_btn).grid(row=1,column=0, sticky=W)
		typeframe.grid(row=0,column=2, padx=2,pady=2, sticky=N)
		otherframe.grid(row=3,column=0, columnspan=2, padx=3,pady=3, sticky=EW)

		miscframe = LabelFrame(self, text='Misc.')
		Checkbutton(miscframe, text='Bring to Front', variable=self.flag_on_top).grid(row=0,column=0, sticky=W)
		f = Frame(miscframe)
		Label(f, text='Control ID:').pack(side=LEFT)
		Entry(f, textvariable=self.identifier, font=couriernew, width=5).pack(side=LEFT)
		f.grid(row=0,column=3, columnspan=2, padx=5, sticky=E)
		Checkbutton(miscframe, text='Unknown 0', variable=self.flag_unk1).grid(row=1,column=0, sticky=W)
		Checkbutton(miscframe, text='Unknown 2', variable=self.flag_unk2).grid(row=1,column=1, sticky=W)
		Checkbutton(miscframe, text='Unknown 5', variable=self.flag_unk3).grid(row=1,column=2, sticky=W)
		Checkbutton(miscframe, text='Unknown 12', variable=self.flag_unk4).grid(row=1,column=3, sticky=W)
		Checkbutton(miscframe, text='Unknown 15', variable=self.flag_unk5).grid(row=1,column=4, sticky=W)
		Checkbutton(miscframe, text='Unknown 17', variable=self.flag_unk6).grid(row=2,column=0, sticky=W)
		Checkbutton(miscframe, text='Unknown 27', variable=self.flag_unk7).grid(row=2,column=1, sticky=W)
		Checkbutton(miscframe, text='Unknown 28', variable=self.flag_unk8).grid(row=2,column=2, sticky=W)
		Checkbutton(miscframe, text='Unknown 29', variable=self.flag_unk9).grid(row=2,column=3, sticky=W)
		Checkbutton(miscframe, text='Unknown 31', variable=self.flag_unk10).grid(row=2,column=4, sticky=W)
		miscframe.grid(row=4,column=0, columnspan=2, padx=3,pady=3, sticky=NSEW)

		isdialog = self.node.widget.type == DialogBIN.BINWidget.TYPE_DIALOG
		if isimage or isdialog:
			self.advanced_widgets.extend((offsetframe,hotkeyframe,horframe,verframe,fontframe))
		if not isimage or isdialog:
			self.advanced_widgets.extend((transparent,findimage))
		if isdialog:
			self.advanced_widgets.append(otherframe)
		else:
			hassound = self.node.widget.type in (DialogBIN.BINWidget.TYPE_DEFAULT_BTN,DialogBIN.BINWidget.TYPE_BUTTON,DialogBIN.BINWidget.TYPE_OPTION_BTN,DialogBIN.BINWidget.TYPE_CHECKBOX,DialogBIN.BINWidget.TYPE_HIGHLIGHT_BTN,DialogBIN.BINWidget.TYPE_LISTBOX,DialogBIN.BINWidget.TYPE_SLIDER)
			if not hassound:
				self.advanced_widgets.append(soundframe)
			isbtn = self.node.widget.type in (DialogBIN.BINWidget.TYPE_DEFAULT_BTN,DialogBIN.BINWidget.TYPE_BUTTON,DialogBIN.BINWidget.TYPE_HIGHLIGHT_BTN)
			if not isbtn:
				self.advanced_widgets.extend((typeframe,soundframe,smkframe))
		self.advanced_widgets.append(miscframe)

		bottom = Frame(self)
		ok = Button(bottom, text='Ok', width=10, command=self.ok)
		ok.pack(side=LEFT, padx=1, pady=3)
		Button(bottom, text='Update Preview', width=15, command=self.update_preview).pack(side=LEFT, padx=3, pady=3)
		Checkbutton(bottom, text='Advanced', variable=self.show_advanced, command=self.update_advanced).pack(side=RIGHT, padx=1, pady=3)
		bottom.grid(row=5,column=0, columnspan=2, pady=3, padx=3, sticky=EW)

		self.load_settings()
		self.load_properties()
		self.update_advanced()
		return ok

	def update_advanced(self):
		self.minsize(0,0)
		self.maxsize(9999, 9999)
		w,h,x,y,f = parse_geometry(self.geometry())
		center_x = x + w/2.0
		center_y = y + h/2.0
		show = self.show_advanced.get()
		if show and not self.advanced_shown:
			for widget in self.advanced_widgets:
				widget.grid()
			self.string_label['text'] = 'Text/Image:'
			self.advanced_shown = True
		elif not show and self.advanced_shown:
			for widget in self.advanced_widgets:
				widget.grid_remove()
			self.string_label['text'] = 'Image:' if self.node.widget.type == DialogBIN.BINWidget.TYPE_IMAGE else 'Text:'
			self.advanced_shown = False
		self.update_idletasks()
		w,h,x,y,f = parse_geometry(self.geometry())
		center_x -= w/2.0
		center_y -= h/2.0
		self.geometry('+%d+%d' % (int(center_x),int(center_y)))
		self.minsize(w,h)
		self.maxsize(w,h)

	def calculate(self, calc, orig, offset, direction, fix, allow_advanced=True):
		if not self.show_advanced.get() or allow_advanced:
			calc.set(orig.get() + offset.get() * direction + fix)

	def load_settings(self):
		self.show_advanced.set(PYBIN_SETTINGS.edit.widget.get('advanced',False))
		PYBIN_SETTINGS.windows.edit.load_window_size('widget', self)
	def save_settings(self):
		PYBIN_SETTINGS.edit.widget.advanced = not not self.show_advanced.get()
		PYBIN_SETTINGS.windows.edit.save_window_size('widget', self)

	def load_property_smk(self):
		smks = ['None']
		for smk in self.parent.bin.smks:
			smks.append(smk.filename)
		self.smks_dropdown.setentries(smks)
		self.smk.set(0 if not self.node.widget.smk else self.parent.bin.smks.index(self.node.widget.smk)+1)
	def load_properties(self):
		self.left.set(self.node.widget.x1, True)
		self.right.set(self.node.widget.x2, True)
		self.width.set(self.node.widget.width, True)
		self.top.set(self.node.widget.y1, True)
		self.bottom.set(self.node.widget.y2, True)
		self.height.set(self.node.widget.height, True)
		self.string.set(TBL.decompile_string(self.node.widget.string))
		self.identifier.set(self.node.widget.identifier)
		self.load_property_smk()
		self.text_offset_x.set(self.node.widget.text_offset_x)
		self.text_offset_y.set(self.node.widget.text_offset_y)
		self.responsive_left.set(self.node.widget.responsive_x1, True)
		self.responsive_right.set(self.node.widget.responsive_x2, True)
		self.responsive_width.set(self.node.widget.responsive_width, True)
		self.responsive_top.set(self.node.widget.responsive_y1, True)
		self.responsive_bottom.set(self.node.widget.responsive_y2, True)
		self.responsive_height.set(self.node.widget.responsive_height, True)

		self.flag_unk1.set((self.node.widget.flags & DialogBIN.BINWidget.FLAG_UNK1 == DialogBIN.BINWidget.FLAG_UNK1))
		self.flag_disabled.set((self.node.widget.flags & DialogBIN.BINWidget.FLAG_DISABLED == DialogBIN.BINWidget.FLAG_DISABLED))
		self.flag_unk2.set((self.node.widget.flags & DialogBIN.BINWidget.FLAG_UNK2 == DialogBIN.BINWidget.FLAG_UNK2))
		self.flag_visible.set((self.node.widget.flags & DialogBIN.BINWidget.FLAG_VISIBLE == DialogBIN.BINWidget.FLAG_VISIBLE))
		self.flag_responsive.set((self.node.widget.flags & DialogBIN.BINWidget.FLAG_RESPONSIVE == DialogBIN.BINWidget.FLAG_RESPONSIVE))
		self.flag_unk3.set((self.node.widget.flags & DialogBIN.BINWidget.FLAG_UNK3 == DialogBIN.BINWidget.FLAG_UNK3))
		self.flag_cancel_btn.set((self.node.widget.flags & DialogBIN.BINWidget.FLAG_CANCEL_BTN == DialogBIN.BINWidget.FLAG_CANCEL_BTN))
		self.flag_no_hover_snd.set((self.node.widget.flags & DialogBIN.BINWidget.FLAG_NO_HOVER_SND == DialogBIN.BINWidget.FLAG_NO_HOVER_SND))
		self.flag_virtual_hotkey.set((self.node.widget.flags & DialogBIN.BINWidget.FLAG_VIRTUAL_HOTKEY == DialogBIN.BINWidget.FLAG_VIRTUAL_HOTKEY))
		self.flag_has_hotkey.set((self.node.widget.flags & DialogBIN.BINWidget.FLAG_HAS_HOTKEY == DialogBIN.BINWidget.FLAG_HAS_HOTKEY))
		self.flag_font_size_10.set((self.node.widget.flags & DialogBIN.BINWidget.FLAG_FONT_SIZE_10 == DialogBIN.BINWidget.FLAG_FONT_SIZE_10))
		self.flag_font_size_16.set((self.node.widget.flags & DialogBIN.BINWidget.FLAG_FONT_SIZE_16 == DialogBIN.BINWidget.FLAG_FONT_SIZE_16))
		self.flag_unk4.set((self.node.widget.flags & DialogBIN.BINWidget.FLAG_UNK4 == DialogBIN.BINWidget.FLAG_UNK4))
		self.flag_transparency.set((self.node.widget.flags & DialogBIN.BINWidget.FLAG_TRANSPARENCY == DialogBIN.BINWidget.FLAG_TRANSPARENCY))
		self.flag_font_size_16x.set((self.node.widget.flags & DialogBIN.BINWidget.FLAG_FONT_SIZE_16x == DialogBIN.BINWidget.FLAG_FONT_SIZE_16x))
		self.flag_unk5.set((self.node.widget.flags & DialogBIN.BINWidget.FLAG_UNK5 == DialogBIN.BINWidget.FLAG_UNK5))
		self.flag_font_size_14.set((self.node.widget.flags & DialogBIN.BINWidget.FLAG_FONT_SIZE_14 == DialogBIN.BINWidget.FLAG_FONT_SIZE_14))
		self.flag_unk6.set((self.node.widget.flags & DialogBIN.BINWidget.FLAG_UNK6 == DialogBIN.BINWidget.FLAG_UNK6))
		self.flag_translucent.set((self.node.widget.flags & DialogBIN.BINWidget.FLAG_TRANSLUCENT == DialogBIN.BINWidget.FLAG_TRANSLUCENT))
		self.flag_default_btn.set((self.node.widget.flags & DialogBIN.BINWidget.FLAG_DEFAULT_BTN == DialogBIN.BINWidget.FLAG_DEFAULT_BTN))
		self.flag_on_top.set((self.node.widget.flags & DialogBIN.BINWidget.FLAG_ON_TOP == DialogBIN.BINWidget.FLAG_ON_TOP))
		self.flag_text_align_center.set((self.node.widget.flags & DialogBIN.BINWidget.FLAG_TEXT_ALIGN_CENTER == DialogBIN.BINWidget.FLAG_TEXT_ALIGN_CENTER))
		self.flag_text_align_right.set((self.node.widget.flags & DialogBIN.BINWidget.FLAG_TEXT_ALIGN_RIGHT == DialogBIN.BINWidget.FLAG_TEXT_ALIGN_RIGHT))
		self.flag_text_align_center2.set((self.node.widget.flags & DialogBIN.BINWidget.FLAG_TEXT_ALIGN_CENTER2 == DialogBIN.BINWidget.FLAG_TEXT_ALIGN_CENTER2))
		self.flag_align_top.set((self.node.widget.flags & DialogBIN.BINWidget.FLAG_ALIGN_TOP == DialogBIN.BINWidget.FLAG_ALIGN_TOP))
		self.flag_align_middle.set((self.node.widget.flags & DialogBIN.BINWidget.FLAG_ALIGN_MIDDLE == DialogBIN.BINWidget.FLAG_ALIGN_MIDDLE))
		self.flag_align_bottom.set((self.node.widget.flags & DialogBIN.BINWidget.FLAG_ALIGN_BOTTOM == DialogBIN.BINWidget.FLAG_ALIGN_BOTTOM))
		self.flag_unk7.set((self.node.widget.flags & DialogBIN.BINWidget.FLAG_UNK7 == DialogBIN.BINWidget.FLAG_UNK7))
		self.flag_unk8.set((self.node.widget.flags & DialogBIN.BINWidget.FLAG_UNK8 == DialogBIN.BINWidget.FLAG_UNK8))
		self.flag_unk9.set((self.node.widget.flags & DialogBIN.BINWidget.FLAG_UNK9 == DialogBIN.BINWidget.FLAG_UNK9))
		self.flag_no_click_snd.set((self.node.widget.flags & DialogBIN.BINWidget.FLAG_NO_CLICK_SND == DialogBIN.BINWidget.FLAG_NO_CLICK_SND))
		self.flag_unk10.set((self.node.widget.flags & DialogBIN.BINWidget.FLAG_UNK10 == DialogBIN.BINWidget.FLAG_UNK10))

	def save_property_smk(self):
		index = self.smk.get()-1
		self.node.widget.smk = (None if index == -1 else self.parent.bin.smks[index])
	def save_properties(self):
		self.node.widget.x1 = self.left.get()
		self.node.widget.x2 = self.right.get()
		self.node.widget.width = self.width.get()
		self.node.widget.y1 = self.top.get()
		self.node.widget.y2 = self.bottom.get()
		self.node.widget.height = self.height.get()
		self.node.widget.string = TBL.compile_string(self.string.get())
		self.node.widget.identifier = self.identifier.get()
		self.save_property_smk()
		self.node.widget.text_offset_x = self.text_offset_x.get()
		self.node.widget.text_offset_y = self.text_offset_y.get()
		self.node.widget.responsive_x1 = self.responsive_left.get()
		self.node.widget.responsive_x2 = self.responsive_right.get()
		self.node.widget.responsive_width = self.responsive_width.get()
		self.node.widget.responsive_y1 = self.responsive_top.get()
		self.node.widget.responsive_y2 = self.responsive_bottom.get()
		self.node.widget.responsive_height = self.responsive_height.get()

		self.node.widget.flags = 0
		self.node.widget.flags |= self.flag_unk1.get() * DialogBIN.BINWidget.FLAG_UNK1
		self.node.widget.flags |= self.flag_disabled.get() * DialogBIN.BINWidget.FLAG_DISABLED
		self.node.widget.flags |= self.flag_unk2.get() * DialogBIN.BINWidget.FLAG_UNK2
		self.node.widget.flags |= self.flag_visible.get() * DialogBIN.BINWidget.FLAG_VISIBLE
		self.node.widget.flags |= self.flag_responsive.get() * DialogBIN.BINWidget.FLAG_RESPONSIVE
		self.node.widget.flags |= self.flag_unk3.get() * DialogBIN.BINWidget.FLAG_UNK3
		self.node.widget.flags |= self.flag_cancel_btn.get() * DialogBIN.BINWidget.FLAG_CANCEL_BTN
		self.node.widget.flags |= self.flag_no_hover_snd.get() * DialogBIN.BINWidget.FLAG_NO_HOVER_SND
		self.node.widget.flags |= self.flag_virtual_hotkey.get() * DialogBIN.BINWidget.FLAG_VIRTUAL_HOTKEY
		self.node.widget.flags |= self.flag_has_hotkey.get() * DialogBIN.BINWidget.FLAG_HAS_HOTKEY
		self.node.widget.flags |= self.flag_font_size_10.get() * DialogBIN.BINWidget.FLAG_FONT_SIZE_10
		self.node.widget.flags |= self.flag_font_size_16.get() * DialogBIN.BINWidget.FLAG_FONT_SIZE_16
		self.node.widget.flags |= self.flag_unk4.get() * DialogBIN.BINWidget.FLAG_UNK4
		self.node.widget.flags |= self.flag_transparency.get() * DialogBIN.BINWidget.FLAG_TRANSPARENCY
		self.node.widget.flags |= self.flag_font_size_16x.get() * DialogBIN.BINWidget.FLAG_FONT_SIZE_16x
		self.node.widget.flags |= self.flag_unk5.get() * DialogBIN.BINWidget.FLAG_UNK5
		self.node.widget.flags |= self.flag_font_size_14.get() * DialogBIN.BINWidget.FLAG_FONT_SIZE_14
		self.node.widget.flags |= self.flag_unk6.get() * DialogBIN.BINWidget.FLAG_UNK6
		self.node.widget.flags |= self.flag_translucent.get() * DialogBIN.BINWidget.FLAG_TRANSLUCENT
		self.node.widget.flags |= self.flag_default_btn.get() * DialogBIN.BINWidget.FLAG_DEFAULT_BTN
		self.node.widget.flags |= self.flag_on_top.get() * DialogBIN.BINWidget.FLAG_ON_TOP
		self.node.widget.flags |= self.flag_text_align_center.get() * DialogBIN.BINWidget.FLAG_TEXT_ALIGN_CENTER
		self.node.widget.flags |= self.flag_text_align_right.get() * DialogBIN.BINWidget.FLAG_TEXT_ALIGN_RIGHT
		self.node.widget.flags |= self.flag_text_align_center2.get() * DialogBIN.BINWidget.FLAG_TEXT_ALIGN_CENTER2
		self.node.widget.flags |= self.flag_align_top.get() * DialogBIN.BINWidget.FLAG_ALIGN_TOP
		self.node.widget.flags |= self.flag_align_middle.get() * DialogBIN.BINWidget.FLAG_ALIGN_MIDDLE
		self.node.widget.flags |= self.flag_align_bottom.get() * DialogBIN.BINWidget.FLAG_ALIGN_BOTTOM
		self.node.widget.flags |= self.flag_unk7.get() * DialogBIN.BINWidget.FLAG_UNK7
		self.node.widget.flags |= self.flag_unk8.get() * DialogBIN.BINWidget.FLAG_UNK8
		self.node.widget.flags |= self.flag_unk9.get() * DialogBIN.BINWidget.FLAG_UNK9
		self.node.widget.flags |= self.flag_no_click_snd.get() * DialogBIN.BINWidget.FLAG_NO_CLICK_SND
		self.node.widget.flags |= self.flag_unk10.get() * DialogBIN.BINWidget.FLAG_UNK10
		self.node.string = None
		self.node.item_string_images = None

	def update_preview(self):
		self.save_properties()
		self.parent.reload_list()
		self.parent.reload_canvas()

	def edit_smk(self):
		if self.node.widget.smk:
			SMKSettings(self, self.node.widget.smk)

	def add_smk(self):
		pass

	def update_smks(self):
		self.load_property_smk()

	def ok(self):
		self.save_settings()
		self.update_preview()
		PyMSDialog.ok(self)

	def cancel(self):
		self.ok()

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

class StringPreview:
	# GLYPH_CACHE = {}

	def __init__(self, text, font, tfontgam, remap=None, remap_palette=None, default_color=1):
		self.text = text
		self.font = font
		self.tfontgam = tfontgam
		self.remap = remap
		self.remap_palette = remap_palette
		self.default_color = default_color
		self.glyphs = None

	def get_glyphs(self):
		if self.glyphs == None:
			self.glyphs = []
			color = self.default_color
			for c in self.text:
				a = ord(c)
				if a >= self.font.start and a < self.font.start + len(self.font.letters):
					a -= self.font.start
					self.glyphs.append(FNT.letter_to_photo(self.tfontgam, self.font.letters[a], color, self.remap, self.remap_palette))
				elif (a in self.remap or a in FNT.COLOR_CODES_INGAME) and not color in FNT.COLOR_OVERPOWER:
					color = a if a > 1 else self.default_color
		return self.glyphs

	def get_positions(self, x1,y1,x2,y2, align_flags):
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
				if align_flags & DialogBIN.BINWidget.FLAG_TEXT_ALIGN_CENTER:
					o = int((size[0] - line_width[0]) / 2.0)
				elif align_flags & DialogBIN.BINWidget.FLAG_TEXT_ALIGN_RIGHT:
					o = size[0] - line_width[0]
				for w in line:
					positions.append([position[0] + o, position[1]])
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
				w += 1
				word.append(w)
				word_width[0] += w
			if c == ' ':
				if line and line_width[0] + word_width[0] >= size[0]:
					add_line()
				add_word()
				if line_width[0] >= size[0]:
					add_line()
			elif c in '\r\n':
				add_word()
				add_line()

		if word:
			add_word()
		if line:
			add_line()

		if align_flags & (DialogBIN.BINWidget.FLAG_ALIGN_MIDDLE | DialogBIN.BINWidget.FLAG_ALIGN_BOTTOM):
			height = y2-y1
			offset = height - (position[1]-y1)
			if align_flags & DialogBIN.BINWidget.FLAG_ALIGN_MIDDLE:
				offset /= 2
			for position in positions:
				position[1] += offset
		return positions

class WidgetNode:
	SMK_FRAME_CACHE = {}

	def __init__(self, toplevel, widget=None):
		self.toplevel = toplevel
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
		self.smks = None
		self.dialog_image = None
		self.frame_delay = None
		self.frame_waited = 0

		self.item_bounds = None
		self.item_text_bounds = None
		self.item_responsive_bounds = None
		self.item_string_images = None
		self.item_image = None
		self.item_smks = []
		self.item_dialog = None

	def get_name(self):
		name = 'Group'
		if self.widget:
			name = DialogBIN.BINWidget.TYPE_NAMES[self.widget.type]
			if self.widget.display_text():
				name = '%s [%s]' % (TBL.decompile_string(self.widget.display_text()),name)
		if self.name:
			name = '%s [%s]' % self.name
		return name

	def remove_from_parent(self):
		if self.parent:
			self.parent.children.remove(self)
			self.parent = None

	def add_child(self, node, index=-1):
		node.remove_from_parent()
		node.parent = self
		if index == -1:
			self.children.append(node)
		else:
			self.children.insert(index, node)

	def visible(self):
		if self.widget and not self.widget.flags & DialogBIN.BINWidget.FLAG_VISIBLE:
			return self.toplevel.show_hidden.get()
		return True

	def enabled(self):
		if self.widget and self.widget.flags & DialogBIN.BINWidget.FLAG_DISABLED:
			return False
		return True

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

	def text_box(self):
		text_box = self.bounding_box()
		if self.widget:
			text_box[0] += self.widget.text_offset_x
			text_box[1] += self.widget.text_offset_y
			if self.widget.type == DialogBIN.BINWidget.TYPE_CHECKBOX:
				image = self.toplevel.dialog_asset(DialogBIN.DIALOG_ASSET_CHECK_SELECTED)
				if image:
					text_box[0] += image.size[0] + 4
			elif self.widget.type == DialogBIN.BINWidget.TYPE_OPTION_BTN:
				image = self.toplevel.dialog_asset(DialogBIN.DIALOG_ASSET_RADIO_SELECTED)
				if image:
					text_box[0] += image.size[0] + 4
		return text_box

	def update_dialog(self):
		reorder = False
		self.dialog_image = None
		if self.widget:
			if self.visible():
				x1,y1,x2,y2 = self.bounding_box()
				x = x1
				y = y1
				anchor = NW
				if self.widget.type == DialogBIN.BINWidget.TYPE_CHECKBOX:
					asset_id = DialogBIN.DIALOG_ASSET_CHECK_DISABLED
					if self.enabled():
						asset_id = DialogBIN.DIALOG_ASSET_CHECK_SELECTED
					pil = self.toplevel.dialog_asset(asset_id)
					if pil:
						self.dialog_image = ImageTk.PhotoImage(pil)
						y += (y2 - y1) / 2
						anchor = W
				elif self.widget.type == DialogBIN.BINWidget.TYPE_OPTION_BTN:
					asset_id = DialogBIN.DIALOG_ASSET_RADIO_DISABLED
					if self.enabled():
						asset_id = DialogBIN.DIALOG_ASSET_RADIO_SELECTED
					pil = self.toplevel.dialog_asset(asset_id)
					if pil:
						self.dialog_image = ImageTk.PhotoImage(pil)
						y += (y2 - y1) / 2
						anchor = W
				elif self.widget.type == DialogBIN.BINWidget.TYPE_SLIDER:
					if self.enabled():
						left = self.toplevel.dialog_asset(DialogBIN.DIALOG_ASSET_SLIDER_LEFT)
						mid = self.toplevel.dialog_asset(DialogBIN.DIALOG_ASSET_SLIDER_MIDDLE)
						spot = self.toplevel.dialog_asset(DialogBIN.DIALOG_ASSET_SLIDER_SPOT)
						right = self.toplevel.dialog_asset(DialogBIN.DIALOG_ASSET_SLIDER_RIGHT)
						dot = self.toplevel.dialog_asset(DialogBIN.DIALOG_ASSET_SLIDER_DOT_YELLOW)
					else:
						left = self.toplevel.dialog_asset(DialogBIN.DIALOG_ASSET_SLIDER_LEFT_DISABLED)
						mid = self.toplevel.dialog_asset(DialogBIN.DIALOG_ASSET_SLIDER_MIDDLE_DISABLED)
						spot = self.toplevel.dialog_asset(DialogBIN.DIALOG_ASSET_SLIDER_SPOT_DISABLED)
						right = self.toplevel.dialog_asset(DialogBIN.DIALOG_ASSET_SLIDER_RIGHT_DISABLED)
						dot = self.toplevel.dialog_asset(DialogBIN.DIALOG_ASSET_SLIDER_DOT_DISABLED)
					if left and mid and spot and right:
						width = x2-x1
						height = 0
						for img in (left,mid,spot,right,dot):
							if img:
								height = max(height, img.size[1])
						spots = 8
						spots_padding = 0
						while spots_padding < 25 and spots > 1:
							spots -= 1
							spots_padding = (width - left.size[0] - right.size[0] - spot.size[0] * (spots+1)) / spots
						draw_x = 0
						mid_y = height / 2
						pil = PILImage.new('RGBA', (width,height))
						pil.paste(left, (draw_x,mid_y - left.size[1]/2))
						draw_x += left.size[0]
						while spots >= 0:
							pil.paste(spot, (draw_x,mid_y - spot.size[1]/2))
							draw_x += spot.size[0]
							if spots and spots_padding > 0:
								pad = mid.resize((spots_padding, mid.size[1]))
								pil.paste(pad, (draw_x,mid_y - pad.size[1]/2))
								draw_x += pad.size[0]
							spots -= 1
						pil.paste(right, (draw_x,mid_y - right.size[1]/2))
						if dot:
							pil.paste(dot, ((width - dot.size[0])/2, mid_y - dot.size[1]/2))
						self.dialog_image = ImageTk.PhotoImage(pil)
						y += (y2 - y1) / 2
						anchor = W
				elif self.widget.type in (DialogBIN.BINWidget.TYPE_BUTTON,DialogBIN.BINWidget.TYPE_DEFAULT_BTN):
					if self.enabled():
						left = self.toplevel.dialog_asset(DialogBIN.DIALOG_ASSET_BUTTON_MID_LEFT)
						mid = self.toplevel.dialog_asset(DialogBIN.DIALOG_ASSET_BUTTON_MID_MIDDLE)
						right = self.toplevel.dialog_asset(DialogBIN.DIALOG_ASSET_BUTTON_MID_RIGHT)
					else:
						left = self.toplevel.dialog_asset(DialogBIN.DIALOG_ASSET_BUTTON_MID_DISABLED_LEFT)
						mid = self.toplevel.dialog_asset(DialogBIN.DIALOG_ASSET_BUTTON_MID_DISABLED_MIDDLE)
						right = self.toplevel.dialog_asset(DialogBIN.DIALOG_ASSET_BUTTON_MID_DISABLED_RIGHT)
					if left and mid and right:
						width = x2-x1
						height = 0
						for img in (left,mid,right):
							height = max(height, img.size[1])
						mid_y = height / 2
						pil = PILImage.new('RGBA', (width,height))
						pil.paste(left, (0,mid_y - left.size[1]/2))
						pad_size = width-left.size[0]-right.size[0]
						if pad_size > 0:
							pad = mid.resize((pad_size,mid.size[1]))
							pil.paste(pad, (left.size[0],mid_y - pad.size[1]/2))
						pil.paste(right, (width-right.size[0],mid_y - right.size[1]/2))
						self.dialog_image = ImageTk.PhotoImage(pil)
						y += (y2 - y1) / 2
						anchor = W
				elif self.widget.type == DialogBIN.BINWidget.TYPE_LISTBOX:
					top = self.toplevel.dialog_asset(DialogBIN.DIALOG_ASSET_SCROLL_VERTICAL_TOP)
					mid = self.toplevel.dialog_asset(DialogBIN.DIALOG_ASSET_SCROLL_VERTICAL_MIDDLE)
					bot = self.toplevel.dialog_asset(DialogBIN.DIALOG_ASSET_SCROLL_VERTICAL_BOTTOM)
					bar = self.toplevel.dialog_asset(DialogBIN.DIALOG_ASSET_SCROLL_BAR)
					if self.enabled():
						up = self.toplevel.dialog_asset(DialogBIN.DIALOG_ASSET_SCROLL_UP)
						down = self.toplevel.dialog_asset(DialogBIN.DIALOG_ASSET_SCROLL_DOWN)
					else:
						up = self.toplevel.dialog_asset(DialogBIN.DIALOG_ASSET_SCROLL_UP_DISABLED)
						down = self.toplevel.dialog_asset(DialogBIN.DIALOG_ASSET_SCROLL_DOWN_DISABLED)
					imgs = (top,mid,bot,bar,up,down)
					if not None in imgs:
						width = 0
						height = y2-y1
						for img in imgs:
							width = max(width, img.size[0])
						mid_x = width / 2
						pil = PILImage.new('RGBA', (width,height))
						pil.paste(up, (mid_x-up.size[0]/2,0))
						pil.paste(top, (mid_x-top.size[0]/2,up.size[1]+2))
						mid_height = height - up.size[1] - 2 - top.size[1] - bot.size[1] - 2 - down.size[1]
						if mid_height > 0:
							mid_full = mid.resize((mid.size[0],mid_height))
							pil.paste(mid_full, (mid_x-mid.size[0]/2,up.size[1]+2+top.size[1]))
						pil.paste(bot, (mid_x-bot.size[0]/2,height-down.size[1]-2-bot.size[1]))
						pil.paste(down, (mid_x-down.size[0]/2,height-down.size[1]))
						pil.paste(bar, (mid_x-bar.size[0]/2,up.size[1]+4))
						self.dialog_image = ImageTk.PhotoImage(pil)
						x = x2
						y += (y2 - y1) / 2
						anchor = E
				elif self.widget.type == DialogBIN.BINWidget.TYPE_COMBOBOX:
					left = self.toplevel.dialog_asset(DialogBIN.DIALOG_ASSET_COMBOBOX_LEFT)
					middle = self.toplevel.dialog_asset(DialogBIN.DIALOG_ASSET_COMBOBOX_MIDDLE)
					right = self.toplevel.dialog_asset(DialogBIN.DIALOG_ASSET_COMBOBOX_RIGHT)
					if self.enabled():
						arrow = self.toplevel.dialog_asset(DialogBIN.DIALOG_ASSET_COMBOBOX_ARROW)
					else:
						arrow = self.toplevel.dialog_asset(DialogBIN.DIALOG_ASSET_COMBOBOX_ARROW_DISABLED)
					imgs = (left,middle,right,arrow)
					if not None in imgs:
						width = x2-x1
						height = 0
						for img in imgs:
							height = max(height, img.size[1])
						mid_y = height / 2
						pil = PILImage.new('RGBA', (width,height))
						pil.paste(left, (0,mid_y - left.size[1]/2))
						pad_size = width-left.size[0]-right.size[0]
						if pad_size > 0:
							pad = middle.resize((pad_size,middle.size[1]))
							pil.paste(pad, (left.size[0],mid_y - pad.size[1]/2))
						pil.paste(right, (width-right.size[0],mid_y - right.size[1]/2))
						pil.paste(arrow, (width-arrow.size[0]-5,mid_y - arrow.size[1]/2))
						self.dialog_image = ImageTk.PhotoImage(pil)
						y += (y2 - y1) / 2
						anchor = W
				elif self.widget.type == DialogBIN.BINWidget.TYPE_DIALOG and self.toplevel.show_dialog.get():
					tl = self.toplevel.dialog_frame(DialogBIN.DIALOG_FRAME_TL)
					t = self.toplevel.dialog_frame(DialogBIN.DIALOG_FRAME_T)
					tr = self.toplevel.dialog_frame(DialogBIN.DIALOG_FRAME_TR)
					l = self.toplevel.dialog_frame(DialogBIN.DIALOG_FRAME_L)
					m = self.toplevel.dialog_frame(DialogBIN.DIALOG_FRAME_M)
					r = self.toplevel.dialog_frame(DialogBIN.DIALOG_FRAME_R)
					bl = self.toplevel.dialog_frame(DialogBIN.DIALOG_FRAME_BL)
					b = self.toplevel.dialog_frame(DialogBIN.DIALOG_FRAME_B)
					br = self.toplevel.dialog_frame(DialogBIN.DIALOG_FRAME_BR)
					if not None in (tl,t,tr,l,m,r,bl,b,br):
						width = x2-x1
						height = y2-y1
						i_width = width-tl.size[0]-tr.size[0]
						i_height = height-tl.size[1]-bl.size[1]
						pil = PILImage.new('RGBA', (width,height))
						pil.paste(tl, (0,0))
						if i_width > 0:
							t_full = t.resize((i_width,t.size[1]))
							pil.paste(t_full, (tl.size[0],0))
						pil.paste(tr, (width-tr.size[0],0))
						if i_height > 0:
							l_full = l.resize((l.size[0],i_height))
							pil.paste(l_full, (0,tl.size[1]))
							if i_width > 0:
								m_full = m.resize((i_width,i_height))
								pil.paste(m_full, tl.size)
							r_full = r.resize((r.size[0],i_height))
							pil.paste(r_full, (width-r.size[0],tr.size[1]))
						pil.paste(bl, (0,height-bl.size[1]))
						if i_width > 0:
							b_full = b.resize((i_width,b.size[1]))
							pil.paste(b_full, (bl.size[0],height-b.size[1]))
						pil.paste(br, (width-br.size[0],height-br.size[1]))
						self.dialog_image = ImageTk.PhotoImage(pil)
				if self.dialog_image:
					if self.item_dialog:
						self.toplevel.widgetCanvas.itemconfigure(self.item_dialog, image=self.dialog_image)
						self.toplevel.widgetCanvas.coords(self.item_dialog, x,y)
					else:
						self.item_dialog = self.toplevel.widgetCanvas.create_image(x,y, image=self.dialog_image, anchor=anchor)
						reorder = True
		if self.dialog_image == None and self.item_dialog:
			self.toplevel.widgetCanvas.delete(self.item_dialog)
			self.item_dialog = None
		return reorder

	def tick(self, dt):
		SHOW_SMKS = self.toplevel.show_smks.get()
		SHOW_ANIMATED = self.toplevel.show_animated.get()
		if SHOW_SMKS and SHOW_ANIMATED and self.smks:
			self.frame_waited += dt
			if self.frame_waited > self.frame_delay:
				for smk in self.smks.values():
					if smk.current_frame < smk.frames or self.widget.smk.flags & DialogBIN.BINSMK.FLAG_REPEATS:
						# while self.frame_waited > self.frame_delay:
							smk.next_frame()
							# self.frame_waited -= self.frame_delay
				self.frame_waited = 0
	def update_video(self):
		reorder = False
		SHOW_SMKS = self.toplevel.show_smks.get()
		SHOW_HOVER_SMKS = self.toplevel.show_hover_smks.get()
		showing = []
		if SHOW_SMKS and self.widget and self.widget.type == DialogBIN.BINWidget.TYPE_HIGHLIGHT_BTN and self.widget.smk and self.visible():
			if self.smks == None:
				self.smks = {}
			check = self.widget.smk
			while check:
				if not check.flags & DialogBIN.BINSMK.FLAG_SHOW_ON_HOVER or SHOW_HOVER_SMKS:
					if not check.filename in self.smks:
						try:
							smk = SMK.SMK()
							smk.load_file(self.toplevel.mpqhandler.get_file('MPQ:' + check.filename))
							delay = int(1000 / float(smk.fps))
							if self.frame_delay == None:
								self.frame_delay = delay
							else:
								self.frame_delay = min(self.frame_delay,delay)
							self.smks[check.filename] = smk
						except:
							InternalErrorDialog.capture(self, 'PyBIN')
					smk = self.smks.get(check.filename)
					if smk:
						showing.append((check,smk))
				check = check.overlay_smk
		while len(self.item_smks) > len(showing):
			self.toplevel.widgetCanvas.delete(self.item_smks[-1])
			del self.item_smks[-1]
		for i,(bin_smk,smk) in enumerate(showing):
			frame = smk.get_frame()
			# trans = ((self.widget.flags & DialogBIN.BINWidget.FLAG_TRANSPARENCY) == DialogBIN.BINWidget.FLAG_TRANSPARENCY)
			trans = False
			if bin_smk.filename in WidgetNode.SMK_FRAME_CACHE and smk.current_frame in WidgetNode.SMK_FRAME_CACHE[bin_smk.filename]:
				image = WidgetNode.SMK_FRAME_CACHE[bin_smk.filename][smk.current_frame]
			else:
				image = GRP.frame_to_photo(frame.palette, frame.image, None, size=False, trans=trans)
				if not bin_smk.filename in WidgetNode.SMK_FRAME_CACHE:
					WidgetNode.SMK_FRAME_CACHE[bin_smk.filename] = {}
				WidgetNode.SMK_FRAME_CACHE[bin_smk.filename][smk.current_frame] = image
			x1,y1,x2,y2 = self.widget.bounding_box()
			x1 += bin_smk.offset_x
			y1 += bin_smk.offset_y
			if i < len(self.item_smks):
				self.toplevel.widgetCanvas.itemconfigure(self.item_smks[i], image=image)
				self.toplevel.widgetCanvas.coords(self.item_smks[i], x1,y1)
			else:
				item = self.toplevel.widgetCanvas.create_image(x1,y1, image=image, anchor=NW)
				self.item_smks.append(item)
				# self.toplevel.widgetCanvas.create_rectangle(x1,y1,x1+self.smk.width,y1+self.smk.height, width=1, outline='#FFFF00')
				reorder = True
		return reorder

	def update_image(self):
		reorder = False
		SHOW_IMAGES = self.toplevel.show_images.get()
		if SHOW_IMAGES and self.widget and self.widget.type == DialogBIN.BINWidget.TYPE_IMAGE and self.visible() and self.widget.string:
			photo_change = False
			if self.photo == None:
				try:
					pcx = PCX.PCX()
					pcx.load_file(self.toplevel.mpqhandler.get_file('MPQ:' + self.widget.string))
					trans = ((self.widget.flags & DialogBIN.BINWidget.FLAG_TRANSPARENCY) == DialogBIN.BINWidget.FLAG_TRANSPARENCY)
					self.photo = GRP.frame_to_photo(pcx.palette, pcx, -1, size=False, trans=trans)
					photo_change = True
				except:
					InternalErrorDialog.capture(self, 'PyBIN')
			if self.photo:
				x1,y1,x2,y2 = self.bounding_box()
				if self.item_image:
					if photo_change:
						self.toplevel.widgetCanvas.itemconfigure(self.item_image, image=self.photo)
					self.toplevel.widgetCanvas.coords(self.item_image, x1,y1)
				else:
					self.item_image = self.toplevel.widgetCanvas.create_image(x1,y1, image=self.photo, anchor=NW)
					reorder = True
		elif self.item_image:
			self.toplevel.widgetCanvas.delete(self.item_image)
			self.item_image = None
		return reorder

	def update_text(self):
		reorder = False
		SHOW_TEXT = self.toplevel.show_text.get()
		if SHOW_TEXT and self.widget and self.widget.display_text() and self.visible():
			if self.string == None:
				if self.widget.flags & DialogBIN.BINWidget.FLAG_FONT_SIZE_10:
					font = self.toplevel.font10
				elif self.widget.flags & DialogBIN.BINWidget.FLAG_FONT_SIZE_14:
					font = self.toplevel.font14
				elif self.widget.flags & DialogBIN.BINWidget.FLAG_FONT_SIZE_16:
					font = self.toplevel.font16
				elif self.widget.flags & DialogBIN.BINWidget.FLAG_FONT_SIZE_16x:
					font = self.toplevel.font16x
				else:
					font = self.toplevel.font10
				remap_pal = self.toplevel.tfont
				remap = FNT.COLOR_CODES_INGAME
				if self.toplevel.tfont:
					remap_pal = self.toplevel.tfont
					remap = FNT.COLOR_CODES_GLUE
				default_color = 2
				if self.widget.type in (DialogBIN.BINWidget.TYPE_BUTTON,DialogBIN.BINWidget.TYPE_COMBOBOX,DialogBIN.BINWidget.TYPE_DEFAULT_BTN,DialogBIN.BINWidget.TYPE_OPTION_BTN,DialogBIN.BINWidget.TYPE_HIGHLIGHT_BTN):
					default_color = 3
				self.string = StringPreview(self.widget.display_text(), font, self.toplevel.tfontgam, remap, remap_pal, default_color)
			x1,y1,x2,y2 = self.text_box()
			align = self.widget.flags
			if self.widget.type == DialogBIN.BINWidget.TYPE_LABEL_LEFT_ALIGN:
				align = 0
			elif self.widget.type == DialogBIN.BINWidget.TYPE_LABEL_CENTER_ALIGN:
				align = DialogBIN.BINWidget.FLAG_TEXT_ALIGN_CENTER
			elif self.widget.type == DialogBIN.BINWidget.TYPE_LABEL_RIGHT_ALIGN:
				align = DialogBIN.BINWidget.FLAG_TEXT_ALIGN_RIGHT
			elif self.widget.type in (DialogBIN.BINWidget.TYPE_BUTTON,DialogBIN.BINWidget.TYPE_DEFAULT_BTN):
				align = DialogBIN.BINWidget.FLAG_TEXT_ALIGN_CENTER | DialogBIN.BINWidget.FLAG_ALIGN_MIDDLE
			elif self.widget.type in (DialogBIN.BINWidget.TYPE_CHECKBOX, DialogBIN.BINWidget.TYPE_OPTION_BTN):
				align = DialogBIN.BINWidget.FLAG_ALIGN_MIDDLE
			positions = self.string.get_positions(x1,y1, x2,y2, align_flags=align)
			if self.item_string_images:
				for item,position in zip(self.item_string_images,positions):
					self.toplevel.widgetCanvas.coords(item, *position)
			else:
				self.item_string_images = []
				glyphs = self.string.get_glyphs()
				for glyph,position in zip(glyphs,positions):
					self.item_string_images.append(self.toplevel.widgetCanvas.create_image(position[0],position[1], image=glyph, anchor=NW))
				reorder = True
		elif self.item_string_images:
			for item in self.item_string_images:
				self.toplevel.widgetCanvas.delete(item)
			self.item_string_images = None
		return reorder

	def update_bounds(self):
		reorder = False
		SHOW_BOUNDING_BOX = self.toplevel.show_bounds_widget.get()
		SHOW_GROUP_BOUNDS = self.toplevel.show_bounds_group.get()
		if SHOW_BOUNDING_BOX and (self.widget or SHOW_GROUP_BOUNDS):
			x1,y1,x2,y2 = self.bounding_box()
			if self.item_bounds:
				self.toplevel.widgetCanvas.coords(self.item_bounds, x1,y1, x2,y2)
			else:
				color = '#505050'
				if self.widget:
					color = '#0080ff'
					if self.widget.type == DialogBIN.BINWidget.TYPE_DIALOG:
						color = '#00A0A0'
				self.item_bounds = self.toplevel.widgetCanvas.create_rectangle(x1,y1, x2,y2, width=1, outline=color)
				reorder = True
		elif self.item_bounds:
			self.toplevel.widgetCanvas.delete(self.item_bounds)
			self.item_bounds = None
		return reorder

	def update_text_bounds(self):
		reorder = False
		SHOW_TEXT_BOUNDS = self.toplevel.show_bounds_text.get()
		if SHOW_TEXT_BOUNDS and self.widget and self.widget.display_text() != None:
			x1,y1,x2,y2 = self.text_box()
			if self.item_text_bounds:
				self.toplevel.widgetCanvas.coords(self.item_text_bounds, x1,y1, x2,y2)
			else:
				self.item_text_bounds = self.toplevel.widgetCanvas.create_rectangle(x1,y1, x2,y2, width=1, outline='#F0F0F0')
				reorder = True
		elif self.item_text_bounds:
			self.toplevel.widgetCanvas.delete(self.item_text_bounds)
			self.item_text_bounds = None
		return reorder

	def update_responsive_bounds(self):
		reorder = False
		SHOW_RESPONSIVE_BOUNDS = self.toplevel.show_bounds_responsive.get()
		if SHOW_RESPONSIVE_BOUNDS and self.widget and self.widget.has_responsive():
			x1,y1,x2,y2 = self.widget.responsive_box()
			if self.item_responsive_bounds:
				self.toplevel.widgetCanvas.coords(self.item_responsive_bounds, x1,y1, x2,y2)
			else:
				self.item_responsive_bounds = self.toplevel.widgetCanvas.create_rectangle(x1,y1, x2,y2, width=1, outline='#00ff80')
				reorder = True
		elif self.item_responsive_bounds:
			self.toplevel.widgetCanvas.delete(self.item_responsive_bounds)
			self.item_responsive_bounds = None
		return reorder

	def update_display(self):
		reorder = False
		reorder = self.update_dialog() or reorder
		reorder = self.update_image() or reorder
		reorder = self.update_video() or reorder
		reorder = self.update_text() or reorder
		reorder = self.update_bounds() or reorder
		reorder = self.update_text_bounds() or reorder
		reorder = self.update_responsive_bounds() or reorder
		return reorder

	def lift(self):
		if self.item_dialog:
			self.toplevel.widgetCanvas.lift(self.item_dialog)
		if self.item_image:
			self.toplevel.widgetCanvas.lift(self.item_image)
		if self.item_smks:
			for item in self.item_smks:
				self.toplevel.widgetCanvas.lift(item)
		if self.item_string_images:
			for item in self.item_string_images:
				self.toplevel.widgetCanvas.lift(item)
		if self.item_bounds:
			self.toplevel.widgetCanvas.lift(self.item_bounds)
		if self.item_text_bounds:
			self.toplevel.widgetCanvas.lift(self.item_text_bounds)
		if self.item_responsive_bounds:
			self.toplevel.widgetCanvas.lift(self.item_responsive_bounds)

	def remove_display(self):
		if self.item_dialog:
			self.toplevel.widgetCanvas.delete(self.item_dialog)
			self.item_dialog = None
		if self.item_image:
			self.toplevel.widgetCanvas.delete(self.item_image)
			self.item_image = None
		if self.item_smks:
			for item in self.item_smks:
				self.toplevel.widgetCanvas.delete(item)
			self.item_smks = []
		if self.item_string_images:
			for item in self.item_string_images:
				self.toplevel.widgetCanvas.delete(item)
			self.item_string_images = []
		if self.item_bounds:
			self.toplevel.widgetCanvas.delete(self.item_bounds)
			self.item_bounds = None
		if self.item_text_bounds:
			self.toplevel.widgetCanvas.delete(self.item_text_bounds)
			self.item_text_bounds = None
		if self.item_responsive_bounds:
			self.toplevel.widgetCanvas.delete(self.item_responsive_bounds)
			self.item_responsive_bounds = None

class PyBIN(Tk):
	def __init__(self, guifile=None):

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
		ga.set_application('PyBIN', VERSIONS['PyBIN'])
		ga.track(GAScreen('PyBIN'))
		setup_trace(self, 'PyBIN')

		self.bin = None
		self.file = None
		self.edited = False
		self.dialog = None
		self.widget_map = None

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
			None,
			('Group',-1),
		)
		for info in fields:
			if info:
				self.type_menu.add_command(label=info[0], command=lambda t=info[1]: self.add_new_node(t))
			else:
				self.type_menu.add_separator()

		frame = Frame(self)
		leftframe = Frame(frame)
		Label(leftframe, text='Widgets:', anchor=W).grid(row=0, column=0, sticky=EW)
		self.widgetTree = TreeList(leftframe)
		self.widgetTree.grid(row=1, column=0, padx=1, pady=1, sticky=NSEW)
		self.widgetTree.bind('<Button-1>', self.list_select)
		self.widgetTree.bind('<B1-Motion>', self.list_drag)
		self.widgetTree.bind('<ButtonRelease-1>', self.list_drop)
		self.widgetTree.bind('<Double-Button-1>', self.list_double_click)
		f = Frame(leftframe)
		buttons = (
			('add', self.add_node, 0, 20, 20, DISABLED),
			('remove', self.remove_node, 0, 20, 20, DISABLED),
			('edit', lambda: self.edit_node_settings(), 0, 20, 20, DISABLED),
			('arrow', self.toggle_preview_settings, 1, 20, 10, NORMAL),
			('down', lambda: self.move_node(-1), 0, 20, 20, DISABLED),
			('up', lambda: self.move_node(2), 0, 20, 20, DISABLED)
		)
		for col,(icon,callback,weight,width,height,state) in enumerate(buttons):
			image = PhotoImage(file=os.path.join(BASE_DIR,'Images','%s.gif' % icon))
			button = Button(f, image=image, width=width, height=height, command=callback, state=state)
			button.image = image
			if icon == 'arrow':
				image = PhotoImage(file=os.path.join(BASE_DIR,'Images','%sup.gif' % icon))
				button.image_up = image
				if not self.show_preview_settings.get():
					button.config(image=button.image_up)
			# button.tooltip = Tooltip(button, btn[1])
			button.grid(row=0,column=col, sticky=S)
			f.grid_columnconfigure(col, weight=weight)
			self.buttons[icon] = button
		f.grid(row=2, column=0, padx=1, pady=1, sticky=EW)

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
		for t in xrange(DialogBIN.THEME_ASSETS_MAIN_MENU,DialogBIN.THEME_ASSETS_NONE):
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
		self.widgetCanvas.bind('<Motion>', self.mouse_motion)
		self.widgetCanvas.bind('<Leave>', lambda e: self.edit_status.set(''))
		self.widgetCanvas.bind('<Double-Button-1>', lambda e,m=0: self.canvas_double_click(e,m))
		self.widgetCanvas.bind('<Control-Double-Button-1>', lambda e,m=MODIFIER_CTRL: self.canvas_double_click(e,m))
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

		self.bind('<Return>', self.list_double_click)

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

		self.update_idletasks()
		w,h,_,_,_ = parse_geometry(self.winfo_geometry())
		self.minsize(w,h)
		PYBIN_SETTINGS.windows.load_window_size('main', self)

		self.mpqhandler = MPQHandler(PYBIN_SETTINGS.settings.get('mpqs',[]))
		if not len(self.mpqhandler.mpqs) and self.mpqhandler.add_defaults():
			PYBIN_SETTINGS.settings.mpqs = self.mpqhandler.mpqs
		e = self.open_files()

		if guifile:
			self.open(file=guifile)

		start_new_thread(check_update, (self, 'PyBIN'))

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

	def toggle_preview_settings(self):
		show = not self.show_preview_settings.get()
		self.show_preview_settings.set(show)
		if show:
			self.buttons['arrow'].config(image=self.buttons['arrow'].image)
			self.preview_settings_frame.grid()
		else:
			self.buttons['arrow'].config(image=self.buttons['arrow'].image_up)
			self.preview_settings_frame.grid_remove()

	def add_node(self):
		self.type_menu.post(*self.winfo_pointerxy())

	def add_new_node(self, ctrl_type):
		parent = self.dialog
		index = 0
		if self.selected_node:
			if self.selected_node.children:
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
			node = WidgetNode(self, widget)
		parent.add_child(node, index)
		self.reload_list()
		self.reload_canvas()
		self.select_node(node)

	def remove_node(self):
		self.selected_node.remove_display()
		if self.selected_node.widget:
			self.bin.widgets.remove(self.selected_node.widget)
		self.selected_node.remove_from_parent()
		self.selected_node = None
		self.update_selection_box()
		self.reload_list()

	def move_node(self, delta):
		index = self.selected_node.parent.children.index(self.selected_node)
		dest = index + delta
		if 0 <= dest <= len(self.selected_node.parent.children):
			self.selected_node.parent.children.insert(dest, self.selected_node)
			del self.selected_node.parent.children[index + (dest < index)]
			self.reload_list()
			self.action_states()
			self.update_zorder()

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
				self.background_image = GRP.frame_to_photo(background.palette, background, -1, size=False)
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
		if self.bin:
			for widget in self.flattened_nodes():
				pass
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
		if self.bin:
			for widget in self.flattened_nodes():
				pass
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
		if index != PYBIN_SETTINGS.preview.get('theme_id'):
			PYBIN_SETTINGS.preview.theme_id = index
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

			tfontgam.load_file(self.mpqhandler.get_file(PYBIN_SETTINGS.settings.files.get('tfontgam', 'MPQ:game\\tfontgam.pcx')))
			path = PYBIN_SETTINGS.settings.files.get('font10', 'MPQ:font\\font10.fnt')
			try:
				font10.load_file(self.mpqhandler.get_file(path, False))
			except:
				font10.load_file(self.mpqhandler.get_file(path, True))
			path = PYBIN_SETTINGS.settings.files.get('font14', 'MPQ:font\\font14.fnt')
			try:
				font14.load_file(self.mpqhandler.get_file(path, False))
			except:
				font14.load_file(self.mpqhandler.get_file(path, True))
			path = PYBIN_SETTINGS.settings.files.get('font16', 'MPQ:font\\font16.fnt')
			try:
				font16.load_file(self.mpqhandler.get_file(path, False))
			except:
				font16.load_file(self.mpqhandler.get_file(path, True))
			path = PYBIN_SETTINGS.settings.files.get('font16x', 'MPQ:font\\font16x.fnt')
			try:
				font16x.load_file(self.mpqhandler.get_file(path, False))
			except:
				font16x.load_file(self.mpqhandler.get_file(path, True))
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
		SettingsDialog(self, data, (340,430), err, settings=PYBIN_SETTINGS)

	def scroll(self, e):
		if e.delta > 0:
			self.listbox.yview('scroll', -2, 'units')
		else:
			self.listbox.yview('scroll', 2, 'units')

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

	def action_states(self):
		isopen = [NORMAL,DISABLED][not self.bin]
		for btn in ['save','saveas','export','close','add']:
			self.buttons[btn]['state'] = isopen
		hassel = (self.selected_node != None)
		isdialog = (hassel and self.selected_node.widget and self.selected_node.widget.type == DialogBIN.BINWidget.TYPE_DIALOG)
		self.buttons['remove']['state'] = [DISABLED,NORMAL][(hassel and not isdialog)]
		self.buttons['edit']['state'] = [DISABLED,NORMAL][hassel]
		canmove = (hassel and not not self.selected_node.parent)
		index = 0
		if canmove:
			index = self.selected_node.parent.children.index(self.selected_node)
		self.buttons['up']['state'] = [DISABLED,NORMAL][(canmove and index > 0)]
		self.buttons['down']['state'] = [DISABLED,NORMAL][(canmove and index < len(self.selected_node.parent.children)-1)]

	def edit(self, n=None):
		self.edited = True
		self.editstatus['state'] = NORMAL
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
		PYBIN_SETTINGS.preview[setting_name] = variable.get()
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
			self.title('PyBIN %s (Unnamed.bin)' % LONG_VERSION)
			self.edited = False
			self.editstatus['state'] = DISABLED
			self.action_states()
			self.tick(True)

	def open(self, key=None, file=None):
		if not self.unsaved():
			if file == None:
				file = PYBIN_SETTINGS.lastpath.bin.select_file('open', self, 'Open Dialog BIN', '.bin', [('StarCraft Dialogs','*.bin'),('All Files','*')])
				if not file:
					return
			dbin = DialogBIN.DialogBIN()
			try:
				dbin.load_file(file)
			except PyMSError, e:
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
			self.title('PyBIN %s (%s)' % (LONG_VERSION,file))
			self.file = file
			self.status.set('Load Successful!')
			self.edited = False
			self.editstatus['state'] = DISABLED
			self.select_node(self.dialog)
			self.action_states()
			self.tick(True)

	def iimport(self, key=None):
		if not self.unsaved():
			file = PYBIN_SETTINGS.lastpath.txt.select_file('import', self, 'Import TXT', '*.txt', [('Text Files','*.txt'),('All Files','*')])
			if not file:
				return
			dbin = DialogBIN.DialogBIN()
			try:
				dbin.interpret_file(file)
			except PyMSError, e:
				ErrorDialog(self, e)
				return
			self.clear()
			self.bin = dbin
			self.title('PyBIN %s (%s)' % (LONG_VERSION,file))
			self.file = file
			self.status.set('Import Successful!')
			self.edited = False
			self.editstatus['state'] = DISABLED
			self.action_states()
			self.tick(True)

	def save(self, key=None):
		if key and self.buttons['save']['state'] != NORMAL:
			return
		if self.file == None:
			self.saveas()
			return
		try:
			self.bin.save_file(self.file)
			self.status.set('Save Successful!')
			self.edited = False
			self.editstatus['state'] = DISABLED
		except PyMSError, e:
			ErrorDialog(self, e)

	def saveas(self, key=None):
		if key and self.buttons['saveas']['state'] != NORMAL:
			return
		file = PYBIN_SETTINGS.lastpath.bin.select_file('save', self, 'Save Dialog BIN As', '.bin', [('StarCraft Dialogs','*.bin'),('All Files','*')], save=True)
		if not file:
			return True
		self.file = file
		self.save()

	def export(self, key=None):
		if key and self.buttons['export']['state'] != NORMAL:
			return
		file = PYBIN_SETTINGS.lastpath.txt.select_file('export', self, 'Export TXT', '*.txt', [('Text Files','*.txt'),('All Files','*')], save=True)
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
			self.clear()
			self.title('PyBIN %s' % LONG_VERSION)
			self.status.set('Load or create a Dialog BIN.')
			self.editstatus['state'] = DISABLED
			self.action_states()

	def register(self, e=None):
		try:
			register_registry('PyBIN','','bin',os.path.join(BASE_DIR, 'PyBIN.pyw'),os.path.join(BASE_DIR,'Images','PyGOT.ico'))
		except PyMSError, e:
			ErrorDialog(self, e)

	def help(self, e=None):
		webbrowser.open('file:///%s' % os.path.join(BASE_DIR, 'Docs', 'PyBIN.html'))

	def about(self, key=None):
		AboutDialog(self, 'PyBIN', LONG_VERSION, [
			('FaRTy1billion','File Specs and BinEdit2')
		])

	def load_settings(self):
		self.show_preview_settings.set(PYBIN_SETTINGS.preview.get('show_settings',True))
		self.show_images.set(PYBIN_SETTINGS.preview.get('show_images',True))
		self.show_text.set(PYBIN_SETTINGS.preview.get('show_text',True))
		self.show_smks.set(PYBIN_SETTINGS.preview.get('show_smks',True))
		self.show_hidden.set(PYBIN_SETTINGS.preview.get('show_hidden',True))
		self.show_dialog.set(PYBIN_SETTINGS.preview.get('show_dialog',False))
		self.show_animated.set(PYBIN_SETTINGS.preview.get('show_animated',False))
		self.show_hover_smks.set(PYBIN_SETTINGS.preview.get('show_hover_smks',False))
		self.show_background.set(PYBIN_SETTINGS.preview.get('show_background',False))
		self.show_theme_index.set(PYBIN_SETTINGS.preview.get('theme_id',-1) + 1)
		self.show_bounds_widget.set(PYBIN_SETTINGS.preview.get('show_bounds_widget',True))
		self.show_bounds_group.set(PYBIN_SETTINGS.preview.get('show_bounds_group',True))
		self.show_bounds_text.set(PYBIN_SETTINGS.preview.get('show_bounds_text',True))
		self.show_bounds_responsive.set(PYBIN_SETTINGS.preview.get('show_bounds_responsive',True))

	def save_settings(self):
		PYBIN_SETTINGS.preview.show_settings = self.show_preview_settings.get()
		PYBIN_SETTINGS.preview.show_images = self.show_images.get()
		PYBIN_SETTINGS.preview.show_text = self.show_text.get()
		PYBIN_SETTINGS.preview.show_smks = self.show_smks.get()
		PYBIN_SETTINGS.preview.show_hidden = self.show_hidden.get()
		PYBIN_SETTINGS.preview.show_dialog = self.show_dialog.get()
		PYBIN_SETTINGS.preview.show_animated = self.show_animated.get()
		PYBIN_SETTINGS.preview.show_hover_smks = self.show_hover_smks.get()
		PYBIN_SETTINGS.preview.show_background = self.show_background.get()
		PYBIN_SETTINGS.preview.theme_id = self.show_theme_index.get()-1
		PYBIN_SETTINGS.preview.show_bounds_widget = self.show_bounds_widget.get()
		PYBIN_SETTINGS.preview.show_bounds_group = self.show_bounds_group.get()
		PYBIN_SETTINGS.preview.show_bounds_text = self.show_bounds_text.get()
		PYBIN_SETTINGS.preview.show_bounds_responsive = self.show_bounds_responsive.get()

	def exit(self, e=None):
		if not self.unsaved():
			PYBIN_SETTINGS.windows.save_window_size('main', self)
			self.save_settings()
			PYBIN_SETTINGS.save()
			self.stop_tick()
			self.destroy()

def main():
	import sys
	if not sys.argv or (len(sys.argv) == 1 and os.path.basename(sys.argv[0]).lower() in ['','pybin.py','pybin.pyw','pybin.exe']):
		gui = PyBIN()
		startup(gui)
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