
from .PyMSDialog import PyMSDialog
from .Hotlink import Hotlink
from .UIKit import *

import webbrowser

# TODO: Update about dialog
class AboutDialog(PyMSDialog):
	def __init__(self, parent, program, version, thanks=[]):
		self.program = program
		self.version = version
		self.thanks = thanks
		self.thanks.extend([
			('ShadowFlare','For SFmpq, some file specs, and all her tools!'),
			('BroodWarAI.com','Support and hosting of course!'),
			('Blizzard','For creating StarCraft and BroodWar...'),
		])
		PyMSDialog.__init__(self, parent, 'About %s' % program, resizable=(False, False))

	def widgetize(self):
		name = Label(self, text='%s %s' % (self.program, self.version), font=Font(size=18))
		name.pack(pady=5)
		frame = Frame(self)
		Label(frame, text='Author:').grid(sticky=E)
		Label(frame, text='Homepage:').grid(sticky=E)
		Hotlink(frame, 'poiuy_qwert (p.q.poiuy_qwert@gmail.com)', self.author).grid(row=0, column=1, sticky=W)
		Hotlink(frame, 'https://github.com/poiuyqwert/PyMS', self.homepage).grid(row=1, column=1, sticky=W)
		frame.pack(padx=5, pady=2)
		if self.thanks:
			Label(self, text='Special Thanks To:', font=Font(bold=True)).pack(pady=2)
			thanks = Frame(self)
			row = 0
			for who,why in self.thanks:
				if who == 'BroodWarAI.com':
					Hotlink(thanks, who, self.broodwarai, font=Font(bold=True), hover_font=Font(bold=True, underline=True)).grid(sticky=E)
				else:
					Label(thanks, text=who).grid(sticky=E)
				Label(thanks, text=why).grid(row=row, column=1, sticky=W)
				row += 1
			thanks.pack(padx=5, pady=1)
		ok = Button(self, text='Ok', width=10, command=self.ok)
		ok.pack(pady=5)
		return ok

	def author(self, e=None):
		webbrowser.open('mailto:p.q.poiuy.qwert@hotmail.com')

	def homepage(self, e=None):
		webbrowser.open('https://github.com/poiuyqwert/PyMS')

	def broodwarai(self, e=None):
		webbrowser.open('http://www.broodwarai.com')
