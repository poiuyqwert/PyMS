
from utils import BASE_DIR
from ..Utilities.DropDownChooser import DropDownChooser
from UIKit import *

import os

class TextDropDown(Frame):
	ARROW = None

	def __init__(self, parent, variable, history=[], width=None, state=NORMAL):
		self.variable = variable
		self.set = self.variable.set
		self.history = history
		Frame.__init__(self, parent, borderwidth=2, relief=SUNKEN)
		self.entry = Entry(self, textvariable=self.variable, width=width, bd=0)
		self.entry.pack(side=LEFT, fill=X, expand=1)
		self.entry['state'] = state
		if TextDropDown.ARROW == None:
			TextDropDown.ARROW = PhotoImage(file=os.path.join(BASE_DIR, 'PyMS','Images','arrow.gif'))
		self.button = Button(self, image=TextDropDown.ARROW, command=self.choose, state=state)
		self.button.pack(side=LEFT, fill=Y)

	def focus_set(self, highlight=False):
		self.entry.focus_set()
		if highlight:
			self.entry.selection_range(0,END)

	def __setitem__(self, item, value):
		if item == 'state':
			self.entry['state'] = value
			self.button['state'] = value
		else:
			self.entry[item] = value

	def __getitem__(self, item):
		return self.entry[item]

	def choose(self, e=None):
		if self.entry['state'] == NORMAL and self.history:
			i = -1
			if self.variable.get() in self.history:
				i = self.history.index(self.variable.get())
			c = DropDownChooser(self, self.history, i)
			if c.result > -1:
				self.variable.set(self.history[c.result])
