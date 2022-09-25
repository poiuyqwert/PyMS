
from .StringPreview import StringPreview

from ..FileFormats import DialogBIN, TBL, SMK, GRP, PCX, FNT

from ..Utilities.UIKit import *
from ..Utilities.InternalErrorDialog import InternalErrorDialog

import sys

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
			x1,y1,_,_ = self.widget.bounding_box()
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
				x1,y1,_,_ = self.bounding_box()
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
