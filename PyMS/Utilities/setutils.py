
from .utils import WIN_REG_AVAILABLE
from .Settings import Settings

import os

PYMS_SETTINGS = Settings('PyMS', '1')

if WIN_REG_AVAILABLE and not 'scdir' in PYMS_SETTINGS:
	try:
		from winreg import OpenKey, HKEY_LOCAL_MACHINE, KEY_READ, KEY_WOW64_32KEY, QueryValueEx # type: ignore
		h = OpenKey(HKEY_LOCAL_MACHINE, 'SOFTWARE\\Blizzard Entertainment\\Starcraft', 0, KEY_READ | KEY_WOW64_32KEY)
		path = QueryValueEx(h, 'InstallPath')[0]
		if os.path.isdir(path):
			PYMS_SETTINGS.scdir = path
	except:
		pass
