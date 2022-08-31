
from .UIKit import *
from . import Assets

class CollapseView(Frame):
	class Button(Button):
		ARROW_DOWN = None
		ARROW_UP = None

		def __init__(self, parent): # type (Widget) -> CollapseView.Button
			self.collapse_view = None # type: CollapseView
			if CollapseView.Button.ARROW_DOWN == None:
				CollapseView.Button.ARROW_DOWN = Assets.get_image('arrow')
			if CollapseView.Button.ARROW_UP == None:
				CollapseView.Button.ARROW_UP = Assets.get_image('arrowup')
			Button.__init__(self, parent, image=CollapseView.Button.ARROW_DOWN, command=self.toggle)

		def _update_state(self, collapsed):
			self['image'] = CollapseView.Button.ARROW_UP if collapsed else CollapseView.Button.ARROW_DOWN

		def toggle(self):
			if not self.collapse_view:
				return
			self.collapse_view.toggle()

		def collapse(self):
			if not self.collapse_view:
				return
			self.collapse_view.collapse()

		def expand(self):
			if not self.collapse_view:
				return
			self.collapse_view.expand()

		def set_collapsed(self, collapsed): # type (bool) -> None
			if not self.collapse_view:
				return
			self.collapse_view.set_collapsed(collapsed)

	def __init__(self, parent, collapse_button, *args, **kwargs): # type: (Widget, CollapseView.Button, *Any, **Any) -> CollapseView
		self.collapsed = False
		self.collapse_button = collapse_button
		self._hide = None
		self._show = None
		self._show_info = None
		self._show_order = None
		self.callback = None
		if 'callback' in kwargs:
			self.callback = kwargs['callback']
			del kwargs['callback']
		Frame.__init__(self, parent, *args, **kwargs)

		collapse_button.collapse_view = self
		self._update_state(apply_callback=False)

	def place(self, **kwargs):
		def _hide():
			self._show_info = self.place_info()
			self.place_forget()
		self._hide = _hide
		def _show():
			show_info = self._show_info or {}
			Frame.place(self, **show_info)
			self._show_info = None
		self._show = _show
		Frame.place(self, **kwargs)

	def pack(self, **kwargs):
		def _hide():
			self._show_info = self.pack_info()
			self._show_order = tuple(widget.winfo_id() for widget in self.master.pack_slaves())
			self.pack_forget()
		self._hide = _hide
		def _show():
			show_info = self._show_info or {}
			if self._show_order and self.winfo_id() in self._show_order:
				slaves = self.master.pack_slaves()
				current_order = tuple(widget.winfo_id() for widget in slaves)
				start_index = self._show_order.index(self.winfo_id())
				check_index = start_index - 1
				while check_index >= 0:
					if self._show_order[check_index] in current_order:
						show_info['after'] = slaves[current_order.index(self._show_order[check_index])]
						break
					check_index -= 1
				check_index = start_index + 1
				while check_index < len(self._show_order):
					if self._show_order[check_index] in current_order:
						show_info['before'] = slaves[current_order.index(self._show_order[check_index])]
						break
					check_index += 1
			Frame.pack(self, **show_info)
			self._show_info = None
			self._show_order = None
		self._show = _show
		Frame.pack(self, **kwargs)

	def grid(self, **kwargs):
		self._hide = self.grid_remove
		self._show = self.grid
		Frame.grid(self, **kwargs)

	def _update_state(self, apply_callback=True):
		self.collapse_button._update_state(self.collapsed)
		if self.collapsed and self._hide:
			self._hide()
		elif not self.collapsed and self._show:
			self._show()
		if apply_callback and self.callback:
			self.callback(self.collapsed)

	def toggle(self):
		self.collapsed = not self.collapsed
		self._update_state()

	def collapse(self):
		if self.collapsed:
			return
		self.collapsed = True
		self._update_state()

	def expand(self):
		if not self.collapsed:
			return
		self.collapsed = False
		self._update_state()

	def set_collapsed(self, collapsed): # type (bool) -> None
		if collapsed == self.collapsed:
			return
		self.collapsed = collapsed
		self._update_state()
