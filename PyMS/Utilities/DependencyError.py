# pylint: disable=consider-using-f-string

from . import UIKit as UI
from . import Assets

class DependencyError(UI.MainWindow):
	def __init__(self, prog: str, msg: str, warning: bool = False, hotlinks: tuple[tuple[str, str], ...] | None = None) -> None:
		UI.MainWindow.__init__(self)
		self.should_continue = False
		self.dont_remind = UI.BooleanVar(value=False)
		self.resizable(False,False)
		self.title('Dependency Error')
		self.set_icon(prog)
		frame = UI.Frame(self)
		frame.pack(side=UI.TOP, padx=20,pady=20)
		UI.Label(frame, text=msg, anchor=UI.W, justify=UI.LEFT).pack(side=UI.TOP,pady=2,padx=2)
		if not hotlinks:
			hotlinks = (
				('Readme (Local)', 'file:///%s' % Assets.readme_file_path),
				('Readme (Online)', 'https://github.com/poiuyqwert/PyMS#installation')
			)
		for hotlink in hotlinks:
			f = UI.Frame(frame)
			UI.Hotlink(f, *hotlink).pack(side=UI.RIGHT, padx=10, pady=2)
			f.pack(side=UI.TOP,fill=UI.X)
		if warning:
			UI.Checkbutton(frame, text="Don't remind me for this version of PyMS", variable=self.dont_remind).pack(side=UI.TOP, pady=5)
			buttons_frame = UI.Frame(frame)
			UI.Button(buttons_frame, text='Continue', width=10, command=self.continue_).pack(side=UI.LEFT, padx=5)
			UI.Button(buttons_frame, text='Exit', width=10, command=self.destroy).pack(side=UI.LEFT, padx=5)
			buttons_frame.pack(side=UI.TOP, pady=2)
		else:
			UI.Button(frame, text='Ok', width=10, command=self.destroy).pack(side=UI.TOP, pady=2)
		self.update_idletasks()
		geometry = UI.Geometry.of(self)
		screen_size = UI.Size(self.winfo_screenwidth(), self.winfo_screenheight())
		self.geometry(geometry.adjust_center_in(screen_size).text)

	def continue_(self, _event: UI.Event | None = None) -> None:
		self.should_continue = True
		if self.dont_remind.get():
			from .PyMSConfig import PYMS_CONFIG
			PYMS_CONFIG.reminder.python_version.value = Assets.version('PyMS')
			PYMS_CONFIG.save()
		self.destroy()
