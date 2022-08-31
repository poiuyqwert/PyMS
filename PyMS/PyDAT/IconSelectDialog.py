
from .DataContext import DataContext

from ..Utilities.UIKit import *
from ..Utilities.PyMSDialog import PyMSDialog
from ..Utilities.ScrolledCanvas import ScrolledCanvas
from ..Utilities.StatusBar import StatusBar
from ..Utilities.ShowScrollbar import ShowScrollbar

from math import floor, ceil

class IconSelectDialog(PyMSDialog):
	# If `none_index` is not `None`, then an empty icon will be shown and its index when selected will be `none_index`
	def __init__(self, parent, data_context, delegate, selected_index, none_index=None): # type: (Toplevel, DataContext, Callable[[int], None], int, int) -> IconSelectDialog
		self.data_context = data_context
		self.delegate = delegate
		self._initial_selection = selected_index
		self.selected_index = selected_index
		self.none_index = none_index
		self._last_display_parameters = None
		PyMSDialog.__init__(self, parent, 'Choose Icon', set_min_size=(True,True))

	def widgetize(self):
		icon_size = self.data_context.cmdicons.frame_size()
		self.scrolled_canvas = ScrolledCanvas(self, horizontal=ShowScrollbar.never, width=icon_size[0] * 10, height=icon_size[1] * 5, background='#000000')
		self.scrolled_canvas.pack(side=TOP, fill=BOTH, expand=1)
		self.selection_box_item = self.scrolled_canvas.canvas.create_rectangle(0, 0, 0, 0, outline='#FFFFFF')

		buttonframe = Frame(self)
		Button(buttonframe, text='Ok', width=10, command=self.ok).pack(side=LEFT, pady=5, padx=3)
		Button(buttonframe, text='Cancel', width=10, command=self.cancel).pack(side=LEFT, padx=3, pady=3)
		buttonframe.pack()

		self.status_selection = StringVar()
		self.status_hover = StringVar()

		statusbar = StatusBar(self)
		statusbar.add_label(self.status_selection, weight=0.5)
		statusbar.add_label(self.status_hover, weight=0.5)
		statusbar.pack(side=BOTTOM, fill=X)

	def setup_complete(self):
		icon_size = self.data_context.cmdicons.frame_size()
		max_width = self.winfo_width() + 5 * icon_size[0]
		max_height = self.winfo_height() + 10 * icon_size[1]
		self.maxsize(max_width, max_height)
		self.data_context.settings.windows.load_window_size('icon_select', self)

		self.scrolled_canvas.canvas.bind(Mouse.Click_Left, self._select_icon)
		self.scrolled_canvas.canvas.bind(Double.Click_Left, lambda *_: self.ok())
		self.scrolled_canvas.canvas.bind(Mouse.Motion, self._update_status_hover)
		self.scrolled_canvas.canvas.bind(Cursor.Leave, lambda *_: self._clear_status_hover())
		self.scrolled_canvas.canvas.bind(WidgetEvent.Configure, lambda *_: self._canvas_resized())
		self.scrolled_canvas.canvas.bind(WidgetEvent.Scrolled, lambda *_: self._draw_icons())
		
		self._update_status_selection()
		self.scrolled_canvas.canvas.update_idletasks()
		self._scroll_to_selection()

	def _icon_size(self):
		return self.data_context.cmdicons.frame_size()

	def _icon_count(self):
		icon_count = self.data_context.cmdicons.frame_count()
		if self.none_index != None:
			icon_count += 1
		return icon_count

	def _display_index_to_frame_index(self, display_index):
		frame_index = display_index
		if self.none_index != None:
			frame_index -= 1
		return frame_index

	def _selected_index_to_display_index(self, selected_index):
		display_index = selected_index
		if self.none_index != None:
			if display_index == self.none_index:
				display_index = 0
			else:
				display_index += 1
		return display_index

	def _display_index_to_selected_index(self, display_index):
		selected_index = display_index
		if self.none_index != None:
			if selected_index == 0:
				selected_index = self.none_index
			else:
				selected_index -= 1
		return selected_index

	def _calculate_visibility(self): # type: () -> tuple[int, int, int, int, int]
		"""Returns: (columns, total_height, start_y, visible_start_index, visible_end_index)"""
		icon_size = self._icon_size()
		icon_count = self._icon_count()
		width = self.scrolled_canvas.canvas.winfo_width()
		columns = int(floor(width / icon_size[0]))
		if not columns:
			return (0, 0, 0, 0, 0)
		total_rows = int(ceil(icon_count / float(columns)))
		total_height = total_rows * icon_size[1]
		top_y = int(self.scrolled_canvas.canvas.yview()[0] * total_height)
		start_y = floor(top_y / icon_size[1]) * icon_size[1]
		visible_start_row = int(floor(start_y / icon_size[1]))
		height = self.scrolled_canvas.canvas.winfo_height()
		visible_row_count = int(ceil((height + top_y - start_y) / float(icon_size[1])))
		visible_start_index = columns * visible_start_row
		visible_icon_count = min(icon_count - visible_start_index, visible_row_count * columns)
		return (columns, total_height, start_y, visible_start_index, visible_start_index + visible_icon_count - 1)

	def _scroll_to_selection(self):
		display_index = self._selected_index_to_display_index(self.selected_index)
		icon_size = self._icon_size()
		columns, total_height, _, _, _ = self._calculate_visibility()
		if columns == 0:
			return
		viewport_height = self.scrolled_canvas.canvas.winfo_height()
		y = max(0,min(total_height,(display_index / columns + 0.5) * icon_size[1] - viewport_height/2.0))
		self.scrolled_canvas.canvas.yview_moveto(y / total_height)

	def _calculate_scrollregion(self):
		columns, height, _, _, _ = self._calculate_visibility()
		if not columns:
			return (0,0)
		icon_size = self._icon_size()
		return (columns * icon_size[0], height)

	def _update_selection_box(self):
		display_index = self._selected_index_to_display_index(self.selected_index)
		columns, _, start_y, visible_start_index, _ = self._calculate_visibility()
		icon_size = self._icon_size()
		x = ((display_index - visible_start_index) % columns) * icon_size[0]
		y = start_y + floor((display_index - visible_start_index) / float(columns)) * icon_size[1]
		self.selection_box_item.coords(x, y, x + icon_size[0], y + icon_size[1])
		self.selection_box_item.tag_lower()

	def _display_index_to_tag(self, display_index):
		return 'icon%d' % display_index

	def _draw_icons(self, force=False):
		columns, _, start_y, visible_start_index, visible_end_index = self._calculate_visibility()
		display_parameters = (columns, visible_start_index, visible_end_index)
		if force or display_parameters == self._last_display_parameters:
			return
		last_start_index = 9999
		last_end_index = -1
		if self._last_display_parameters:
			_, last_start_index, last_end_index = self._last_display_parameters
		self._last_display_parameters = display_parameters
		start_index = min(visible_start_index, last_start_index)
		end_index = max(visible_end_index, last_end_index)
		icon_size = self._icon_size()
		for index in range(start_index, end_index + 1):
			if self.none_index != None and index == 0:
				continue
			was_visible = (index >= last_start_index and index <= last_end_index)
			is_visible = (index >= visible_start_index and index <= visible_end_index)
			tag = self._display_index_to_tag(index)
			if is_visible:
				x = ((index - visible_start_index) % columns) * icon_size[0]
				y = start_y + floor((index - visible_start_index) / float(columns)) * icon_size[1]
				frame_index = self._display_index_to_frame_index(index)
				icon, dx, dx2, dy, dy2 = tuple(self.data_context.get_cmdicon(frame_index, highlighted=(self._display_index_to_selected_index(index) == self.selected_index)))
				x += icon_size[0] / 2 - dx - (dx2 - dx) / 2
				y += icon_size[1] / 2 - dy - (dy2 - dy) / 2
				if was_visible:
					self.scrolled_canvas.canvas.coords(tag, x,y)
				else:
					self.scrolled_canvas.canvas.create_image(x,y, image=icon, tags=tag, anchor=NW)
			else:
				self.scrolled_canvas.canvas.delete(tag)
		self.selection_box_item.tag_raise()

	def _redraw_selection(self, old_selection, new_selection):
		_, start_index, end_index = self._last_display_parameters
		old_display_index = self._selected_index_to_display_index(old_selection)
		if old_display_index >= start_index and old_display_index <= end_index:
			frame_index = self._display_index_to_frame_index(old_display_index)
			icon, _, _, _, _ = tuple(self.data_context.get_cmdicon(frame_index, highlighted=False))
			self.scrolled_canvas.canvas.itemconfigure(self._display_index_to_tag(old_display_index), image=icon)
		new_display_index = self._selected_index_to_display_index(new_selection)
		if new_display_index >= start_index and new_display_index <= end_index:
			frame_index = self._display_index_to_frame_index(new_display_index)
			icon, _, _, _, _ = tuple(self.data_context.get_cmdicon(frame_index, highlighted=True))
			self.scrolled_canvas.canvas.itemconfigure(self._display_index_to_tag(new_display_index), image=icon)

	def _canvas_resized(self):
		scrollregion = self._calculate_scrollregion()
		self.scrolled_canvas.canvas.config(scrollregion=(0,0,scrollregion[0],scrollregion[1]))
		self._draw_icons()
		self._update_selection_box()

	def _selected_index_to_name(self, selected_index):
		if selected_index == self.none_index:
			return 'None'
		if selected_index < 0 or selected_index >= len(self.data_context.cmdicons.names):
			return 'Unknown'
		return self.data_context.cmdicons.names[selected_index]

	def _update_status_selection(self):
		self.status_selection.set('Selected: %d (%s)' % (self.selected_index, self._selected_index_to_name(self.selected_index)))

	def _coords_to_display_index(self, x, y, add_scroll_offset=True):
		columns, total_height, _, _, _ = self._calculate_visibility()
		icon_size = self._icon_size()
		column = int(floor(x / icon_size[0]))
		if column < 0 or column >= columns:
			return None
		if add_scroll_offset:
			y += int(self.scrolled_canvas.canvas.yview()[0] * total_height)
		row = int(floor(y / icon_size[1]))
		return column + row * columns

	def _select_icon(self, event):
		display_index = self._coords_to_display_index(event.x, event.y)
		if display_index == None or display_index < 0 or display_index >= self._icon_count():
			return
		selected_index = self._display_index_to_selected_index(display_index)
		if selected_index == self.selected_index:
			return
		self._redraw_selection(self.selected_index, selected_index)
		self.selected_index = selected_index
		self._update_selection_box()
		self._update_status_selection()

	def _clear_status_hover(self):
		self.status_hover.set('')

	def _update_status_hover(self, event):
		display_index = self._coords_to_display_index(event.x, event.y)
		if display_index == None or display_index < 0 or display_index >= self._icon_count():
			self._clear_status_hover()
			return
		selection_index = self._display_index_to_selected_index(display_index)
		self.status_hover.set('Hovering: %d (%s)' % (selection_index, self._selected_index_to_name(selection_index)))

	def ok(self):
		if self.selected_index != self._initial_selection:
			self.delegate(self.selected_index)
		PyMSDialog.ok(self)

	def dismiss(self):
		self.data_context.settings.windows.save_window_size('icon_select', self)
		PyMSDialog.dismiss(self)
