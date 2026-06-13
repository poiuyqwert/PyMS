
from __future__ import annotations

from .Config import PyBINConfig
from .Delegates import MainDelegate
from .SMKSettings import SMKSettings

from ..FileFormats import DialogBIN, TBL

from ..Utilities import UIKit as UI
from ..Utilities.PyMSDialog import PyMSDialog
from ..Utilities.utils import pack_flags
from ..Utilities import Assets
from ..Utilities.MPQHandler import MPQHandler

from typing import TYPE_CHECKING, Callable, Any
if TYPE_CHECKING:
	from .WidgetNode import WidgetNode

class WidgetSettings(PyMSDialog, MainDelegate):
	def __init__(self, parent: UI.Misc, node: WidgetNode, delegate: MainDelegate) -> None:
		self.node = node
		assert node.widget is not None
		self.widget = node.widget
		self.delegate = delegate

		self.advanced_widgets: list[UI.Widget] = []
		self.advanced_shown = True
		self.show_advanced = UI.BooleanVar()

		self.left = UI.IntegerVar(val_range=[0,65535])
		self.right = UI.IntegerVar(val_range=[0,65535])
		self.width = UI.IntegerVar(val_range=[0,65535])
		def calc_right(_: Any) -> None:
			self.calculate(self.right, self.left, self.width, 1, fix=-1, allow_advanced=False)
		self.left.callback = calc_right
		self.width.callback = calc_right
		self.top = UI.IntegerVar(val_range=[0,65535])
		self.bottom = UI.IntegerVar(val_range=[0,65535])
		self.height = UI.IntegerVar(val_range=[0,65535])
		def calc_bottom(_: Any) -> None:
			self.calculate(self.left, self.right, self.width, -1, fix=1, allow_advanced=False)
		self.top.callback = calc_bottom
		self.height.callback = calc_bottom
		self.string = UI.StringVar()
		self.identifier = UI.IntegerVar(val_range=[0,65535])
		self.smk = UI.IntVar()
		self.text_offset_x = UI.IntegerVar(val_range=[0,65535])
		self.text_offset_y = UI.IntegerVar(val_range=[0,65535])
		self.responsive_left = UI.IntegerVar(val_range=[0,65535])
		self.responsive_right = UI.IntegerVar(val_range=[0,65535])
		self.responsive_width = UI.IntegerVar(val_range=[0,65535])
		def calc_responsive_right(_: Any) -> None:
			self.calculate(self.responsive_right, self.responsive_left, self.responsive_width, 1, fix=-1, allow_advanced=False)
		self.responsive_left.callback = calc_responsive_right
		self.responsive_width.callback = calc_responsive_right
		self.responsive_top = UI.IntegerVar(val_range=[0,65535])
		self.responsive_bottom = UI.IntegerVar(val_range=[0,65535])
		self.responsive_height = UI.IntegerVar(val_range=[0,65535])
		def calc_responsive_bottom(_: Any) -> None:
			self.calculate(self.responsive_left, self.responsive_right, self.responsive_width, -1, fix=1, allow_advanced=False)
		self.responsive_top.callback = calc_responsive_bottom
		self.responsive_height.callback = calc_responsive_bottom

		self.flag_unk1 = UI.BooleanVar()
		self.flag_disabled = UI.BooleanVar()
		self.flag_unk2 = UI.BooleanVar()
		self.flag_visible = UI.BooleanVar()
		self.flag_responsive = UI.BooleanVar()
		self.flag_unk3 = UI.BooleanVar()
		self.flag_cancel_btn = UI.BooleanVar()
		self.flag_no_hover_snd = UI.BooleanVar()
		self.flag_virtual_hotkey = UI.BooleanVar()
		self.flag_has_hotkey = UI.BooleanVar()
		self.flag_font_size_10 = UI.BooleanVar()
		self.flag_font_size_16 = UI.BooleanVar()
		self.flag_unk4 = UI.BooleanVar()
		self.flag_transparency = UI.BooleanVar()
		self.flag_font_size_16x = UI.BooleanVar()
		self.flag_unk5 = UI.BooleanVar()
		self.flag_font_size_14 = UI.BooleanVar()
		self.flag_unk6 = UI.BooleanVar()
		self.flag_translucent = UI.BooleanVar()
		self.flag_default_btn = UI.BooleanVar()
		self.flag_on_top = UI.BooleanVar()
		self.flag_text_align_center = UI.BooleanVar()
		self.flag_text_align_right = UI.BooleanVar()
		self.flag_text_align_center2 = UI.BooleanVar()
		self.flag_align_top = UI.BooleanVar()
		self.flag_align_middle = UI.BooleanVar()
		self.flag_align_bottom = UI.BooleanVar()
		self.flag_unk7 = UI.BooleanVar()
		self.flag_unk8 = UI.BooleanVar()
		self.flag_unk9 = UI.BooleanVar()
		self.flag_no_click_snd = UI.BooleanVar()
		self.flag_unk10 = UI.BooleanVar()

		self.scr_unknown1 = UI.IntegerVar(val_range=[0,65535])

		assert node.widget is not None
		PyMSDialog.__init__(self, parent, 'Edit ' + DialogBIN.BINWidget.TYPE_NAMES[node.widget.type], resizable=(False, False))

	def widgetize(self) -> (UI.Misc | None):
		def calc_button(f: UI.Misc, calc: UI.IntegerVar, orig: UI.IntegerVar, offset: UI.IntegerVar, direction: int, *, fix: int) -> UI.Button:
			def calc_callback(calc: UI.IntegerVar, orig: UI.IntegerVar, offset: UI.IntegerVar, direction: int, *, fix: int) -> Callable[[], None]:
				def calculate() -> None:
					self.calculate(calc, orig, offset, direction, fix=fix)
				return calculate
			return UI.Button(f, image=Assets.get_image('debug'), width=20, height=20, command=calc_callback(calc, orig, offset, direction, fix=fix))
		boundsframe = UI.LabelFrame(self, text="Bounds")
		UI.Label(boundsframe, text='Left:').grid(row=0,column=0, sticky=UI.E)
		UI.Entry(boundsframe, textvariable=self.left, font=UI.Font.fixed(), width=5).grid(row=0,column=1)
		calculate = calc_button(boundsframe, self.left, self.right, self.width, -1, fix=1)
		calculate.grid(row=0,column=2)
		self.advanced_widgets.append(calculate)
		UI.Label(boundsframe, text='Top:').grid(row=0,column=3, sticky=UI.E)
		UI.Entry(boundsframe, textvariable=self.top, font=UI.Font.fixed(), width=5).grid(row=0,column=4)
		calculate = calc_button(boundsframe, self.top, self.bottom, self.height, -1, fix=1)
		calculate.grid(row=0,column=5)
		self.advanced_widgets.append(calculate)
		right_label = UI.Label(boundsframe, text='Right:')
		right_label.grid(row=1,column=0, sticky=UI.E)
		self.advanced_widgets.append(right_label)
		right_entry = UI.Entry(boundsframe, textvariable=self.right, font=UI.Font.fixed(), width=5)
		right_entry.grid(row=1,column=1)
		self.advanced_widgets.append(right_entry)
		calculate = calc_button(boundsframe, self.right, self.left, self.width, 1, fix=-1)
		calculate.grid(row=1,column=2)
		self.advanced_widgets.append(calculate)
		bottom_label = UI.Label(boundsframe, text='Bottom:')
		bottom_label.grid(row=1,column=3, sticky=UI.E)
		self.advanced_widgets.append(bottom_label)
		bottom_entry = UI.Entry(boundsframe, textvariable=self.bottom, font=UI.Font.fixed(), width=5)
		bottom_entry.grid(row=1,column=4)
		self.advanced_widgets.append(bottom_entry)
		calculate = calc_button(boundsframe, self.bottom, self.top, self.height, 1, fix=-1)
		calculate.grid(row=1,column=5)
		self.advanced_widgets.append(calculate)
		UI.Label(boundsframe, text='Width:').grid(row=2,column=0, sticky=UI.E)
		UI.Entry(boundsframe, textvariable=self.width, font=UI.Font.fixed(), width=5).grid(row=2,column=1)
		calculate = calc_button(boundsframe, self.width, self.right, self.left, -1, fix=1)
		calculate.grid(row=2,column=2)
		self.advanced_widgets.append(calculate)
		UI.Label(boundsframe, text='Height:').grid(row=2,column=3, sticky=UI.E)
		UI.Entry(boundsframe, textvariable=self.height, font=UI.Font.fixed(), width=5).grid(row=2,column=4)
		calculate = calc_button(boundsframe, self.height, self.bottom, self.top, -1, fix=1)
		calculate.grid(row=2,column=5)
		self.advanced_widgets.append(calculate)
		boundsframe.grid(row=0,column=0, padx=5,pady=0, ipadx=2,ipady=2, sticky=UI.N)

		responsiveframe = UI.LabelFrame(self, text="Mouse Response")
		UI.Label(responsiveframe, text='Left:').grid(row=0,column=0, sticky=UI.E)
		UI.Entry(responsiveframe, textvariable=self.responsive_left, font=UI.Font.fixed(), width=5).grid(row=0,column=1)
		calculate = calc_button(responsiveframe, self.responsive_left, self.responsive_right, self.responsive_width, -1, fix=1)
		calculate.grid(row=0,column=2)
		self.advanced_widgets.append(calculate)
		UI.Label(responsiveframe, text='Top:').grid(row=0,column=3, sticky=UI.E)
		UI.Entry(responsiveframe, textvariable=self.responsive_top, font=UI.Font.fixed(), width=5).grid(row=0,column=4)
		calculate = calc_button(responsiveframe, self.responsive_top, self.responsive_bottom, self.responsive_height, -1, fix=1)
		calculate.grid(row=0,column=5)
		self.advanced_widgets.append(calculate)
		right_label = UI.Label(responsiveframe, text='Right:')
		right_label.grid(row=1,column=0, sticky=UI.E)
		self.advanced_widgets.append(right_label)
		right_entry = UI.Entry(responsiveframe, textvariable=self.responsive_right, font=UI.Font.fixed(), width=5)
		right_entry.grid(row=1,column=1)
		self.advanced_widgets.append(right_entry)
		calculate = calc_button(responsiveframe, self.responsive_right, self.responsive_left, self.responsive_width, 1, fix=-1)
		calculate.grid(row=1,column=2)
		self.advanced_widgets.append(calculate)
		bottom_label = UI.Label(responsiveframe, text='Bottom:')
		bottom_label.grid(row=1,column=3, sticky=UI.E)
		self.advanced_widgets.append(bottom_label)
		bottom_entry = UI.Entry(responsiveframe, textvariable=self.responsive_bottom, font=UI.Font.fixed(), width=5)
		bottom_entry.grid(row=1,column=4)
		self.advanced_widgets.append(bottom_entry)
		calculate = calc_button(responsiveframe, self.responsive_bottom, self.responsive_top, self.responsive_height, 1, fix=-1)
		calculate.grid(row=1,column=5)
		self.advanced_widgets.append(calculate)
		UI.Label(responsiveframe, text='Width:').grid(row=2,column=0, sticky=UI.E)
		UI.Entry(responsiveframe, textvariable=self.responsive_width, font=UI.Font.fixed(), width=5).grid(row=2,column=1)
		calculate = calc_button(responsiveframe, self.responsive_width, self.responsive_right, self.responsive_left, -1, fix=1)
		calculate.grid(row=2,column=2)
		self.advanced_widgets.append(calculate)
		UI.Label(responsiveframe, text='Height:').grid(row=2,column=3, sticky=UI.E)
		UI.Entry(responsiveframe, textvariable=self.responsive_height, font=UI.Font.fixed(), width=5).grid(row=2,column=4)
		calculate = calc_button(responsiveframe, self.responsive_height, self.responsive_bottom, self.responsive_top, -1, fix=1)
		calculate.grid(row=2,column=5)
		self.advanced_widgets.append(calculate)
		UI.Checkbutton(responsiveframe, text='Responds to Mouse', variable=self.flag_responsive).grid(row=3,column=0, columnspan=6)
		responsiveframe.grid(row=0,column=1, padx=5,pady=0, ipadx=2,ipady=2, sticky=UI.N)

		isimage = self.widget.type == DialogBIN.BINWidget.TYPE_IMAGE
		stringframe = UI.LabelFrame(self, text="String")
		textframe = UI.Frame(stringframe)
		self.string_label = UI.Label(textframe, text='Image:' if isimage else 'Text:')
		self.string_label.grid(row=0,column=0)
		UI.Entry(textframe, textvariable=self.string, font=UI.Font.fixed()).grid(row=0,column=1, sticky=UI.EW)
		findimage = UI.Button(textframe, image=Assets.get_image('openmpq'), width=20, height=20)#, command=btn[1], state=btn[3])
		findimage.grid(row=0, column=2)
		textframe.grid_columnconfigure(1, weight=1)
		textframe.grid(row=0,column=0, columnspan=5, sticky=UI.EW)
		transparent = UI.Checkbutton(textframe, text='Image Transparency', variable=self.flag_transparency)
		transparent.grid(row=1,column=0, columnspan=5, sticky=UI.W)
		offsetframe = UI.LabelFrame(stringframe, text='Offset')
		UI.Label(offsetframe, text='X:').grid(row=0,column=0, sticky=UI.E)
		UI.Entry(offsetframe, textvariable=self.text_offset_x, font=UI.Font.fixed(), width=5).grid(row=0,column=1)
		UI.Label(offsetframe, text='Y:').grid(row=1,column=0, sticky=UI.E)
		UI.Entry(offsetframe, textvariable=self.text_offset_y, font=UI.Font.fixed(), width=5).grid(row=1,column=1)
		offsetframe.grid(row=3,column=0, padx=3,pady=3, ipadx=2,ipady=2, sticky=UI.N)
		hotkeyframe = UI.LabelFrame(stringframe, text='Hotkey')
		UI.Checkbutton(hotkeyframe, text='Normal', variable=self.flag_has_hotkey).grid(row=0,column=0, sticky=UI.W)
		UI.Checkbutton(hotkeyframe, text='Virtual', variable=self.flag_virtual_hotkey).grid(row=1,column=0, sticky=UI.W)
		hotkeyframe.grid(row=3,column=1, padx=3,pady=3, sticky=UI.N)
		horframe = UI.LabelFrame(stringframe, text="Horizontal")
		UI.Checkbutton(horframe, text='Center', variable=self.flag_text_align_center).grid(row=0,column=0, sticky=UI.W)
		UI.Checkbutton(horframe, text='Right', variable=self.flag_text_align_right).grid(row=1,column=0, sticky=UI.W)
		UI.Checkbutton(horframe, text='Center 2', variable=self.flag_text_align_center2).grid(row=2,column=0, sticky=UI.W)
		horframe.grid(row=3,column=2, padx=3,pady=3, sticky=UI.N)
		verframe = UI.LabelFrame(stringframe, text="Vertical")
		UI.Checkbutton(verframe, text='Top', variable=self.flag_align_top).grid(row=0,column=0, sticky=UI.W)
		UI.Checkbutton(verframe, text='Middle', variable=self.flag_align_middle).grid(row=1,column=0, sticky=UI.W)
		UI.Checkbutton(verframe, text='Bottom', variable=self.flag_align_bottom).grid(row=2,column=0, sticky=UI.W)
		verframe.grid(row=3,column=3, padx=3,pady=3, sticky=UI.N)
		fontframe = UI.LabelFrame(stringframe, text='Font')
		UI.Checkbutton(fontframe, text='Size 10', variable=self.flag_font_size_10).grid(row=0,column=0, sticky=UI.W)
		UI.Checkbutton(fontframe, text='Size 14', variable=self.flag_font_size_14).grid(row=1,column=0, sticky=UI.W)
		UI.Checkbutton(fontframe, text='Size 16', variable=self.flag_font_size_16).grid(row=2,column=0, sticky=UI.W)
		UI.Checkbutton(fontframe, text='Size 16x', variable=self.flag_font_size_16x).grid(row=3,column=0, sticky=UI.W)
		fontframe.grid(row=3,column=4, padx=3,pady=3, sticky=UI.N)

		stringframe.grid_columnconfigure(0, weight=1)
		stringframe.grid_columnconfigure(1, weight=1)
		stringframe.grid_columnconfigure(2, weight=1)
		stringframe.grid_columnconfigure(3, weight=1)
		stringframe.grid_columnconfigure(4, weight=1)
		stringframe.grid(row=1,column=0, columnspan=2, padx=5,pady=0, ipadx=2,ipady=2, sticky=UI.NSEW)

		smkframe = UI.LabelFrame(self, text='SMK')
		self.smks_dropdown = UI.DropDown(smkframe, self.smk, ['None'], stay_right=False)
		self.smks_dropdown.grid(row=0, column=0, padx=2,pady=2, sticky=UI.EW)
		button = UI.Button(smkframe, image=Assets.get_image('edit'), width=20, height=20, command=self.edit_smk)
		button.grid(row=0, column=1)
		button = UI.Button(smkframe, image=Assets.get_image('add'), width=20, height=20, command=self.add_smk)
		button.grid(row=0, column=2)
		UI.Checkbutton(smkframe, text='Translucent', variable=self.flag_translucent).grid(row=1,column=0, columnspan=3)
		smkframe.grid_columnconfigure(0, weight=1)
		smkframe.grid(row=2,column=0, columnspan=2, padx=5,pady=0, ipadx=2,ipady=2, sticky=UI.NSEW)

		otherframe = UI.Frame(self)
		stateframe = UI.LabelFrame(otherframe, text='State')
		UI.Checkbutton(stateframe, text='Visible', variable=self.flag_visible).grid(row=2,column=0, sticky=UI.W)
		UI.Checkbutton(stateframe, text='Disabled', variable=self.flag_disabled).grid(row=3,column=0, sticky=UI.W)
		stateframe.grid(row=0,column=0, padx=2,pady=2, sticky=UI.N)
		soundframe = UI.LabelFrame(otherframe, text='Sounds')
		UI.Checkbutton(soundframe, text='No Hover', variable=self.flag_no_hover_snd).grid(row=2,column=0, sticky=UI.W)
		UI.Checkbutton(soundframe, text='No Click', variable=self.flag_no_click_snd).grid(row=3,column=0, sticky=UI.W)
		soundframe.grid(row=0,column=1, padx=2,pady=2, sticky=UI.N)
		typeframe = UI.LabelFrame(otherframe, text='Btn. Type')
		UI.Checkbutton(typeframe, text='Default', variable=self.flag_default_btn).grid(row=0,column=0, sticky=UI.W)
		UI.Checkbutton(typeframe, text='Cancel', variable=self.flag_cancel_btn).grid(row=1,column=0, sticky=UI.W)
		typeframe.grid(row=0,column=2, padx=2,pady=2, sticky=UI.N)
		scrframe = UI.LabelFrame(otherframe, text='SC:R')
		f = UI.Frame(scrframe)
		UI.Label(f, text='Unknown 1:').pack(side=UI.LEFT)
		self.scr_unknown1_entry = UI.Entry(f, textvariable=self.scr_unknown1, font=UI.Font.fixed(), width=5, state=UI.NORMAL if self.delegate.get_scr_enabled() else UI.DISABLED)
		self.scr_unknown1_entry.pack(side=UI.LEFT)
		f.grid(row=0,column=3, columnspan=2, padx=5, sticky=UI.E)
		scrframe.grid(row=0,column=3, padx=2,pady=2, sticky=UI.N)
		otherframe.grid(row=3,column=0, columnspan=2, padx=3,pady=3, sticky=UI.EW)

		miscframe = UI.LabelFrame(self, text='Misc.')
		UI.Checkbutton(miscframe, text='Bring to Front', variable=self.flag_on_top).grid(row=0,column=0, sticky=UI.W)
		f = UI.Frame(miscframe)
		UI.Label(f, text='Control ID:').pack(side=UI.LEFT)
		UI.Entry(f, textvariable=self.identifier, font=UI.Font.fixed(), width=5).pack(side=UI.LEFT)
		f.grid(row=0,column=3, columnspan=2, padx=5, sticky=UI.E)
		UI.Checkbutton(miscframe, text='Unknown 0', variable=self.flag_unk1).grid(row=1,column=0, sticky=UI.W)
		UI.Checkbutton(miscframe, text='Unknown 2', variable=self.flag_unk2).grid(row=1,column=1, sticky=UI.W)
		UI.Checkbutton(miscframe, text='Unknown 5', variable=self.flag_unk3).grid(row=1,column=2, sticky=UI.W)
		UI.Checkbutton(miscframe, text='Unknown 12', variable=self.flag_unk4).grid(row=1,column=3, sticky=UI.W)
		UI.Checkbutton(miscframe, text='Unknown 15', variable=self.flag_unk5).grid(row=1,column=4, sticky=UI.W)
		UI.Checkbutton(miscframe, text='Unknown 17', variable=self.flag_unk6).grid(row=2,column=0, sticky=UI.W)
		UI.Checkbutton(miscframe, text='Unknown 27', variable=self.flag_unk7).grid(row=2,column=1, sticky=UI.W)
		UI.Checkbutton(miscframe, text='Unknown 28', variable=self.flag_unk8).grid(row=2,column=2, sticky=UI.W)
		UI.Checkbutton(miscframe, text='Unknown 29', variable=self.flag_unk9).grid(row=2,column=3, sticky=UI.W)
		UI.Checkbutton(miscframe, text='Unknown 31', variable=self.flag_unk10).grid(row=2,column=4, sticky=UI.W)
		miscframe.grid(row=4,column=0, columnspan=2, padx=3,pady=3, sticky=UI.NSEW)

		isdialog = self.widget.type == DialogBIN.BINWidget.TYPE_DIALOG
		if isimage or isdialog:
			self.advanced_widgets.extend((offsetframe,hotkeyframe,horframe,verframe,fontframe))
		if not isimage or isdialog:
			self.advanced_widgets.extend((transparent,findimage))
		if isdialog:
			self.advanced_widgets.append(otherframe)
		else:
			hassound = self.widget.type in (DialogBIN.BINWidget.TYPE_DEFAULT_BTN,DialogBIN.BINWidget.TYPE_BUTTON,DialogBIN.BINWidget.TYPE_OPTION_BTN,DialogBIN.BINWidget.TYPE_CHECKBOX,DialogBIN.BINWidget.TYPE_HIGHLIGHT_BTN,DialogBIN.BINWidget.TYPE_LISTBOX,DialogBIN.BINWidget.TYPE_SLIDER)
			if not hassound:
				self.advanced_widgets.append(soundframe)
			isbtn = self.widget.type in (DialogBIN.BINWidget.TYPE_DEFAULT_BTN,DialogBIN.BINWidget.TYPE_BUTTON,DialogBIN.BINWidget.TYPE_HIGHLIGHT_BTN)
			if not isbtn:
				self.advanced_widgets.extend((typeframe,soundframe,smkframe))
		self.advanced_widgets.append(scrframe)
		self.advanced_widgets.append(miscframe)

		bottom = UI.Frame(self)
		ok = UI.Button(bottom, text='Ok', width=10, command=self.ok)
		ok.pack(side=UI.LEFT, padx=1, pady=3)
		UI.Button(bottom, text='Update Preview', width=15, command=self.update_preview).pack(side=UI.LEFT, padx=3, pady=3)
		UI.Checkbutton(bottom, text='Advanced', variable=self.show_advanced, command=self.update_advanced).pack(side=UI.RIGHT, padx=1, pady=3)
		bottom.grid(row=5,column=0, columnspan=2, pady=3, padx=3, sticky=UI.EW)

		return ok

	def setup_complete(self) -> None:
		self.load_settings()
		self.load_properties()
		self.update_advanced()

	def update_advanced(self) -> None:
		self.minsize(0,0)
		self.maxsize(9999, 9999)
		initial_geometry = UI.Geometry.of(self)
		show = self.show_advanced.get()
		if show and not self.advanced_shown:
			for widget in self.advanced_widgets:
				widget.grid()
			self.string_label['text'] = 'Text/Image:'
			self.advanced_shown = True
		elif not show and self.advanced_shown:
			for widget in self.advanced_widgets:
				widget.grid_remove()
			self.string_label['text'] = 'Image:' if self.widget.type == DialogBIN.BINWidget.TYPE_IMAGE else 'Text:'
			self.advanced_shown = False
		self.update_idletasks()
		updated_geometry = UI.Geometry.of(self)
		self.geometry(updated_geometry.adjust_center_at(initial_geometry.center).text)
		self.minsize(updated_geometry.size.width, updated_geometry.size.height)
		self.maxsize(updated_geometry.size.width, updated_geometry.size.height)

	def calculate(self, calc: UI.IntegerVar, orig: UI.IntegerVar, offset: UI.IntegerVar, direction: int, *, fix: int, allow_advanced: bool = True) -> None:
		if not self.show_advanced.get() or allow_advanced:
			calc.set(orig.get() + offset.get() * direction + fix)

	def load_settings(self) -> None:
		config = self.delegate.get_config()
		self.show_advanced.set(config.edit.widget.advanced.value)
		config.windows.edit.widget.load_size(self)

	def save_settings(self) -> None:
		config = self.delegate.get_config()
		config.edit.widget.advanced.value = self.show_advanced.get()
		config.windows.edit.widget.save_size(self)

	def load_property_smk(self) -> None:
		smks = ['None']
		smk_id = 0
		if dialog_bin := self.delegate.get_bin():
			if self.widget.smk:
				smk_id = dialog_bin.smks.index(self.widget.smk)+1
			for smk in dialog_bin.smks:
				name = smk.filename
				if smk.overlay_smk:
					name += f" (Overlay: {smk.overlay_smk.filename})"
				smks.append(name)
		self.smks_dropdown.setentries(smks)
		self.smk.set(0 if not self.widget.smk else smk_id)

	def load_properties(self) -> None:
		self.left.set(self.widget.x1, True)
		self.right.set(self.widget.x2, True)
		self.width.set(self.widget.width, True)
		self.top.set(self.widget.y1, True)
		self.bottom.set(self.widget.y2, True)
		self.height.set(self.widget.height, True)
		self.string.set(TBL.decompile_string(self.widget.string))
		self.identifier.set(self.widget.identifier)
		self.scr_unknown1.set(self.widget.scr_unknown1)
		self.load_property_smk()
		self.text_offset_x.set(self.widget.text_offset_x)
		self.text_offset_y.set(self.widget.text_offset_y)
		self.responsive_left.set(self.widget.responsive_x1, True)
		self.responsive_right.set(self.widget.responsive_x2, True)
		self.responsive_width.set(self.widget.responsive_width, True)
		self.responsive_top.set(self.widget.responsive_y1, True)
		self.responsive_bottom.set(self.widget.responsive_y2, True)
		self.responsive_height.set(self.widget.responsive_height, True)

		self.flag_unk1.set((self.widget.flags & DialogBIN.BINWidget.FLAG_UNK1 == DialogBIN.BINWidget.FLAG_UNK1))
		self.flag_disabled.set((self.widget.flags & DialogBIN.BINWidget.FLAG_DISABLED == DialogBIN.BINWidget.FLAG_DISABLED))
		self.flag_unk2.set((self.widget.flags & DialogBIN.BINWidget.FLAG_UNK2 == DialogBIN.BINWidget.FLAG_UNK2))
		self.flag_visible.set((self.widget.flags & DialogBIN.BINWidget.FLAG_VISIBLE == DialogBIN.BINWidget.FLAG_VISIBLE))
		self.flag_responsive.set((self.widget.flags & DialogBIN.BINWidget.FLAG_RESPONSIVE == DialogBIN.BINWidget.FLAG_RESPONSIVE))
		self.flag_unk3.set((self.widget.flags & DialogBIN.BINWidget.FLAG_UNK3 == DialogBIN.BINWidget.FLAG_UNK3))
		self.flag_cancel_btn.set((self.widget.flags & DialogBIN.BINWidget.FLAG_CANCEL_BTN == DialogBIN.BINWidget.FLAG_CANCEL_BTN))
		self.flag_no_hover_snd.set((self.widget.flags & DialogBIN.BINWidget.FLAG_NO_HOVER_SND == DialogBIN.BINWidget.FLAG_NO_HOVER_SND))
		self.flag_virtual_hotkey.set((self.widget.flags & DialogBIN.BINWidget.FLAG_VIRTUAL_HOTKEY == DialogBIN.BINWidget.FLAG_VIRTUAL_HOTKEY))
		self.flag_has_hotkey.set((self.widget.flags & DialogBIN.BINWidget.FLAG_HAS_HOTKEY == DialogBIN.BINWidget.FLAG_HAS_HOTKEY))
		self.flag_font_size_10.set((self.widget.flags & DialogBIN.BINWidget.FLAG_FONT_SIZE_10 == DialogBIN.BINWidget.FLAG_FONT_SIZE_10))
		self.flag_font_size_16.set((self.widget.flags & DialogBIN.BINWidget.FLAG_FONT_SIZE_16 == DialogBIN.BINWidget.FLAG_FONT_SIZE_16))
		self.flag_unk4.set((self.widget.flags & DialogBIN.BINWidget.FLAG_UNK4 == DialogBIN.BINWidget.FLAG_UNK4))
		self.flag_transparency.set((self.widget.flags & DialogBIN.BINWidget.FLAG_TRANSPARENCY == DialogBIN.BINWidget.FLAG_TRANSPARENCY))
		self.flag_font_size_16x.set((self.widget.flags & DialogBIN.BINWidget.FLAG_FONT_SIZE_16x == DialogBIN.BINWidget.FLAG_FONT_SIZE_16x))
		self.flag_unk5.set((self.widget.flags & DialogBIN.BINWidget.FLAG_UNK5 == DialogBIN.BINWidget.FLAG_UNK5))
		self.flag_font_size_14.set((self.widget.flags & DialogBIN.BINWidget.FLAG_FONT_SIZE_14 == DialogBIN.BINWidget.FLAG_FONT_SIZE_14))
		self.flag_unk6.set((self.widget.flags & DialogBIN.BINWidget.FLAG_UNK6 == DialogBIN.BINWidget.FLAG_UNK6))
		self.flag_translucent.set((self.widget.flags & DialogBIN.BINWidget.FLAG_TRANSLUCENT == DialogBIN.BINWidget.FLAG_TRANSLUCENT))
		self.flag_default_btn.set((self.widget.flags & DialogBIN.BINWidget.FLAG_DEFAULT_BTN == DialogBIN.BINWidget.FLAG_DEFAULT_BTN))
		self.flag_on_top.set((self.widget.flags & DialogBIN.BINWidget.FLAG_ON_TOP == DialogBIN.BINWidget.FLAG_ON_TOP))
		self.flag_text_align_center.set((self.widget.flags & DialogBIN.BINWidget.FLAG_TEXT_ALIGN_CENTER == DialogBIN.BINWidget.FLAG_TEXT_ALIGN_CENTER))
		self.flag_text_align_right.set((self.widget.flags & DialogBIN.BINWidget.FLAG_TEXT_ALIGN_RIGHT == DialogBIN.BINWidget.FLAG_TEXT_ALIGN_RIGHT))
		self.flag_text_align_center2.set((self.widget.flags & DialogBIN.BINWidget.FLAG_TEXT_ALIGN_CENTER2 == DialogBIN.BINWidget.FLAG_TEXT_ALIGN_CENTER2))
		self.flag_align_top.set((self.widget.flags & DialogBIN.BINWidget.FLAG_ALIGN_TOP == DialogBIN.BINWidget.FLAG_ALIGN_TOP))
		self.flag_align_middle.set((self.widget.flags & DialogBIN.BINWidget.FLAG_ALIGN_MIDDLE == DialogBIN.BINWidget.FLAG_ALIGN_MIDDLE))
		self.flag_align_bottom.set((self.widget.flags & DialogBIN.BINWidget.FLAG_ALIGN_BOTTOM == DialogBIN.BINWidget.FLAG_ALIGN_BOTTOM))
		self.flag_unk7.set((self.widget.flags & DialogBIN.BINWidget.FLAG_UNK7 == DialogBIN.BINWidget.FLAG_UNK7))
		self.flag_unk8.set((self.widget.flags & DialogBIN.BINWidget.FLAG_UNK8 == DialogBIN.BINWidget.FLAG_UNK8))
		self.flag_unk9.set((self.widget.flags & DialogBIN.BINWidget.FLAG_UNK9 == DialogBIN.BINWidget.FLAG_UNK9))
		self.flag_no_click_snd.set((self.widget.flags & DialogBIN.BINWidget.FLAG_NO_CLICK_SND == DialogBIN.BINWidget.FLAG_NO_CLICK_SND))
		self.flag_unk10.set((self.widget.flags & DialogBIN.BINWidget.FLAG_UNK10 == DialogBIN.BINWidget.FLAG_UNK10))

	def save_property_smk(self) -> bool:
		assert (dialog_bin := self.delegate.get_bin())
		edited = False
		index = self.smk.get()-1
		smk = (None if index == -1 else dialog_bin.smks[index])
		if smk != self.widget.smk:
			self.widget.smk = smk
			edited = True
		return edited

	def save_properties(self) -> None:
		edited = False
		if self.left.get() != self.widget.x1:
			self.widget.x1 = self.left.get()
			edited = True
		if self.right.get() != self.widget.x2:
			self.widget.x2 = self.right.get()
			edited = True
		if self.width.get() != self.widget.width:
			self.widget.width = self.width.get()
			edited = True
		if self.top.get() != self.widget.y1:
			self.widget.y1 = self.top.get()
			edited = True
		if self.bottom.get() != self.widget.y2:
			self.widget.y2 = self.bottom.get()
			edited = True
		if self.height.get() != self.widget.height:
			self.widget.height = self.height.get()
			edited = True
		string = TBL.compile_string(self.string.get())
		if string != self.widget.string:
			self.widget.string = string
			edited = True
		if self.identifier.get() != self.widget.identifier:
			self.widget.identifier = self.identifier.get()
			edited = True
		if self.scr_unknown1.get() != self.widget.scr_unknown1:
			self.widget.scr_unknown1 = self.scr_unknown1.get()
			edited = True
		edited = edited or self.save_property_smk()
		if self.text_offset_x.get() != self.widget.text_offset_x:
			self.widget.text_offset_x = self.text_offset_x.get()
			edited = True
		if self.text_offset_y.get() != self.widget.text_offset_y:
			self.widget.text_offset_y = self.text_offset_y.get()
			edited = True
		if self.responsive_left.get() != self.widget.responsive_x1:
			self.widget.responsive_x1 = self.responsive_left.get()
			edited = True
		if self.responsive_right.get() != self.widget.responsive_x2:
			self.widget.responsive_x2 = self.responsive_right.get()
			edited = True
		if self.responsive_width.get() != self.widget.responsive_width:
			self.widget.responsive_width = self.responsive_width.get()
			edited = True
		if self.responsive_top.get() != self.widget.responsive_y1:
			self.widget.responsive_y1 = self.responsive_top.get()
			edited = True
		if self.responsive_bottom.get() != self.widget.responsive_y2:
			self.widget.responsive_y2 = self.responsive_bottom.get()
			edited = True
		if self.responsive_height.get() != self.widget.responsive_height:
			self.widget.responsive_height = self.responsive_height.get()
			edited = True

		flags = pack_flags((
			(self.flag_unk1.get(), DialogBIN.BINWidget.FLAG_UNK1),
			(self.flag_disabled.get(), DialogBIN.BINWidget.FLAG_DISABLED),
			(self.flag_unk2.get(), DialogBIN.BINWidget.FLAG_UNK2),
			(self.flag_visible.get(), DialogBIN.BINWidget.FLAG_VISIBLE),
			(self.flag_responsive.get(), DialogBIN.BINWidget.FLAG_RESPONSIVE),
			(self.flag_unk3.get(), DialogBIN.BINWidget.FLAG_UNK3),
			(self.flag_cancel_btn.get(), DialogBIN.BINWidget.FLAG_CANCEL_BTN),
			(self.flag_no_hover_snd.get(), DialogBIN.BINWidget.FLAG_NO_HOVER_SND),
			(self.flag_virtual_hotkey.get(), DialogBIN.BINWidget.FLAG_VIRTUAL_HOTKEY),
			(self.flag_has_hotkey.get(), DialogBIN.BINWidget.FLAG_HAS_HOTKEY),
			(self.flag_font_size_10.get(), DialogBIN.BINWidget.FLAG_FONT_SIZE_10),
			(self.flag_font_size_16.get(), DialogBIN.BINWidget.FLAG_FONT_SIZE_16),
			(self.flag_unk4.get(), DialogBIN.BINWidget.FLAG_UNK4),
			(self.flag_transparency.get(), DialogBIN.BINWidget.FLAG_TRANSPARENCY),
			(self.flag_font_size_16x.get(), DialogBIN.BINWidget.FLAG_FONT_SIZE_16x),
			(self.flag_unk5.get(), DialogBIN.BINWidget.FLAG_UNK5),
			(self.flag_font_size_14.get(), DialogBIN.BINWidget.FLAG_FONT_SIZE_14),
			(self.flag_unk6.get(), DialogBIN.BINWidget.FLAG_UNK6),
			(self.flag_translucent.get(), DialogBIN.BINWidget.FLAG_TRANSLUCENT),
			(self.flag_default_btn.get(), DialogBIN.BINWidget.FLAG_DEFAULT_BTN),
			(self.flag_on_top.get(), DialogBIN.BINWidget.FLAG_ON_TOP),
			(self.flag_text_align_center.get(), DialogBIN.BINWidget.FLAG_TEXT_ALIGN_CENTER),
			(self.flag_text_align_right.get(), DialogBIN.BINWidget.FLAG_TEXT_ALIGN_RIGHT),
			(self.flag_text_align_center2.get(), DialogBIN.BINWidget.FLAG_TEXT_ALIGN_CENTER2),
			(self.flag_align_top.get(), DialogBIN.BINWidget.FLAG_ALIGN_TOP),
			(self.flag_align_middle.get(), DialogBIN.BINWidget.FLAG_ALIGN_MIDDLE),
			(self.flag_align_bottom.get(), DialogBIN.BINWidget.FLAG_ALIGN_BOTTOM),
			(self.flag_unk7.get(), DialogBIN.BINWidget.FLAG_UNK7),
			(self.flag_unk8.get(), DialogBIN.BINWidget.FLAG_UNK8),
			(self.flag_unk9.get(), DialogBIN.BINWidget.FLAG_UNK9),
			(self.flag_no_click_snd.get(), DialogBIN.BINWidget.FLAG_NO_CLICK_SND),
			(self.flag_unk10.get(), DialogBIN.BINWidget.FLAG_UNK10),
		))
		if flags != self.widget.flags:
			self.widget.flags = flags
			edited = True

		self.node.string = None
		self.node.item_string_images = None

		if edited:
			self.delegate.mark_edited()

	def update_preview(self) -> None:
		self.save_properties()
		self.delegate.refresh_nodes()
		self.delegate.refresh_preview()

	def edit_smk(self) -> None:
		if not self.widget.smk:
			return
		SMKSettings(self, smk=self.widget.smk, widget=self.node, delegate=self)

	def add_smk(self) -> None:
		if not (dialog_bin := self.delegate.get_bin()):
			return
		smk = DialogBIN.BINSMK()
		dialog_bin.smks.append(smk)
		self.widget.smk = smk
		self.delegate.mark_edited()
		SMKSettings(self, smk=smk, widget=self.node, delegate=self)

	def ok(self, _event: UI.Event | None = None) -> None:
		self.update_preview()
		PyMSDialog.ok(self)

	def cancel(self, _event: UI.Event | None = None) -> None:
		self.ok()

	def dismiss(self) -> None:
		self.save_settings()
		PyMSDialog.dismiss(self)

	# MainDelegate
	def get_bin(self) -> (DialogBIN.DialogBIN | None):
		return self.delegate.get_bin()

	def get_config(self) -> PyBINConfig:
		return self.delegate.get_config()

	def get_mpqhandler(self) -> MPQHandler:
		return self.delegate.get_mpqhandler()

	def get_scr_enabled(self) -> bool:
		return self.delegate.get_scr_enabled()

	def mark_edited(self) -> None:
		self.delegate.mark_edited()

	def refresh_preview(self) -> None:
		self.delegate.refresh_preview()

	def refresh_smks(self) -> None:
		self.load_property_smk()
		self.delegate.refresh_smks()

	def refresh_nodes(self) -> None:
		self.delegate.refresh_nodes()
