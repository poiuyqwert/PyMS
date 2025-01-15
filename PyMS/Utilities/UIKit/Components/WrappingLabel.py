
from ..Widgets import Label, Event
from ..EventPattern import *

class WrappingLabel(Label):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.bind(WidgetEvent.Configure(), self.update_wrapping)

	def update_wrapping(self, event: Event) -> None:
		self.config(wraplength=self.winfo_width())
