
from .UIKit import *

class StatusBar(Frame):
	def __init__(self, *args, **kwargs):
		self._weights = []
		Frame.__init__(self, *args, **kwargs)

	def _adjust_weights(self):
		none_count = self._weights.count(None)
		split_remainder = 0
		if none_count:
			remainder = 1 - sum(weight for weight in self._weights if weight)
			split_remainder = int(100 * remainder / float(none_count))
		for column,weight in enumerate(self._weights):
			self.grid_columnconfigure(column, weight=split_remainder if weight == None else int(100 * weight))

	def add_label(self, text_variable, width=None, weight=None):
		label = Label(self, textvariable=text_variable, width=width, bd=1, relief=SUNKEN, anchor=W)
		label.grid(row=0, column=len(self._weights), padx=1, sticky=NSEW)
		self._weights.append(weight)
		self._adjust_weights()
		return label

	def add_icon(self, image, weight=0):
		label = Label(self, image=image, bd=0, state=DISABLED)
		label.image = image
		label.grid(row=0, column=len(self._weights), padx=1, sticky=NS)
		self._weights.append(weight)
		self._adjust_weights()
		return label

	def add_spacer(self, weight=None):
		frame = Frame(self, bd=1, relief=SUNKEN)
		frame.grid(row=0, column=len(self._weights), padx=1, sticky=NSEW)
		self._weights.append(weight)
		self._adjust_weights()
		return frame
