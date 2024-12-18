
from . import Assets
from .PyMSConfig import PYMS_CONFIG
from .PyMSDialog import PyMSDialog
from .UIKit import *
from .SemVer import SemVer

import json, urllib.request, urllib.parse, urllib.error
from _thread import start_new_thread

class UpdateDialog(PyMSDialog):
	BRANCH = 'AISE' # Default to `master` branch, but can be update for long-lived branches

	@staticmethod
	def check_update(window: WindowExtensions, program: str) -> None:
		def do_check_update(window: WindowExtensions, program: str) -> None:
			VERSIONS_URL = 'https://raw.githubusercontent.com/poiuyqwert/PyMS/%s/PyMS/versions.json' % UpdateDialog.BRANCH
			try:
				import ssl
				versions = json.loads(urllib.request.urlopen(VERSIONS_URL, context=ssl.SSLContext()).read())
				latest_PyMS_version = SemVer(versions['PyMS'])
				latest_program_version = SemVer(versions[program])
				PyMS_version = SemVer(Assets.version('PyMS'))
				program_version = SemVer(Assets.version(program))
			except:
				return
			if PyMS_version >= latest_PyMS_version and program_version >= latest_program_version:
				return
			show = 2
			if PyMS_dont_remind_me_raw := PYMS_CONFIG.reminder.pyms_version.data.get('PyMS'):
				PyMS_dont_remind_me = SemVer(PyMS_dont_remind_me_raw)
				if PyMS_dont_remind_me >= latest_PyMS_version:
					show -= 1
			if program_dont_remind_me_raw := PYMS_CONFIG.reminder.pyms_version.data.get(program):
				program_dont_remind_me = SemVer(program_dont_remind_me_raw)
				if program_dont_remind_me >= latest_program_version:
					show -= 1
			if not show:
				return
			def callback():
				if hasattr(window, '_pyms__window_blocking') and window._pyms__window_blocking:
					window.after(1000, callback)
					return
				UpdateDialog(window,program,versions)
			window.after(1, callback)
		start_new_thread(do_check_update, (window, program))

	def __init__(self, parent: Misc, program: str, versions: dict[str, str]) -> None:
		self.program = program
		self.versions = versions
		PyMSDialog.__init__(self, parent, 'New Version Found', resizable=(False, False))

	def widgetize(self) -> Misc | None:
		if SemVer(Assets.version(self.program)) < SemVer(self.versions[self.program]):
			text = "Your version of %s (%s) is older then the current version (%s).\nIt is recommended that you update as soon as possible." % (self.program,Assets.version(self.program),self.versions[self.program])	
		else:
			text = "Your version of PyMS (%s) is older then the current version (%s).\nIt is recommended that you update as soon as possible." % (Assets.version('PyMS'),self.versions['PyMS'])
		Label(self, justify=LEFT, anchor=W, text=text).pack(pady=5,padx=5)
		f = Frame(self)
		self.dont_remind_me = BooleanVar()
		Checkbutton(f, text="Don't remind me for this version", variable=self.dont_remind_me).pack(side=LEFT, padx=5)
		Hotlink(f, 'Github', 'https://github.com/poiuyqwert/PyMS').pack(side=RIGHT, padx=5)
		f.pack(fill=X, expand=1)
		ok = Button(self, text='Ok', width=10, command=self.ok)
		ok.pack(pady=5)
		return ok

	def ok(self, _: Event | None = None) -> None:
		if self.dont_remind_me.get():
			PYMS_CONFIG.reminder.pyms_version.data['PyMS'] = self.versions['PyMS']
			PYMS_CONFIG.reminder.pyms_version.data[self.program] = self.versions[self.program]
			PYMS_CONFIG.save()
		PyMSDialog.ok(self)
