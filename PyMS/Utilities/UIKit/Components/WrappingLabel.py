
from ..Widgets import Label
from .. import Event
from ..EventPattern import WidgetEvent

from typing import Any

class WrappingLabel(Label):
	def __init__(self, *args: Any, **kwargs: Any) -> None:
		super().__init__(*args, **kwargs)
		self.bind(WidgetEvent.Configure(), self.update_wrapping)

	def update_wrapping(self, _event: Event) -> None:
		self.config(wraplength=self.winfo_width())
