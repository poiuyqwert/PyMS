
from PyMS.Utilities.UIKit import Misc
from . import UIKit as UI
from .PyMSDialog import PyMSDialog

class SponsorDialog(PyMSDialog):
	def __init__(self, parent: Misc) -> None:
		super().__init__(parent, "Donate", center=True, grabwait=True, escape=True, resizable=(False, False))

	def widgetize(self) -> Misc | None:
		UI.Label(self, wraplength=500, justify=UI.LEFT, text="""Hey, this is poiuy_qwert, the creator and maintainer of PyMS (and BWAILauncher). I am a StarCraft Broodwar Modding and Mapping enthusiast. At this point I don't do much modding or mapping myself, but I do build and maintain tools to help other people realize their own mods/maps.

I have been building/maintaining PyMS since 2007, and continue to add tools/features, fix bugs and improve the tools, as well as support users in using the tools. I hope to continue working on these tools, and continuing to make them the best tools available.

I do all this work for free and open source, but if you would like to say thank you, you can make a one-time "buy me a coffee" style donation, or a monthly sponsorship, through my Github Sponsor page. Any amount is greatly appreciated, and goes a long way to appeasing the wife for me spending time working on "useless" stuff for free.

Thank you!""").pack(side=UI.TOP, fill=UI.X, padx=10, pady=10)

		frame = UI.Frame(self)
		UI.Label(frame, text='Donate Here: ').pack(side=UI.LEFT)
		UI.Hotlink(frame, 'https://github.com/sponsors/poiuyqwert', 'https://github.com/sponsors/poiuyqwert?frequency=one-time&sponsor=poiuyqwert').pack(side=UI.LEFT)
		frame.pack()

		ok = UI.Button(self, text='Ok', width=10, command=self.ok)
		ok.pack(pady=10)
		return ok
