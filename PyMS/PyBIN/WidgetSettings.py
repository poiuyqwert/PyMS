
from .SMKSettings import SMKSettings

from ..FileFormats import DialogBIN, TBL

from ..Utilities.UIKit import *
from ..Utilities.IntegerVar import IntegerVar
from ..Utilities.PyMSDialog import PyMSDialog
from ..Utilities.DropDown import DropDown
from ..Utilities import Assets

class WidgetSettings(PyMSDialog):
	def __init__(self, parent, node):
		self.settings = parent.settings
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

		self.scr_unknown1 = IntegerVar(range=[0,65535])

		PyMSDialog.__init__(self, parent, 'Edit ' + DialogBIN.BINWidget.TYPE_NAMES[node.widget.type], resizable=(False, False))

	def widgetize(self):
		def calc_button(f, calc, orig, offset, direction, fix):
			return Button(f, image=Assets.get_image('debug'), width=20, height=20, command=lambda calc=calc,orig=orig,offset=offset,direction=direction,fix=fix: self.calculate(calc,orig,offset,direction,fix))
		boundsframe = LabelFrame(self, text="Bounds")
		Label(boundsframe, text='Left:').grid(row=0,column=0, sticky=E)
		Entry(boundsframe, textvariable=self.left, font=Font.fixed(), width=5).grid(row=0,column=1)
		calculate = calc_button(boundsframe, self.left, self.right, self.width, -1, 1)
		calculate.grid(row=0,column=2)
		self.advanced_widgets.append(calculate)
		Label(boundsframe, text='Top:').grid(row=0,column=3, sticky=E)
		Entry(boundsframe, textvariable=self.top, font=Font.fixed(), width=5).grid(row=0,column=4)
		calculate = calc_button(boundsframe, self.top, self.bottom, self.height, -1, 1)
		calculate.grid(row=0,column=5)
		self.advanced_widgets.append(calculate)
		right_label = Label(boundsframe, text='Right:')
		right_label.grid(row=1,column=0, sticky=E)
		self.advanced_widgets.append(right_label)
		right_entry = Entry(boundsframe, textvariable=self.right, font=Font.fixed(), width=5)
		right_entry.grid(row=1,column=1)
		self.advanced_widgets.append(right_entry)
		calculate = calc_button(boundsframe, self.right, self.left, self.width, 1, -1)
		calculate.grid(row=1,column=2)
		self.advanced_widgets.append(calculate)
		bottom_label = Label(boundsframe, text='Bottom:')
		bottom_label.grid(row=1,column=3, sticky=E)
		self.advanced_widgets.append(bottom_label)
		bottom_entry = Entry(boundsframe, textvariable=self.bottom, font=Font.fixed(), width=5)
		bottom_entry.grid(row=1,column=4)
		self.advanced_widgets.append(bottom_entry)
		calculate = calc_button(boundsframe, self.bottom, self.top, self.height, 1, -1)
		calculate.grid(row=1,column=5)
		self.advanced_widgets.append(calculate)
		Label(boundsframe, text='Width:').grid(row=2,column=0, sticky=E)
		Entry(boundsframe, textvariable=self.width, font=Font.fixed(), width=5).grid(row=2,column=1)
		calculate = calc_button(boundsframe, self.width, self.right, self.left, -1, 1)
		calculate.grid(row=2,column=2)
		self.advanced_widgets.append(calculate)
		Label(boundsframe, text='Height:').grid(row=2,column=3, sticky=E)
		Entry(boundsframe, textvariable=self.height, font=Font.fixed(), width=5).grid(row=2,column=4)
		calculate = calc_button(boundsframe, self.height, self.bottom, self.top, -1, 1)
		calculate.grid(row=2,column=5)
		self.advanced_widgets.append(calculate)
		boundsframe.grid(row=0,column=0, padx=5,pady=0, ipadx=2,ipady=2, sticky=N)

		responsiveframe = LabelFrame(self, text="Mouse Response")
		Label(responsiveframe, text='Left:').grid(row=0,column=0, sticky=E)
		Entry(responsiveframe, textvariable=self.responsive_left, font=Font.fixed(), width=5).grid(row=0,column=1)
		calculate = calc_button(responsiveframe, self.responsive_left, self.responsive_right, self.responsive_width, -1, 1)
		calculate.grid(row=0,column=2)
		self.advanced_widgets.append(calculate)
		Label(responsiveframe, text='Top:').grid(row=0,column=3, sticky=E)
		Entry(responsiveframe, textvariable=self.responsive_top, font=Font.fixed(), width=5).grid(row=0,column=4)
		calculate = calc_button(responsiveframe, self.responsive_top, self.responsive_bottom, self.responsive_height, -1, 1)
		calculate.grid(row=0,column=5)
		self.advanced_widgets.append(calculate)
		right_label = Label(responsiveframe, text='Right:')
		right_label.grid(row=1,column=0, sticky=E)
		self.advanced_widgets.append(right_label)
		right_entry = Entry(responsiveframe, textvariable=self.responsive_right, font=Font.fixed(), width=5)
		right_entry.grid(row=1,column=1)
		self.advanced_widgets.append(right_entry)
		calculate = calc_button(responsiveframe, self.responsive_right, self.responsive_left, self.responsive_width, 1, -1)
		calculate.grid(row=1,column=2)
		self.advanced_widgets.append(calculate)
		bottom_label = Label(responsiveframe, text='Bottom:')
		bottom_label.grid(row=1,column=3, sticky=E)
		self.advanced_widgets.append(bottom_label)
		bottom_entry = Entry(responsiveframe, textvariable=self.responsive_bottom, font=Font.fixed(), width=5)
		bottom_entry.grid(row=1,column=4)
		self.advanced_widgets.append(bottom_entry)
		calculate = calc_button(responsiveframe, self.responsive_bottom, self.responsive_top, self.responsive_height, 1, -1)
		calculate.grid(row=1,column=5)
		self.advanced_widgets.append(calculate)
		Label(responsiveframe, text='Width:').grid(row=2,column=0, sticky=E)
		Entry(responsiveframe, textvariable=self.responsive_width, font=Font.fixed(), width=5).grid(row=2,column=1)
		calculate = calc_button(responsiveframe, self.responsive_width, self.responsive_right, self.responsive_left, -1, 1)
		calculate.grid(row=2,column=2)
		self.advanced_widgets.append(calculate)
		Label(responsiveframe, text='Height:').grid(row=2,column=3, sticky=E)
		Entry(responsiveframe, textvariable=self.responsive_height, font=Font.fixed(), width=5).grid(row=2,column=4)
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
		Entry(textframe, textvariable=self.string, font=Font.fixed()).grid(row=0,column=1, sticky=EW)
		findimage = Button(textframe, image=Assets.get_image('openmpq'), width=20, height=20)#, command=btn[1], state=btn[3])
		findimage.grid(row=0, column=2)
		textframe.grid_columnconfigure(1, weight=1)
		textframe.grid(row=0,column=0, columnspan=5, sticky=EW)
		transparent = Checkbutton(textframe, text='Image Transparency', variable=self.flag_transparency)
		transparent.grid(row=1,column=0, columnspan=5, sticky=W)
		offsetframe = LabelFrame(stringframe, text='Offset')
		Label(offsetframe, text='X:').grid(row=0,column=0, sticky=E)
		Entry(offsetframe, textvariable=self.text_offset_x, font=Font.fixed(), width=5).grid(row=0,column=1)
		Label(offsetframe, text='Y:').grid(row=1,column=0, sticky=E)
		Entry(offsetframe, textvariable=self.text_offset_y, font=Font.fixed(), width=5).grid(row=1,column=1)
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
		self.smks_dropdown = DropDown(smkframe, self.smk, ['None'], stay_right=False)
		self.smks_dropdown.grid(row=0, column=0, padx=2,pady=2, sticky=EW)
		button = Button(smkframe, image=Assets.get_image('edit'), width=20, height=20, command=self.edit_smk)
		button.grid(row=0, column=1)
		button = Button(smkframe, image=Assets.get_image('add'), width=20, height=20, command=self.add_smk)
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
		scrframe = LabelFrame(otherframe, text='SC:R')
		f = Frame(scrframe)
		Label(f, text='Unknown 1:').pack(side=LEFT)
		self.scr_unknown1_entry = Entry(f, textvariable=self.scr_unknown1, font=Font.fixed(), width=5, state=NORMAL if self.parent.scr_enabled.get() else DISABLED)
		self.scr_unknown1_entry.pack(side=LEFT)
		f.grid(row=0,column=3, columnspan=2, padx=5, sticky=E)
		scrframe.grid(row=0,column=3, padx=2,pady=2, sticky=N)
		otherframe.grid(row=3,column=0, columnspan=2, padx=3,pady=3, sticky=EW)

		miscframe = LabelFrame(self, text='Misc.')
		Checkbutton(miscframe, text='Bring to Front', variable=self.flag_on_top).grid(row=0,column=0, sticky=W)
		f = Frame(miscframe)
		Label(f, text='Control ID:').pack(side=LEFT)
		Entry(f, textvariable=self.identifier, font=Font.fixed(), width=5).pack(side=LEFT)
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
		self.advanced_widgets.append(scrframe)
		self.advanced_widgets.append(miscframe)

		bottom = Frame(self)
		ok = Button(bottom, text='Ok', width=10, command=self.ok)
		ok.pack(side=LEFT, padx=1, pady=3)
		Button(bottom, text='Update Preview', width=15, command=self.update_preview).pack(side=LEFT, padx=3, pady=3)
		Checkbutton(bottom, text='Advanced', variable=self.show_advanced, command=self.update_advanced).pack(side=RIGHT, padx=1, pady=3)
		bottom.grid(row=5,column=0, columnspan=2, pady=3, padx=3, sticky=EW)

		return ok

	def setup_complete(self):
		self.load_settings()
		self.load_properties()
		self.update_advanced()

	def update_advanced(self):
		self.minsize(0,0)
		self.maxsize(9999, 9999)
		w,h,x,y,_ = parse_geometry(self.geometry())
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
		w,h,x,y,_ = parse_geometry(self.geometry())
		center_x -= w/2.0
		center_y -= h/2.0
		self.geometry('+%d+%d' % (int(center_x),int(center_y)))
		self.minsize(w,h)
		self.maxsize(w,h)

	def calculate(self, calc, orig, offset, direction, fix, allow_advanced=True):
		if not self.show_advanced.get() or allow_advanced:
			calc.set(orig.get() + offset.get() * direction + fix)

	def load_settings(self):
		self.show_advanced.set(self.settings.edit.widget.get('advanced',False))
		self.settings.windows.edit.load_window_size('widget', self)
	def save_settings(self):
		self.settings.edit.widget.advanced = not not self.show_advanced.get()
		self.settings.windows.edit.save_window_size('widget', self)

	def load_property_smk(self):
		smks = ['None']
		for smk in self.parent.bin.smks:
			name = smk.filename
			if smk.overlay_smk:
				name += " (Overlay: %s)" % smk.overlay_smk.filename
			smks.append(name)
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
		self.scr_unknown1.set(self.node.widget.scr_unknown1)
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
		edited = False
		index = self.smk.get()-1
		smk = (None if index == -1 else self.parent.bin.smks[index])
		if smk != self.node.widget.smk:
			self.node.widget.smk = smk
			edited = True
		return edited
	def save_properties(self):
		edited = False
		if self.left.get() != self.node.widget.x1:
			self.node.widget.x1 = self.left.get()
			edited = True
		if self.right.get() != self.node.widget.x2:
			self.node.widget.x2 = self.right.get()
			edited = True
		if self.width.get() != self.node.widget.width:
			self.node.widget.width = self.width.get()
			edited = True
		if self.top.get() != self.node.widget.y1:
			self.node.widget.y1 = self.top.get()
			edited = True
		if self.bottom.get() != self.node.widget.y2:
			self.node.widget.y2 = self.bottom.get()
			edited = True
		if self.height.get() != self.node.widget.height:
			self.node.widget.height = self.height.get()
			edited = True
		string = TBL.compile_string(self.string.get())
		if string != self.node.widget.string:
			self.node.widget.string = string
			edited = True
		if self.identifier.get() != self.node.widget.identifier:
			self.node.widget.identifier = self.identifier.get()
			edited = True
		if self.scr_unknown1.get() != self.node.widget.scr_unknown1:
			self.node.widget.scr_unknown1 = self.scr_unknown1.get()
			edited = True
		edited = edited or self.save_property_smk()
		if self.text_offset_x.get() != self.node.widget.text_offset_x:
			self.node.widget.text_offset_x = self.text_offset_x.get()
			edited = True
		if self.text_offset_y.get() != self.node.widget.text_offset_y:
			self.node.widget.text_offset_y = self.text_offset_y.get()
			edited = True
		if self.responsive_left.get() != self.node.widget.responsive_x1:
			self.node.widget.responsive_x1 = self.responsive_left.get()
			edited = True
		if self.responsive_right.get() != self.node.widget.responsive_x2:
			self.node.widget.responsive_x2 = self.responsive_right.get()
			edited = True
		if self.responsive_width.get() != self.node.widget.responsive_width:
			self.node.widget.responsive_width = self.responsive_width.get()
			edited = True
		if self.responsive_top.get() != self.node.widget.responsive_y1:
			self.node.widget.responsive_y1 = self.responsive_top.get()
			edited = True
		if self.responsive_bottom.get() != self.node.widget.responsive_y2:
			self.node.widget.responsive_y2 = self.responsive_bottom.get()
			edited = True
		if self.responsive_height.get() != self.node.widget.responsive_height:
			self.node.widget.responsive_height = self.responsive_height.get()
			edited = True

		flags = 0
		flags |= self.flag_unk1.get() * DialogBIN.BINWidget.FLAG_UNK1
		flags |= self.flag_disabled.get() * DialogBIN.BINWidget.FLAG_DISABLED
		flags |= self.flag_unk2.get() * DialogBIN.BINWidget.FLAG_UNK2
		flags |= self.flag_visible.get() * DialogBIN.BINWidget.FLAG_VISIBLE
		flags |= self.flag_responsive.get() * DialogBIN.BINWidget.FLAG_RESPONSIVE
		flags |= self.flag_unk3.get() * DialogBIN.BINWidget.FLAG_UNK3
		flags |= self.flag_cancel_btn.get() * DialogBIN.BINWidget.FLAG_CANCEL_BTN
		flags |= self.flag_no_hover_snd.get() * DialogBIN.BINWidget.FLAG_NO_HOVER_SND
		flags |= self.flag_virtual_hotkey.get() * DialogBIN.BINWidget.FLAG_VIRTUAL_HOTKEY
		flags |= self.flag_has_hotkey.get() * DialogBIN.BINWidget.FLAG_HAS_HOTKEY
		flags |= self.flag_font_size_10.get() * DialogBIN.BINWidget.FLAG_FONT_SIZE_10
		flags |= self.flag_font_size_16.get() * DialogBIN.BINWidget.FLAG_FONT_SIZE_16
		flags |= self.flag_unk4.get() * DialogBIN.BINWidget.FLAG_UNK4
		flags |= self.flag_transparency.get() * DialogBIN.BINWidget.FLAG_TRANSPARENCY
		flags |= self.flag_font_size_16x.get() * DialogBIN.BINWidget.FLAG_FONT_SIZE_16x
		flags |= self.flag_unk5.get() * DialogBIN.BINWidget.FLAG_UNK5
		flags |= self.flag_font_size_14.get() * DialogBIN.BINWidget.FLAG_FONT_SIZE_14
		flags |= self.flag_unk6.get() * DialogBIN.BINWidget.FLAG_UNK6
		flags |= self.flag_translucent.get() * DialogBIN.BINWidget.FLAG_TRANSLUCENT
		flags |= self.flag_default_btn.get() * DialogBIN.BINWidget.FLAG_DEFAULT_BTN
		flags |= self.flag_on_top.get() * DialogBIN.BINWidget.FLAG_ON_TOP
		flags |= self.flag_text_align_center.get() * DialogBIN.BINWidget.FLAG_TEXT_ALIGN_CENTER
		flags |= self.flag_text_align_right.get() * DialogBIN.BINWidget.FLAG_TEXT_ALIGN_RIGHT
		flags |= self.flag_text_align_center2.get() * DialogBIN.BINWidget.FLAG_TEXT_ALIGN_CENTER2
		flags |= self.flag_align_top.get() * DialogBIN.BINWidget.FLAG_ALIGN_TOP
		flags |= self.flag_align_middle.get() * DialogBIN.BINWidget.FLAG_ALIGN_MIDDLE
		flags |= self.flag_align_bottom.get() * DialogBIN.BINWidget.FLAG_ALIGN_BOTTOM
		flags |= self.flag_unk7.get() * DialogBIN.BINWidget.FLAG_UNK7
		flags |= self.flag_unk8.get() * DialogBIN.BINWidget.FLAG_UNK8
		flags |= self.flag_unk9.get() * DialogBIN.BINWidget.FLAG_UNK9
		flags |= self.flag_no_click_snd.get() * DialogBIN.BINWidget.FLAG_NO_CLICK_SND
		flags |= self.flag_unk10.get() * DialogBIN.BINWidget.FLAG_UNK10
		if flags != self.node.widget.flags:
			self.node.widget.flags = flags
			edited = True

		self.node.string = None
		self.node.item_string_images = None

		if edited:
			self.mark_edited()

	def update_preview(self):
		self.save_properties()
		self.parent.reload_list()
		self.parent.reload_canvas()

	def edit_smk(self):
		if self.node.widget.smk:
			SMKSettings(self, self.node.widget.smk)

	def add_smk(self):
		smk = DialogBIN.BINSMK()
		self.parent.bin.smks.append(smk)
		self.node.widget.smk = smk
		self.mark_edited()
		SMKSettings(self, smk)

	def mark_edited(self):
		self.parent.mark_edited()

	def update_smks(self):
		self.load_property_smk()

	def ok(self):
		self.update_preview()
		PyMSDialog.ok(self)

	def cancel(self):
		self.ok()

	def dismiss(self):
		self.save_settings()
		PyMSDialog.dismiss(self)
