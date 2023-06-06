
from . import Assets
from .setutils import PYMS_SETTINGS
from .PyMSDialog import PyMSDialog
from .UIKit import *

import json, urllib.request, urllib.parse, urllib.error
from _thread import start_new_thread

class UpdateDialog(PyMSDialog):
	BRANCH = 'master' # Default to `master` branch, but can be update for long-lived branches

	@staticmethod
	def check_update(window, program): # type: (AnyWindow, str) -> None
		def do_check_update(window, program): # type: (AnyWindow, str) -> None
			VERSIONS_URL = 'https://raw.githubusercontent.com/poiuyqwert/PyMS/%s/PyMS/versions.json' % UpdateDialog.BRANCH
			remindme = PYMS_SETTINGS.get('remindme', True)
			if remindme == True or remindme != Assets.version('PyMS'):
				try:
					import ssl
					versions = json.loads(urllib.request.urlopen(VERSIONS_URL, context=ssl.SSLContext()).read())
					latest_PyMS_version = SemVer(versions['PyMS'])
					latest_program_version = SemVer(versions[program])
					PyMS_version = SemVer(Assets.version('PyMS'))
					program_version = SemVer(Assets.version(program))
				except:
					return
				if PyMS_version < latest_PyMS_version or program_version < latest_program_version:
					def callback():
						if hasattr(window, '_pyms__window_blocking') and window._pyms__window_blocking:
							window.after(1000, callback)
							return
						UpdateDialog(window,program,versions)
					window.after(1, callback)
		start_new_thread(do_check_update, (window, program))

	def __init__(self, parent, program, versions): # type: (Misc, str, dict[str, str]) -> None
		self.program = program
		self.versions = versions
		PyMSDialog.__init__(self, parent, 'New Version Found', resizable=(False, False))

	def widgetize(self): # type: () -> (Misc | None)
		if SemVer(Assets.version(self.program)) < SemVer(self.versions[self.program]):
			text = "Your version of %s (%s) is older then the current version (%s).\nIt is recommended that you update as soon as possible." % (self.program,Assets.version(self.program),self.versions[self.program])	
		else:
			text = "Your version of PyMS (%s) is older then the current version (%s).\nIt is recommended that you update as soon as possible." % (Assets.version('PyMS'),self.versions['PyMS'])
		Label(self, justify=LEFT, anchor=W, text=text).pack(pady=5,padx=5)
		f = Frame(self)
		self.remind = IntVar()
		remindme = PYMS_SETTINGS.get('remindme', True)
		self.remind.set(remindme == True or remindme != Assets.version('PyMS'))
		Checkbutton(f, text='Remind me later', variable=self.remind).pack(side=LEFT, padx=5)
		Hotlink(f, 'Github', 'https://github.com/poiuyqwert/PyMS').pack(side=RIGHT, padx=5)
		f.pack(fill=X, expand=1)
		ok = Button(self, text='Ok', width=10, command=self.ok)
		ok.pack(pady=5)
		return ok

	def ok(self, _=None): # type: (Event | None) -> None
		PYMS_SETTINGS.remindme = [Assets.version('PyMS'),1][self.remind.get()]
		PYMS_SETTINGS.save()
		PyMSDialog.ok(self)

class SemVer(object):
	def __init__(self, version): # type: (str) -> None
		self.meta = None
		if '-' in version:
			version,self.meta = version.split('-')
		components = (int(c) for c in version.split('.'))
		self.major, self.minor, self.patch = components

	def __lt__(self, other): # type: (Any) -> bool
		if not isinstance(other, SemVer):
			return False
		if self.major < other.major:
			return True
		elif self.major > other.major:
			return False
		if self.minor < other.minor:
			return True
		elif self.minor > other.minor:
			return False
		if self.patch < other.patch:
			return True
		elif self.patch > other.patch:
			return False
		return False
