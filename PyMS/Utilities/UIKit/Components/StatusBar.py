
from ..Widgets import *

class StatusBar(Frame):
	def __init__(self, parent: Misc, *args, **kwargs):
		self._weights: list[float | None] = []
		Frame.__init__(self, parent, *args, **kwargs)

	def _adjust_weights(self) -> None:
		none_count = self._weights.count(None)
		split_remainder = 0
		if none_count:
			remainder = 1 - sum(weight for weight in self._weights if weight)
			split_remainder = int(100 * remainder / float(none_count))
		for column,weight in enumerate(self._weights):
			self.grid_columnconfigure(column, weight=split_remainder if weight is None else int(100 * weight))

	def add_label(self, text_variable: StringVar, width: int | None = None, weight: float | None = None) -> Label:
		label = Label(self, textvariable=text_variable, width=width, bd=1, relief=SUNKEN, anchor=W) # type: ignore[arg-type]
		label.grid(row=0, column=len(self._weights), padx=1, sticky=NSEW)
		self._weights.append(weight)
		self._adjust_weights()
		return label

	def add_icon(self, image: Image, weight: float = 0) -> Label:
		label = Label(self, image=image, bd=0, state=DISABLED)
		setattr(label, '_image', image)
		label.grid(row=0, column=len(self._weights), padx=1, sticky=NS)
		self._weights.append(weight)
		self._adjust_weights()
		return label

	def add_spacer(self, weight: float | None = None) -> Frame:
		frame = Frame(self, bd=1, relief=SUNKEN)
		frame.grid(row=0, column=len(self._weights), padx=1, sticky=NSEW)
		self._weights.append(weight)
		self._adjust_weights()
		return frame
