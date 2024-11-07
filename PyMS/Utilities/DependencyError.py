
from .UIKit import *
from . import Assets

class DependencyError(MainWindow):
	def __init__(self, prog: str, msg: str, warning: bool = False, hotlinks: tuple[tuple[str, str], ...] | None = None) -> None:
		MainWindow.__init__(self)
		self.should_continue = False
		self.dont_remind = BooleanVar(value=False)
		self.resizable(False,False)
		self.title('Dependency Error')
		self.set_icon(prog)
		frame = Frame(self)
		frame.pack(side=TOP, padx=20,pady=20)
		Label(frame, text=msg, anchor=W, justify=LEFT).pack(side=TOP,pady=2,padx=2)
		if not hotlinks:
			hotlinks = (
				('Readme (Local)', 'file:///%s' % Assets.readme_file_path),
				('Readme (Online)', 'https://github.com/poiuyqwert/PyMS#installation')
			)
		for hotlink in hotlinks:
			f = Frame(frame)
			Hotlink(f, *hotlink).pack(side=RIGHT, padx=10, pady=2)
			f.pack(side=TOP,fill=X)
		if warning:
			Checkbutton(frame, text="Don't remind me for this version of PyMS", variable=self.dont_remind).pack(side=TOP, pady=5)
			buttons_frame = Frame(frame)
			Button(buttons_frame, text='Continue', width=10, command=self.continue_).pack(side=LEFT, padx=5)
			Button(buttons_frame, text='Exit', width=10, command=self.destroy).pack(side=LEFT, padx=5)
			buttons_frame.pack(side=TOP, pady=2)
		else:
			Button(frame, text='Ok', width=10, command=self.destroy).pack(side=TOP, pady=2)
		self.update_idletasks()
		geometry = Geometry.of(self)
		screen_size = Size(self.winfo_screenwidth(), self.winfo_screenheight())
		self.geometry(geometry.adjust_center_in(screen_size).text)

	def continue_(self, event: Event | None = None) -> None:
		self.should_continue = True
		if self.dont_remind.get():
			from .PyMSConfig import PYMS_CONFIG
			PYMS_CONFIG.reminder.python_version.value = Assets.version('PyMS')
			PYMS_CONFIG.save()
		self.destroy()
