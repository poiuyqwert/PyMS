
from __future__ import annotations

from .utils import WIN_REG_AVAILABLE
from . import Config

import os

class PyMSConfig(Config.Config):
	_name = 'PyMS'
	_version = 1

	class Analytics(Config.Group):
		def __init__(self):
			self.allow = Config.Boolean(default=True)
			self.tid = Config.String(default='UA-42320973-2')
			self.cid = Config.String()
			super().__init__()

	def __init__(self):
		self.analytics = PyMSConfig.Analytics()
		self.scdir = Config.SelectDirectory(title='Choose StarCraft Directory')
		self.dont_remind_me = Config.Dictionary(value_type=str)
		self.theme = Config.String()
		super().__init__()

PYMS_CONFIG = PyMSConfig()

if WIN_REG_AVAILABLE and PYMS_CONFIG.scdir.path is None:
	try:
		from winreg import OpenKey, HKEY_LOCAL_MACHINE, KEY_READ, KEY_WOW64_32KEY, QueryValueEx # type: ignore
		h = OpenKey(HKEY_LOCAL_MACHINE, 'SOFTWARE\\Blizzard Entertainment\\Starcraft', 0, KEY_READ | KEY_WOW64_32KEY)
		path = QueryValueEx(h, 'InstallPath')[0]
		if isinstance(path, str) and os.path.isdir(path):
			PYMS_CONFIG.scdir.path = path
	except:
		pass
