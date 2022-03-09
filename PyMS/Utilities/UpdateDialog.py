
from utils import VERSIONS
from setutils import PYMS_SETTINGS
from PyMSDialog import PyMSDialog
from Hotlink import Hotlink
from UIKit import *

import webbrowser, json, urllib
from thread import start_new_thread

class UpdateDialog(PyMSDialog):
	BRANCH = 'expanded_dat_files' # Default to `master` branch, but can be update for long-lived branches

	@staticmethod
	def check_update(window, program):
		def do_check_update(window, program):
			VERSIONS_URL = 'https://raw.githubusercontent.com/poiuyqwert/PyMS/%s/PyMS/versions.json' % UpdateDialog.BRANCH
			remindme = PYMS_SETTINGS.get('remindme', True)
			if remindme == True or remindme != VERSIONS['PyMS']:
				try:
					versions = json.loads(urllib.urlopen(VERSIONS_URL).read())
					PyMS_version = SemVer(versions['PyMS'])
					program_version = SemVer(versions[program])
				except:
					return
				if VERSIONS['PyMS'] < PyMS_version or VERSIONS[program] < program_version:
					def callback():
						if hasattr(window, '_pyms__window_blocking') and window._pyms__window_blocking:
							window.after(1000, callback)
							return
						UpdateDialog(window,program,versions)
					window.after(1, callback)
		start_new_thread(do_check_update, (window, program))

	def __init__(self, parent, program, versions):
		self.program = program
		self.versions = versions
		PyMSDialog.__init__(self, parent, 'New Version Found', resizable=(False, False))

	def widgetize(self):
		if SemVer(VERSIONS[self.program]) < SemVer(self.versions[self.program]):
			text = "Your version of %s (%s) is older then the current version (%s).\nIt is recommended that you update as soon as possible." % (self.program,VERSIONS[self.program],self.versions[self.program])	
		else:
			text = "Your version of PyMS (%s) is older then the current version (%s).\nIt is recommended that you update as soon as possible." % (VERSIONS['PyMS'],self.versions['PyMS'])
		Label(self, justify=LEFT, anchor=W, text=text).pack(pady=5,padx=5)
		f = Frame(self)
		self.remind = IntVar()
		remindme = PYMS_SETTINGS.get('remindme', True)
		self.remind.set(remindme == True or remindme != VERSIONS['PyMS'])
		Checkbutton(f, text='Remind me later', variable=self.remind).pack(side=LEFT, padx=5)
		Hotlink(f, 'Github', self.github).pack(side=RIGHT, padx=5)
		f.pack(fill=X, expand=1)
		ok = Button(self, text='Ok', width=10, command=self.ok)
		ok.pack(pady=5)
		return ok

	def github(self, e=None):
		webbrowser.open('https://github.com/poiuyqwert/PyMS')

	def ok(self):
		PYMS_SETTINGS.remindme = [VERSIONS['PyMS'],1][self.remind.get()]
		PYMS_SETTINGS.save()
		PyMSDialog.ok(self)

class SemVer(object):
	def __init__(self, version):
		self.meta = None
		if '-' in version:
			version,self.meta = version.split('-')
		components = (int(c) for c in version.split('.'))
		self.major, self.minor, self.patch = components

	def __lt__(self, other):
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
