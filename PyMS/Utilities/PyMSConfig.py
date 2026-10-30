
from __future__ import annotations

from . import registry
from . import Config

import os

def _migrate_1_to_2(data: dict) -> None:
	Config.migrate_fields(data, (
		(('dont_remind_me',), ('reminder', 'pyms_version', 'PyMS')),
	))

class PyMSConfig(Config.Config):
	_name = 'PyMS'
	_version = 2
	_migrations = {
		1: _migrate_1_to_2
	}

	class Analytics(Config.Group):
		def __init__(self) -> None:
			self.allow = Config.Boolean(default=True)
			self.tid = Config.String(default='UA-42320973-2')
			self.cid = Config.String()
			super().__init__()

	class Reminder(Config.Group):
		def __init__(self) -> None:
			self.pyms_version = Config.Dictionary(value_type=str)
			self.python_version = Config.String(default=None)
			super().__init__()

	def __init__(self) -> None:
		self.analytics = PyMSConfig.Analytics()
		self.scdir = Config.SelectDirectory(title='Choose StarCraft Directory')
		self.reminder = PyMSConfig.Reminder()
		self.theme = Config.String()
		super().__init__()

PYMS_CONFIG = PyMSConfig()

if registry.IS_AVAILABLE and not PYMS_CONFIG.scdir.is_set:
	try:
		from winreg import OpenKey, HKEY_LOCAL_MACHINE, KEY_READ, KEY_WOW64_32KEY, QueryValueEx # type: ignore # pylint: disable=import-error
		with OpenKey(HKEY_LOCAL_MACHINE, 'SOFTWARE\\Blizzard Entertainment\\Starcraft', 0, KEY_READ | KEY_WOW64_32KEY) as h:
			path = QueryValueEx(h, 'InstallPath')[0]
		if isinstance(path, str) and os.path.isdir(path):
			PYMS_CONFIG.scdir.path = path
			PYMS_CONFIG.scdir.is_set = True
	except Exception:
		pass
