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

EDIT_NONE = 0
EDIT_MOVE = 1
EDIT_RESIZE_LEFT = 2
EDIT_RESIZE_TOP = 3
EDIT_RESIZE_RIGHT = 4
EDIT_RESIZE_BOTTOM = 5

MODIFIER_SHIFT = 1
MODIFIER_CTRL = 2

class WidgetSettings(PyMSDialog):
	def __init__(self, parent, node):
		self.node = node

		self.advanced_widgets = []
		self.advanced_shown = True
		self.show_advanced = BooleanVar()
		self.show_advanced.set(parent.settings.get('advanced_widget_editor',False))

		self.left = IntegerVar(range=[0,65535])
		self.right = IntegerVar(range=[0,65535])
		self.width = IntegerVar(range=[0,65535])
		self.top = IntegerVar(range=[0,65535])
		self.bottom = IntegerVar(range=[0,65535])
		self.height = IntegerVar(range=[0,65535])
		self.string = StringVar()
		self.identifier = IntegerVar(range=[0,65535])
		self.text_offset_x = IntegerVar(range=[0,65535])
		self.text_offset_y = IntegerVar(range=[0,65535])
		self.responsive_left = IntegerVar(range=[0,65535])
		self.responsive_right = IntegerVar(range=[0,65535])
		self.responsive_width = IntegerVar(range=[0,65535])
		self.responsive_top = IntegerVar(range=[0,65535])
		self.responsive_bottom = IntegerVar(range=[0,65535])
		self.responsive_height = IntegerVar(range=[0,65535])

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
		self.flag_no_click_soung = BooleanVar()
		self.flag_unk10 = BooleanVar()

		self.load_settings()

		PyMSDialog.__init__(self, parent, 'Edit ' + DialogBIN.BINWidget.TYPE_NAMES[node.widget.type])

	def update_advanced(self):
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

	def calculate(self, calc, orig, offset, direction, fix):
		calc.set(orig.get() + offset.get() * direction + fix)

	def widgetize(self):
		self.resizable(False, False)
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
		horframe.grid(row=3,column=2, padx=3,pady=3, sticky=N)
		verframe = LabelFrame(stringframe, text="Vertical")
		Checkbutton(verframe, text='Top', variable=self.flag_align_top).grid(row=0,column=0, sticky=W)
		Checkbutton(verframe, text='Middle', variable=self.flag_align_middle).grid(row=1,column=0, sticky=W)
		Checkbutton(verframe, text='Right', variable=self.flag_align_bottom).grid(row=2,column=0, sticky=W)
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
		isdialog = self.node.widget.type == DialogBIN.BINWidget.TYPE_DIALOG
		if isimage or isdialog:
			self.advanced_widgets.extend((offsetframe,hotkeyframe,horframe,verframe,fontframe))
		if not isimage or isdialog:
			self.advanced_widgets.extend((transparent,findimage))

		bottom = Frame(self)
		ok = Button(bottom, text='Ok', width=10, command=self.ok)
		ok.pack(side=LEFT, padx=1, pady=3)
		Button(bottom, text='Update Preview', width=15, command=self.update_preview).pack(side=LEFT, padx=3, pady=3)
		Checkbutton(bottom, text='Advanced', variable=self.show_advanced, command=self.update_advanced).pack(side=RIGHT, padx=1, pady=3)
		bottom.grid(row=2,column=0, columnspan=2, pady=3, padx=3, sticky=EW)
		self.update_advanced()
		return ok

	def load_settings(self):
		self.left.set(self.node.widget.x1)
		self.right.set(self.node.widget.x2)
		self.width.set(self.node.widget.width)
		self.top.set(self.node.widget.y1)
		self.bottom.set(self.node.widget.y2)
		self.height.set(self.node.widget.height)
		self.string.set(TBL.decompile_string(self.node.widget.string))
		self.identifier.set(self.node.widget.identifier)
		self.text_offset_x.set(self.node.widget.text_offset_x)
		self.text_offset_y.set(self.node.widget.text_offset_y)
		self.responsive_left.set(self.node.widget.responsive_x1)
		self.responsive_right.set(self.node.widget.responsive_x2)
		self.responsive_width.set(self.node.widget.responsive_width)
		self.responsive_top.set(self.node.widget.responsive_y1)
		self.responsive_bottom.set(self.node.widget.responsive_y2)
		self.responsive_height.set(self.node.widget.responsive_height)

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
		self.flag_no_click_soung.set((self.node.widget.flags & DialogBIN.BINWidget.FLAG_NO_CLICK_SOUNG == DialogBIN.BINWidget.FLAG_NO_CLICK_SOUNG))
		self.flag_unk10.set((self.node.widget.flags & DialogBIN.BINWidget.FLAG_UNK10 == DialogBIN.BINWidget.FLAG_UNK10))

	def save_settings(self):
		self.node.widget.x1 = self.left.get()
		self.node.widget.x2 = self.right.get()
		self.node.widget.width = self.width.get()
		self.node.widget.y1 = self.top.get()
		self.node.widget.y2 = self.bottom.get()
		self.node.widget.height = self.height.get()
		self.node.widget.string = TBL.compile_string(self.string.get())
		self.node.widget.identifier = self.identifier.get()
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
		self.node.widget.flags |= self.flag_no_click_soung.get() * DialogBIN.BINWidget.FLAG_NO_CLICK_SOUNG
		self.node.widget.flags |= self.flag_unk10.get() * DialogBIN.BINWidget.FLAG_UNK10

	def update_preview(self):
		self.save_settings()
		self.parent.reload_list()
		self.parent.reload_canvas()

	def ok(self):
		self.update_preview()
		PyMSDialog.ok(self)

def edit_event(x1,y1,x2,y2, mouseX,mouseY, resizable=True):
	event = []
	nx1 = (x1 if x1 < x2 else x2)
	ny1 = (y1 if y1 < y2 else y2)
	nx2 = (x2 if x2 > x1 else x1)
	ny2 = (y2 if y2 > y1 else y1)
	d = 5 * resizable
	if nx1-d <= mouseX <= nx2+d and ny1-d <= mouseY <= ny2+d:
		event.append(EDIT_MOVE)
		if resizable:
			dist_left = abs(x1 - mouseX)
			dist_right = abs(x2 - mouseX)
			if dist_left < dist_right and dist_left <= 5:
				event = [EDIT_RESIZE_LEFT,EDIT_NONE]
			elif dist_right < dist_left and dist_right <= 5:
				event = [EDIT_RESIZE_RIGHT,EDIT_NONE]
			dist_top = abs(y1 - mouseY)
			dist_bot = abs(y2 - mouseY)
			if dist_top < dist_bot and dist_top <= 5:
				if len(event) == 1:
					event = [EDIT_NONE,EDIT_RESIZE_TOP]
				else:
					event[1] = EDIT_RESIZE_TOP
			elif dist_bot < dist_top and dist_bot <= 5:
				if len(event) == 1:
					event = [EDIT_NONE,EDIT_RESIZE_BOTTOM]
				else:
					event[1] = EDIT_RESIZE_BOTTOM
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
				add_line()

		if word:
			add_word()
		if line:
			add_line()
		return positions

class WidgetNode:
	def __init__(self, widget=None):
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
		if SHOW_IMAGES and self.widget and self.widget.type == DialogBIN.BINWidget.TYPE_IMAGE and self.widget.flags & DialogBIN.BINWidget.FLAG_VISIBLE and self.widget.string:
			photo_change = False
			if self.photo == None:
				photo_change = True
				pcx = PCX.PCX()
				try:
					pcx.load_file(toplevel.mpqhandler.get_file('MPQ:' + self.widget.string))
					trans = ((self.widget.flags & DialogBIN.BINWidget.FLAG_TRANSPARENCY) == DialogBIN.BINWidget.FLAG_TRANSPARENCY)
					self.photo = GRP.frame_to_photo(pcx.palette, pcx, -1, size=False, trans=trans)
				except Exception, e:
					print self.widget.string
					print repr(e)
			if self.photo:
				x1,y1,x2,y2 = self.bounding_box()
				if self.item_image:
					if photo_change:
						toplevel.widgetCanvas.itemconfigure(self.item_image, image=self.photo)
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
				color = '#505050'
				if self.widget:
					color = '#0080ff'
					if self.widget.type == DialogBIN.BINWidget.TYPE_DIALOG:
						color = '#00A0A0'
				self.item_bounds = toplevel.widgetCanvas.create_rectangle(x1,y1, x2,y2, width=1, outline=color)
				reorder = True
		elif self.item_bounds:
			toplevel.widgetCanvas.delete(self.item_bounds)
			self.item_bounds = None
		return reorder

	def update_text_bounds(self, toplevel):
		reorder = False
		SHOW_TEXT_BOUNDS = toplevel.show_bounds_text.get()
		if SHOW_TEXT_BOUNDS and self.widget and self.widget.display_text() != None:
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
		if SHOW_RESPONSIVE_BOUNDS and self.widget and self.widget.has_responsive():
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

	def remove_display(self, toplevel):
		if self.item_image:
			toplevel.widgetCanvas.delete(self.item_image)
			self.item_image = None
		if self.item_string_images:
			for item in self.item_string_images:
				toplevel.widgetCanvas.delete(item)
			self.item_string_images = []
		if self.item_bounds:
			toplevel.widgetCanvas.delete(self.item_bounds)
			self.item_bounds = None
		if self.item_text_bounds:
			toplevel.widgetCanvas.delete(self.item_text_bounds)
			self.item_text_bounds = None
		if self.item_responsive_bounds:
			toplevel.widgetCanvas.delete(self.item_responsive_bounds)
			self.item_responsive_bounds = None

class PyBIN(Tk):
	def __init__(self, guifile=None):
		self.settings = loadsettings('PyBIN',
			{
				'tfontgam':'MPQ:game\\tfontgam.pcx',
				'font10':'MPQ:font\\font10.fnt',
				'font14':'MPQ:font\\font14.fnt',
				'font16':'MPQ:font\\font16.fnt',
				'font16x':'MPQ:font\\font16x.fnt',
				'show_background_path_history':[
					'None',
					'MPQ:glue\\palmm\\backgnd.pcx',
				]
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
		self.event_moved = False

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

		self.show_images = BooleanVar()
		self.show_images.set(self.settings.get('show_images',True))
		self.show_text = BooleanVar()
		self.show_text.set(self.settings.get('show_text',True))
		self.show_smks = BooleanVar()
		self.show_smks.set(self.settings.get('show_smks',True))
		self.show_animated = BooleanVar()
		self.show_animated.set(self.settings.get('show_animated',False))
		self.show_background = BooleanVar()
		self.show_background.set(self.settings.get('show_background',False))
		self.show_background_index = IntVar()
		path = self.settings.get('show_background_path','None')
		history = self.settings.get('show_background_path_history',['None'])
		if not path in history:
			if path == 'None':
				history.insert(0, path)
			else:
				history.insert(1, path)
		self.last_background_index = history.index(path)
		self.show_background_index.set(self.last_background_index)
		self.show_bounds_widget = BooleanVar()
		self.show_bounds_widget.set(self.settings.get('show_bounds_widget',True))
		self.show_bounds_group = BooleanVar()
		self.show_bounds_group.set(self.settings.get('show_bounds_group',True))
		self.show_bounds_text = BooleanVar()
		self.show_bounds_text.set(self.settings.get('show_bounds_text',True))
		self.show_bounds_responsive = BooleanVar()
		self.show_bounds_responsive.set(self.settings.get('show_bounds_responsive',True))

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
			('add', self.add_node, LEFT),
			('remove', self.remove_node, LEFT),
			('edit', lambda: self.edit_node_settings(), LEFT),
			('down', lambda: self.move_node(2), RIGHT),
			('up', lambda: self.move_node(-1), RIGHT)
		)
		for icon,callback,side in buttons:
			image = PhotoImage(file=os.path.join(BASE_DIR,'Images','%s.gif' % icon))
			button = Button(f, image=image, width=20, height=20, command=callback, state=DISABLED)
			button.image = image
			# button.tooltip = Tooltip(button, btn[1])
			button.pack(side=side)
			self.buttons[icon] = button
		f.grid(row=2, column=0, padx=1, pady=1, sticky=EW)
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
		Checkbutton(flagframe, text='Background:', variable=self.show_background, command=lambda: self.toggle_setting('show_background',self.show_background)).grid(row=2, column=0, columnspan=2, sticky=W)
		f = Frame(flagframe)
		DropDown(f, self.show_background_index, self.settings['show_background_path_history'], self.change_background).grid(row=0, column=0, sticky=W+E)
		image = PhotoImage(file=os.path.join(BASE_DIR,'Images','open.gif'))
		button = Button(f, image=image, width=20, height=20)#, command=btn[1], state=btn[3])
		button.image = image
		button.grid(row=0, column=1)
		image = PhotoImage(file=os.path.join(BASE_DIR,'Images','openmpq.gif'))
		button = Button(f, image=image, width=20, height=20)#, command=btn[1], state=btn[3])
		button.image = image
		button.grid(row=0, column=2)
		f.grid_columnconfigure(0, weight=1)
		f.grid(row=3, column=0, columnspan=2, sticky=NSEW, padx=5, pady=0)
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
		boundsframe.grid(row=4, column=0, columnspan=2, sticky=NSEW, padx=5, pady=5)
		flagframe.grid_columnconfigure(0, weight=1)
		flagframe.grid_columnconfigure(1, weight=1)
		flagframe.grid(row=3, column=0, padx=1, pady=1, sticky=EW)
		leftframe.grid_rowconfigure(1, weight=1)
		leftframe.grid_columnconfigure(0, weight=1)
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
			node = WidgetNode()
		else:
			x1,y1,x2,y2 = parent.bounding_box()
			widget = DialogBIN.BINWidget(ctrl_type)
			widget.width = 201
			widget.height = 101
			widget.x1 = x1 + (x2-x1-(widget.width-1)) / 2
			widget.y1 = y1 + (y2-y1-(widget.height-1)) / 2
			widget.x2 = widget.x1 + widget.width-1
			widget.y2 = widget.y1 + widget.height-1
			if widget.type in DialogBIN.BINWidget.TYPES_RESPONSIVE:
				widget.responsive_x1 = 0
				widget.responsive_y1 = 0
				widget.responsive_x2 = widget.width-1
				widget.responsive_y2 = widget.height-1
			node = WidgetNode(widget)
		parent.add_child(node, index)
		self.reload_list()
		self.reload_canvas()
		self.select_node(node)

	def remove_node(self):
		self.selected_node.remove_display(self)
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

	def load_background(self, index):
		try:
			path = self.settings['show_background_path_history'][index]
			background = PCX.PCX()
			background.load_file(self.mpqhandler.get_file(path))
		except:
			return False
		self.background_image = GRP.frame_to_photo(background.palette, background, -1, size=False)
		return True

	def update_background(self):
		if self.bin and self.show_background.get() and self.show_background_index.get():
			if not self.background_image:
				self.load_background(self.show_background_index.get())
			if self.item_background:
				self.widgetCanvas.itemconfigure(self.item_background, image=self.background_image)
			else:
				self.item_background = self.widgetCanvas.create_image(0,0, image=self.background_image, anchor=NW)
				self.widgetCanvas.lower(self.item_background)
		elif self.item_background:
			self.widgetCanvas.delete(self.item_background)
			self.item_background = None

	def change_background(self, n):
		index = self.show_background_index.get()
		if index != self.last_background_index:
			changed = False
			path = 'None'
			if index:
				changed = self.load_background(index)
				if not changed:
					self.show_background_index.set(self.last_background_index)
					# todo: check remove from list
			else:
				self.background_image = None
				changed = True
			if changed:
				self.settings['show_background_path'] = path
				self.update_background()
				self.last_background_index = index

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
			node = WidgetNode(widget)
			if self.dialog == None:
				self.dialog = node
				# test = self.dialog
			else:
				self.dialog.add_child(node)
				# if len(test.children) == 4:
				# 	group = WidgetNode(None)
				# 	test.add_child(group)
				# 	test = group
				# test.add_child(node)

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
			if node == self.selected_node:
				self.widgetTree.select(node.index)
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
			self.update_background()
			reorder = False
			for node in self.flattened_nodes():
				reorder = node.update_display(self) or reorder
			self.update_selection_box()
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
			self.widgetTree.see(self.selected_node.index)
		else:
			self.widgetTree.select(None)

	def edit_node_settings(self, node=None):
		if node == None:
			node = self.selected_node
		if node and node.widget:
			WidgetSettings(self, node)

	def canvas_double_click(self, e, m):
		print ('canvas_double_click', e)
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
						for child in node.children:
							found_child = check_clicked(child, x,y)
							if found_child != None:
								found = found_child
								break
				return found
			node = check_clicked(self.dialog, e.x,e.y)
			if node:
				self.edit_node_settings(node)

	def list_double_click(self, event):
		print ('list_double_click', event)
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
		if self.selected_node:
			index = self.widgetTree.index("@%d,%d" % (event.x, event.y))
			self.widgetTree.highlight(index)

	def list_drop(self, event):
		# todo: Not started on node?
		if self.selected_node:
			self.widgetTree.highlight(None)
			index,below = self.widgetTree.lookup_coords(event.x, event.y)
			if index and index != self.selected_node.index:
				highlight = self.widget_map[index]
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
			for child in node.children:
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
						node.update_display(self)
						if node == self.selected_node:
							self.update_selection_box()
					offset_node(self.edit_node, dx,dy)
				elif self.event_moved:
					if EDIT_RESIZE_LEFT in self.current_event:
						self.edit_node.widget.x1 = x
					elif EDIT_RESIZE_RIGHT in self.current_event:
						self.edit_node.widget.x2 = x
					if EDIT_RESIZE_TOP in self.current_event:
						self.edit_node.widget.y1 = y
					elif EDIT_RESIZE_BOTTOM in self.current_event:
						self.edit_node.widget.y2 = y
					self.edit_node.update_display(self)
					if self.edit_node == self.selected_node:
						self.update_selection_box()
				check = self.edit_node
				while check.parent and check.parent.widget == None:
					check.parent.update_display(self)
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

		self.background_image = None

		self.item_background = None
		self.item_selection_box = None

		self.widgetTree.delete(ALL)
		self.widgetCanvas.delete(ALL)

	def new(self, key=None):
		if not self.unsaved():
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
			self.clear()
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
			self.bin.save_file(self.file)
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