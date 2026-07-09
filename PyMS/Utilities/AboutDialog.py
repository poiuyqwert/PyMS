
from .PyMSDialog import PyMSDialog
from . import UIKit as UI

# TODO: Update about dialog
class AboutDialog(PyMSDialog):
	def __init__(self, parent: UI.Misc, program: str, version: str, thanks: list[tuple[str, str]] | None = None) -> None:
		self.program = program
		self.version = version
		self.thanks = thanks or []
		self.thanks.extend([
			('ShadowFlare','For SFmpq, some file specs, and all her tools!'),
			('Ladislav Zezula','For StormLib'),
			('BroodWarAI.com','Support and hosting of course!'),
			('Blizzard','For creating StarCraft and BroodWar...'),
		])
		PyMSDialog.__init__(self, parent, f'About {program}', resizable=(False, False))

	def widgetize(self) -> UI.Misc | None:
		name = UI.Label(self, text=f'{self.program} {self.version}', font=UI.Font(size=18))
		name.pack(pady=5)
		frame = UI.Frame(self)
		UI.Label(frame, text='Author:').grid(sticky=UI.E)
		UI.Label(frame, text='Homepage:').grid(sticky=UI.E)
		UI.Hotlink(frame, 'poiuy_qwert (p.q.poiuy_qwert@gmail.com)', 'mailto:p.q.poiuy.qwert@hotmail.com').grid(row=0, column=1, sticky=UI.W)
		UI.Hotlink(frame, 'https://github.com/poiuyqwert/PyMS', 'https://github.com/poiuyqwert/PyMS').grid(row=1, column=1, sticky=UI.W)
		frame.pack(padx=5, pady=2)
		if self.thanks:
			UI.Label(self, text='Special Thanks To:', font=UI.Font.default().bolded()).pack(pady=2)
			thanks = UI.Frame(self)
			row = 0
			for who,why in self.thanks:
				if who == 'BroodWarAI.com':
					UI.Hotlink(thanks, who, 'http://www.broodwarai.com', font=UI.Font.default().bolded(), hover_font=UI.Font.default().bolded().underline()).grid(sticky=UI.E)
				else:
					UI.Label(thanks, text=who).grid(sticky=UI.E)
				UI.Label(thanks, text=why).grid(row=row, column=1, sticky=UI.W)
				row += 1
			thanks.pack(padx=5, pady=1)
		ok = UI.Button(self, text='Ok', width=10, command=self.ok)
		ok.pack(pady=5)
		return ok
