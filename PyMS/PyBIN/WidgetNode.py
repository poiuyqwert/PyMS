
from __future__ import annotations

from .Delegates import NodeDelegate
from .StringPreview import StringPreview

from ..FileFormats import DialogBIN, TBL, SMK, GRP, PCX, FNT

from ..Utilities.UIKit import *

import sys

from typing import cast

class WidgetNode:
	SMK_FRAME_CACHE: dict[str, dict[int, ImageTk.PhotoImage]] = {}

	def __init__(self, delegate: NodeDelegate, widget: DialogBIN.BINWidget | None = None) -> None:
		self.delegate = delegate
		self.widget = widget
		self.parent: WidgetNode | None = None
		self.name = None
		self.index: str | None = None
		self.children: list[WidgetNode] | None
		if widget and widget.type != DialogBIN.BINWidget.TYPE_DIALOG:
			self.children = None
		else:
			self.children = []

		self.string: StringPreview | None = None
		self.photo: ImageTk.PhotoImage | None = None
		self.smks: dict[str, SMK.SMK] | None = None
		self.dialog_image: ImageTk.PhotoImage | None = None
		self.frame_delay: int | None = None
		self.frame_waited = 0.0

		self.item_bounds: Canvas.Item | None = None # type: ignore[name-defined]
		self.item_text_bounds: Canvas.Item | None = None # type: ignore[name-defined]
		self.item_responsive_bounds: Canvas.Item | None = None # type: ignore[name-defined]
		self.item_string_images: list[Canvas.Item] | None = None # type: ignore[name-defined]
		self.item_image: Canvas.Item | None = None # type: ignore[name-defined]
		self.item_smks: list[Canvas.Item] = [] # type: ignore[name-defined]
		self.item_dialog: Canvas.Item | None = None # type: ignore[name-defined]

	def get_name(self) -> str:
		name = 'Group'
		if self.widget:
			name = DialogBIN.BINWidget.TYPE_NAMES[self.widget.type]
			display_text = self.widget.display_text()
			if display_text:
				name = '%s [%s]' % (TBL.decompile_string(display_text),name)
		if self.name:
			name = '%s [%s]' % self.name
		return name

	def remove_from_parent(self) -> None:
		if not self.parent or self.parent.children is None:
			return
		self.parent.children.remove(self)
		self.parent = None

	def add_child(self, node: WidgetNode, index: int = -1):
		if self.children is None:
			return
		node.remove_from_parent()
		node.parent = self
		if index == -1:
			self.children.append(node)
		else:
			self.children.insert(index, node)

	def visible(self) -> bool:
		if self.widget and not self.widget.flags & DialogBIN.BINWidget.FLAG_VISIBLE:
			return self.delegate.get_show_hidden()
		return True

	def enabled(self) -> bool:
		if self.widget and self.widget.flags & DialogBIN.BINWidget.FLAG_DISABLED:
			return False
		return True

	def bounding_box(self) -> tuple[int, int, int, int]:
		if self.widget:
			return self.widget.bounding_box()
		if self.children is None:
			return (0,0,0,0)
		x1 = sys.maxsize
		y1 = sys.maxsize
		x2 = 0
		y2 = 0
		for node in self.children:
			cx1,cy1,cx2,cy2 = node.bounding_box()
			if cx1 < x1:
				x1 = cx1
			if cy1 < y1:
				y1 = cy1
			if cx2 > x2:
				x2 = cx2
			if cy2 > y2:
				y2 = cy2
		return (x1,y1,x2,y2)

	def text_box(self) -> tuple[int, int, int, int]:
		x1,y1,x2,y2 = self.bounding_box()
		if self.widget:
			x1 += self.widget.text_offset_x
			y1 += self.widget.text_offset_y
			if self.widget.type == DialogBIN.BINWidget.TYPE_CHECKBOX:
				image = self.delegate.get_dialog_asset(DialogBIN.DIALOG_ASSET_CHECK_SELECTED)
				if image:
					x1 += image.size[0] + 4
			elif self.widget.type == DialogBIN.BINWidget.TYPE_OPTION_BTN:
				image = self.delegate.get_dialog_asset(DialogBIN.DIALOG_ASSET_RADIO_SELECTED)
				if image:
					x1 += image.size[0] + 4
		return (x1,y1,x2,y2)

	def update_dialog(self) -> bool:
		reorder = False
		self.dialog_image = None
		if self.widget and self.visible():
			x1,y1,x2,y2 = self.bounding_box()
			x = x1
			y = y1
			anchor: Anchor = NW
			if self.widget.type == DialogBIN.BINWidget.TYPE_CHECKBOX:
				asset_id = DialogBIN.DIALOG_ASSET_CHECK_DISABLED
				if self.enabled():
					asset_id = DialogBIN.DIALOG_ASSET_CHECK_SELECTED
				pil = self.delegate.get_dialog_asset(asset_id)
				if pil:
					self.dialog_image = ImageTk.PhotoImage(pil)
					y += (y2 - y1) // 2
					anchor = W
			elif self.widget.type == DialogBIN.BINWidget.TYPE_OPTION_BTN:
				asset_id = DialogBIN.DIALOG_ASSET_RADIO_DISABLED
				if self.enabled():
					asset_id = DialogBIN.DIALOG_ASSET_RADIO_SELECTED
				pil = self.delegate.get_dialog_asset(asset_id)
				if pil:
					self.dialog_image = ImageTk.PhotoImage(pil)
					y += (y2 - y1) // 2
					anchor = W
			elif self.widget.type == DialogBIN.BINWidget.TYPE_SLIDER:
				if self.enabled():
					left = self.delegate.get_dialog_asset(DialogBIN.DIALOG_ASSET_SLIDER_LEFT)
					mid = self.delegate.get_dialog_asset(DialogBIN.DIALOG_ASSET_SLIDER_MIDDLE)
					spot = self.delegate.get_dialog_asset(DialogBIN.DIALOG_ASSET_SLIDER_SPOT)
					right = self.delegate.get_dialog_asset(DialogBIN.DIALOG_ASSET_SLIDER_RIGHT)
					dot = self.delegate.get_dialog_asset(DialogBIN.DIALOG_ASSET_SLIDER_DOT_YELLOW)
				else:
					left = self.delegate.get_dialog_asset(DialogBIN.DIALOG_ASSET_SLIDER_LEFT_DISABLED)
					mid = self.delegate.get_dialog_asset(DialogBIN.DIALOG_ASSET_SLIDER_MIDDLE_DISABLED)
					spot = self.delegate.get_dialog_asset(DialogBIN.DIALOG_ASSET_SLIDER_SPOT_DISABLED)
					right = self.delegate.get_dialog_asset(DialogBIN.DIALOG_ASSET_SLIDER_RIGHT_DISABLED)
					dot = self.delegate.get_dialog_asset(DialogBIN.DIALOG_ASSET_SLIDER_DOT_DISABLED)
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
						spots_padding = (width - left.size[0] - right.size[0] - spot.size[0] * (spots+1)) // spots
					draw_x = 0
					mid_y = height // 2
					pil = PILImage.new('RGBA', (width,height))
					pil.paste(left, (draw_x,mid_y - left.size[1]//2))
					draw_x += left.size[0]
					while spots >= 0:
						pil.paste(spot, (draw_x,mid_y - spot.size[1]//2))
						draw_x += spot.size[0]
						if spots and spots_padding > 0:
							pad = mid.resize((spots_padding, mid.size[1]))
							pil.paste(pad, (draw_x,mid_y - pad.size[1]//2))
							draw_x += pad.size[0]
						spots -= 1
					pil.paste(right, (draw_x,mid_y - right.size[1]//2))
					if dot:
						pil.paste(dot, ((width - dot.size[0])//2, mid_y - dot.size[1]//2))
					self.dialog_image = ImageTk.PhotoImage(pil)
					y += (y2 - y1) // 2
					anchor = W
			elif self.widget.type in (DialogBIN.BINWidget.TYPE_BUTTON,DialogBIN.BINWidget.TYPE_DEFAULT_BTN):
				if self.enabled():
					left = self.delegate.get_dialog_asset(DialogBIN.DIALOG_ASSET_BUTTON_MID_LEFT)
					mid = self.delegate.get_dialog_asset(DialogBIN.DIALOG_ASSET_BUTTON_MID_MIDDLE)
					right = self.delegate.get_dialog_asset(DialogBIN.DIALOG_ASSET_BUTTON_MID_RIGHT)
				else:
					left = self.delegate.get_dialog_asset(DialogBIN.DIALOG_ASSET_BUTTON_MID_DISABLED_LEFT)
					mid = self.delegate.get_dialog_asset(DialogBIN.DIALOG_ASSET_BUTTON_MID_DISABLED_MIDDLE)
					right = self.delegate.get_dialog_asset(DialogBIN.DIALOG_ASSET_BUTTON_MID_DISABLED_RIGHT)
				if left and mid and right:
					width = x2-x1
					height = 0
					for img in (left,mid,right):
						height = max(height, img.size[1])
					mid_y = height // 2
					pil = PILImage.new('RGBA', (width,height))
					pil.paste(left, (0,mid_y - left.size[1]//2))
					pad_size = width-left.size[0]-right.size[0]
					if pad_size > 0:
						pad = mid.resize((pad_size,mid.size[1]))
						pil.paste(pad, (left.size[0],mid_y - pad.size[1]//2))
					pil.paste(right, (width-right.size[0],mid_y - right.size[1]//2))
					self.dialog_image = ImageTk.PhotoImage(pil)
					y += (y2 - y1) // 2
					anchor = W
			elif self.widget.type == DialogBIN.BINWidget.TYPE_LISTBOX:
				top = self.delegate.get_dialog_asset(DialogBIN.DIALOG_ASSET_SCROLL_VERTICAL_TOP)
				mid = self.delegate.get_dialog_asset(DialogBIN.DIALOG_ASSET_SCROLL_VERTICAL_MIDDLE)
				bot = self.delegate.get_dialog_asset(DialogBIN.DIALOG_ASSET_SCROLL_VERTICAL_BOTTOM)
				bar = self.delegate.get_dialog_asset(DialogBIN.DIALOG_ASSET_SCROLL_BAR)
				if self.enabled():
					up = self.delegate.get_dialog_asset(DialogBIN.DIALOG_ASSET_SCROLL_UP)
					down = self.delegate.get_dialog_asset(DialogBIN.DIALOG_ASSET_SCROLL_DOWN)
				else:
					up = self.delegate.get_dialog_asset(DialogBIN.DIALOG_ASSET_SCROLL_UP_DISABLED)
					down = self.delegate.get_dialog_asset(DialogBIN.DIALOG_ASSET_SCROLL_DOWN_DISABLED)
				if top and mid and bot and bar and up and down:
					width = 0
					height = y2-y1
					for img in (top,mid,bot,bar,up,down):
						width = max(width, img.size[0])
					mid_x = width // 2
					pil = PILImage.new('RGBA', (width,height))
					pil.paste(up, (mid_x-up.size[0]//2,0))
					pil.paste(top, (mid_x-top.size[0]//2,up.size[1]+2))
					mid_height = height - up.size[1] - 2 - top.size[1] - bot.size[1] - 2 - down.size[1]
					if mid_height > 0:
						mid_full = mid.resize((mid.size[0],mid_height))
						pil.paste(mid_full, (mid_x-mid.size[0]//2,up.size[1]+2+top.size[1]))
					pil.paste(bot, (mid_x-bot.size[0]//2,height-down.size[1]-2-bot.size[1]))
					pil.paste(down, (mid_x-down.size[0]//2,height-down.size[1]))
					pil.paste(bar, (mid_x-bar.size[0]//2,up.size[1]+4))
					self.dialog_image = ImageTk.PhotoImage(pil)
					x = x2
					y += (y2 - y1) // 2
					anchor = E
			elif self.widget.type == DialogBIN.BINWidget.TYPE_COMBOBOX:
				left = self.delegate.get_dialog_asset(DialogBIN.DIALOG_ASSET_COMBOBOX_LEFT)
				middle = self.delegate.get_dialog_asset(DialogBIN.DIALOG_ASSET_COMBOBOX_MIDDLE)
				right = self.delegate.get_dialog_asset(DialogBIN.DIALOG_ASSET_COMBOBOX_RIGHT)
				if self.enabled():
					arrow = self.delegate.get_dialog_asset(DialogBIN.DIALOG_ASSET_COMBOBOX_ARROW)
				else:
					arrow = self.delegate.get_dialog_asset(DialogBIN.DIALOG_ASSET_COMBOBOX_ARROW_DISABLED)
				if left and middle and right and arrow:
					width = x2-x1
					height = 0
					for img in (left,middle,right,arrow):
						height = max(height, img.size[1])
					mid_y = height // 2
					pil = PILImage.new('RGBA', (width,height))
					pil.paste(left, (0,mid_y - left.size[1]//2))
					pad_size = width-left.size[0]-right.size[0]
					if pad_size > 0:
						pad = middle.resize((pad_size,middle.size[1]))
						pil.paste(pad, (left.size[0],mid_y - pad.size[1]//2))
					pil.paste(right, (width-right.size[0],mid_y - right.size[1]//2))
					pil.paste(arrow, (width-arrow.size[0]-5,mid_y - arrow.size[1]//2))
					self.dialog_image = ImageTk.PhotoImage(pil)
					y += (y2 - y1) // 2
					anchor = W
			elif self.widget.type == DialogBIN.BINWidget.TYPE_DIALOG and self.delegate.get_show_dialog():
				tl = self.delegate.get_dialog_frame(DialogBIN.DIALOG_FRAME_TL)
				t = self.delegate.get_dialog_frame(DialogBIN.DIALOG_FRAME_T)
				tr = self.delegate.get_dialog_frame(DialogBIN.DIALOG_FRAME_TR)
				l = self.delegate.get_dialog_frame(DialogBIN.DIALOG_FRAME_L)
				m = self.delegate.get_dialog_frame(DialogBIN.DIALOG_FRAME_M)
				r = self.delegate.get_dialog_frame(DialogBIN.DIALOG_FRAME_R)
				bl = self.delegate.get_dialog_frame(DialogBIN.DIALOG_FRAME_BL)
				b = self.delegate.get_dialog_frame(DialogBIN.DIALOG_FRAME_B)
				br = self.delegate.get_dialog_frame(DialogBIN.DIALOG_FRAME_BR)
				if tl and t and tr and l and m and r and bl and b and br:
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
					self.delegate.node_render_image_update(self.item_dialog, x, y, self.dialog_image)
				else:
					self.delegate.node_render_image_create(x, y, self.dialog_image, anchor)
					reorder = True
		if self.dialog_image is None and self.item_dialog:
			self.delegate.node_render_delete(self.item_dialog)
			self.item_dialog = None
		return reorder

	def tick(self, dt: float) -> None:
		SHOW_SMKS = self.delegate.get_show_smks()
		SHOW_ANIMATED = self.delegate.get_show_animated()
		if not SHOW_SMKS or not SHOW_ANIMATED or not self.smks or not self.widget or not self.widget.smk:
			return
		self.frame_waited += dt
		if self.frame_delay is None or self.frame_waited < self.frame_delay:
			return
		for smk in list(self.smks.values()):
			if smk.current_frame < smk.frames or self.widget.smk.flags & DialogBIN.BINSMK.FLAG_REPEATS:
				# while self.frame_waited > self.frame_delay:
					smk.next_frame()
					# self.frame_waited -= self.frame_delay
		self.frame_waited = 0

	def update_video(self) -> bool:
		reorder = False
		SHOW_SMKS = self.delegate.get_show_smks()
		SHOW_HOVER_SMKS = self.delegate.get_show_animated()
		showing: list[tuple[DialogBIN.BINSMK, SMK.SMK]] = []
		if SHOW_SMKS and self.widget and self.widget.type == DialogBIN.BINWidget.TYPE_HIGHLIGHT_BTN and self.widget.smk and self.visible():
			if self.smks is None:
				self.smks = {}
			check: DialogBIN.BINSMK | None = self.widget.smk
			while check:
				if not check.flags & DialogBIN.BINSMK.FLAG_SHOW_ON_HOVER or SHOW_HOVER_SMKS:
					if not check.filename in self.smks:
						try:
							smk = SMK.SMK()
							smk.load_file(self.delegate.get_mpqhandler().get_file('MPQ:' + check.filename))
							delay = int(1000 / float(smk.fps))
							if self.frame_delay is None:
								self.frame_delay = delay
							else:
								self.frame_delay = min(self.frame_delay,delay)
							self.smks[check.filename] = smk
						except:
							self.delegate.capture_exception()
					show_smk = self.smks.get(check.filename)
					if show_smk:
						showing.append((check, show_smk))
				check = check.overlay_smk
		while len(self.item_smks) > len(showing):
			self.delegate.node_render_delete(self.item_smks[-1])
			del self.item_smks[-1]
		for i,(bin_smk,smk) in enumerate(showing):
			frame = smk.get_frame()
			# trans = ((self.widget.flags & DialogBIN.BINWidget.FLAG_TRANSPARENCY) == DialogBIN.BINWidget.FLAG_TRANSPARENCY)
			trans = False
			if bin_smk.filename in WidgetNode.SMK_FRAME_CACHE and smk.current_frame in WidgetNode.SMK_FRAME_CACHE[bin_smk.filename]:
				image = WidgetNode.SMK_FRAME_CACHE[bin_smk.filename][smk.current_frame]
			else:
				image = cast(ImageTk.PhotoImage, GRP.frame_to_photo(frame.palette, frame.image, None, size=False, trans=trans))
				if not bin_smk.filename in WidgetNode.SMK_FRAME_CACHE:
					WidgetNode.SMK_FRAME_CACHE[bin_smk.filename] = {}
				WidgetNode.SMK_FRAME_CACHE[bin_smk.filename][smk.current_frame] = image
			assert self.widget is not None
			x1,y1,_,_ = self.widget.bounding_box()
			x1 += bin_smk.offset_x
			y1 += bin_smk.offset_y
			if i < len(self.item_smks):
				self.delegate.node_render_image_update(self.item_smks[i], x1, y1, image)
			else:
				item = self.delegate.node_render_image_create(x1, y1, image, NW)
				self.item_smks.append(item)
				# self.toplevel.widgetCanvas.create_rectangle(x1,y1,x1+self.smk.width,y1+self.smk.height, width=1, outline='#FFFF00')
				reorder = True
		return reorder

	def update_image(self) -> bool:
		reorder = False
		SHOW_IMAGES = self.delegate.get_show_images()
		if SHOW_IMAGES and self.widget and self.widget.type == DialogBIN.BINWidget.TYPE_IMAGE and self.visible() and self.widget.string:
			photo_change = False
			if self.photo is None:
				try:
					pcx = PCX.PCX()
					pcx.load_file(self.delegate.get_mpqhandler().load_file('MPQ:' + self.widget.string))
					trans = ((self.widget.flags & DialogBIN.BINWidget.FLAG_TRANSPARENCY) == DialogBIN.BINWidget.FLAG_TRANSPARENCY)
					self.photo = cast(ImageTk.PhotoImage, GRP.frame_to_photo(pcx.palette, pcx, -1, size=False, trans=trans))
					photo_change = True
				except:
					self.delegate.capture_exception()
			if self.photo:
				x1,y1,_,_ = self.bounding_box()
				if self.item_image:
					self.delegate.node_render_image_update(self.item_image, x1, y1, self.photo)
				else:
					self.item_image = self.delegate.node_render_image_create(x1, y1, self.photo, NW)
					reorder = True
		elif self.item_image:
			self.delegate.node_render_delete(self.item_image)
			self.item_image = None
		return reorder

	def update_text(self) -> bool:
		reorder = False
		SHOW_TEXT = self.delegate.get_show_text()
		if SHOW_TEXT and self.widget and self.widget.display_text() and self.visible():
			if self.string is None:
				font = self.delegate.get_font(self.widget.flags)
				tfontgam = self.delegate.get_tfontgam()
				remap_pal = tfontgam
				remap = FNT.COLOR_CODES_INGAME
				if tfont := self.delegate.get_tfont():
					remap_pal = tfont
					remap = FNT.COLOR_CODES_GLUE
				default_color = 2
				if self.widget.type in (DialogBIN.BINWidget.TYPE_BUTTON,DialogBIN.BINWidget.TYPE_COMBOBOX,DialogBIN.BINWidget.TYPE_DEFAULT_BTN,DialogBIN.BINWidget.TYPE_OPTION_BTN,DialogBIN.BINWidget.TYPE_HIGHLIGHT_BTN):
					default_color = 3
				self.string = StringPreview(self.widget.display_text() or '', font, tfontgam, remap, remap_pal, default_color)
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
					self.delegate.node_render_image_update(item, position[0], position[1], None)
			else:
				self.item_string_images = []
				glyphs = self.string.get_glyphs()
				for glyph,position in zip(glyphs,positions):
					self.item_string_images.append(self.delegate.node_render_image_create(position[0], position[1], glyph, NW))
				reorder = True
		elif self.item_string_images:
			for item in self.item_string_images:
				self.delegate.node_render_delete(item)
			self.item_string_images = None
		return reorder

	def update_bounds(self) -> bool:
		reorder = False
		SHOW_BOUNDING_BOX = self.delegate.get_show_bounds_widget()
		SHOW_GROUP_BOUNDS = self.delegate.get_show_bounds_group()
		if SHOW_BOUNDING_BOX and (self.widget or SHOW_GROUP_BOUNDS):
			x1,y1,x2,y2 = self.bounding_box()
			if self.item_bounds:
				self.delegate.node_render_rect_update(self.item_bounds, x1, y1, x2, y2)
			else:
				color = '#505050'
				if self.widget:
					color = '#0080ff'
					if self.widget.type == DialogBIN.BINWidget.TYPE_DIALOG:
						color = '#00A0A0'
				self.item_bounds = self.delegate.node_render_rect_create(x1, y1, x2, y2, color)
				reorder = True
		elif self.item_bounds:
			self.delegate.node_render_delete(self.item_bounds)
			self.item_bounds = None
		return reorder

	def update_text_bounds(self) -> bool:
		reorder = False
		SHOW_TEXT_BOUNDS = self.delegate.get_show_bounds_text()
		if SHOW_TEXT_BOUNDS and self.widget and self.widget.display_text() is not None:
			x1,y1,x2,y2 = self.text_box()
			if self.item_text_bounds:
				self.delegate.node_render_rect_update(self.item_text_bounds, x1, y1, x2, y2)
			else:
				self.item_text_bounds = self.delegate.node_render_rect_create(x1, y1, x2, y2, '#F0F0F0')
				reorder = True
		elif self.item_text_bounds:
			self.delegate.node_render_delete(self.item_text_bounds)
			self.item_text_bounds = None
		return reorder

	def update_responsive_bounds(self) -> bool:
		reorder = False
		SHOW_RESPONSIVE_BOUNDS = self.delegate.get_show_bounds_responsive()
		if SHOW_RESPONSIVE_BOUNDS and self.widget and self.widget.has_responsive():
			x1,y1,x2,y2 = self.widget.responsive_box()
			if self.item_responsive_bounds:
				self.delegate.node_render_rect_update(self.item_responsive_bounds, x1, y1, x2, y2)
			else:
				self.item_responsive_bounds = self.delegate.node_render_rect_create(x1, y1, x2, y2, '#00FF80')
				reorder = True
		elif self.item_responsive_bounds:
			self.delegate.node_render_delete(self.item_responsive_bounds)
			self.item_responsive_bounds = None
		return reorder

	def update_display(self) -> bool:
		reorder = False
		reorder = self.update_dialog() or reorder
		reorder = self.update_image() or reorder
		reorder = self.update_video() or reorder
		reorder = self.update_text() or reorder
		reorder = self.update_bounds() or reorder
		reorder = self.update_text_bounds() or reorder
		reorder = self.update_responsive_bounds() or reorder
		return reorder

	def lift(self) -> None:
		if self.item_dialog:
			self.delegate.node_render_lift(self.item_dialog)
		if self.item_image:
			self.delegate.node_render_lift(self.item_image)
		if self.item_smks:
			for item in self.item_smks:
				self.delegate.node_render_lift(item)
		if self.item_string_images:
			for item in self.item_string_images:
				self.delegate.node_render_lift(item)
		if self.item_bounds:
			self.delegate.node_render_lift(self.item_bounds)
		if self.item_text_bounds:
			self.delegate.node_render_lift(self.item_text_bounds)
		if self.item_responsive_bounds:
			self.delegate.node_render_lift(self.item_responsive_bounds)

	def remove_display(self) -> None:
		if self.item_dialog:
			self.delegate.node_render_delete(self.item_dialog)
			self.item_dialog = None
		if self.item_image:
			self.delegate.node_render_delete(self.item_image)
			self.item_image = None
		if self.item_smks:
			for item in self.item_smks:
				self.delegate.node_render_delete(item)
			self.item_smks = []
		if self.item_string_images:
			for item in self.item_string_images:
				self.delegate.node_render_delete(item)
			self.item_string_images = []
		if self.item_bounds:
			self.delegate.node_render_delete(self.item_bounds)
			self.item_bounds = None
		if self.item_text_bounds:
			self.delegate.node_render_delete(self.item_text_bounds)
			self.item_text_bounds = None
		if self.item_responsive_bounds:
			self.delegate.node_render_delete(self.item_responsive_bounds)
			self.item_responsive_bounds = None
