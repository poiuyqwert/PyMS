
from utils import BASE_DIR, WIN_REG_AVAILABLE, parse_geometry
from Settings import Settings

from Tkinter import *

import os, json

PYMS_SETTINGS = Settings('PyMS', '1')

if WIN_REG_AVAILABLE and not 'scdir' in PYMS_SETTINGS:
	try:
		from _winreg import OpenKey, HKEY_LOCAL_MACHINE, KEY_READ, KEY_WOW64_32KEY, QueryValueEx
		h = OpenKey(HKEY_LOCAL_MACHINE, 'SOFTWARE\\Blizzard Entertainment\\Starcraft', 0, KEY_READ | KEY_WOW64_32KEY)
		path = QueryValueEx(h, 'InstallPath')[0]
		if os.path.isdir(path):
			PYMS_SETTINGS.scdir = path
	except:
		pass

# TODO: Remove all below once switched to using Settings
def loadsettings(program, default={}):
	settings = default
	path = os.path.join(BASE_DIR,'Settings','%s.txt' % program)
	if os.path.exists(path):
		try:
			contents = None
			with file(path, 'r') as f:
				contents = f.read()
			settings.update(json.loads(contents))
		except:
			pass
	return settings

def savesettings(program, settings):
	try:
		f = file(os.path.join(BASE_DIR,'Settings','%s.txt' % program),'w')
		f.write(json.dumps(settings, sort_keys=True, indent=4))
		f.close()
	except:
		pass

def loadsize(window, settings, setting='window', full=False, size=True, position=None):
	geometry = settings.get(setting)
	if geometry:
		w,h,x,y,fullscreen = parse_geometry(geometry)
		if position:
			x,y = position
		if size and w != None and h != None:
			screen_w = window.winfo_screenwidth()
			screen_h = window.winfo_screenheight()
			resizable = window.resizable()
			min_size = window.minsize()
			if x+w > screen_w:
				x = screen_w-w
			if x < 0:
				x = 0
			if w > screen_w and resizable[0] and screen_w > min_size[0]:
				w = screen_w
			if y+h > screen_h:
				y = max(0,screen_h-h)
			if y < 0:
				y = 0
			if h > screen_h and resizable[1] and screen_h > min_size[1]:
				h = screen_h
			window.geometry('%dx%d+%d+%d' % (w,h, x,y))
		else:
			window.geometry('+%d+%d' % (x,y))
		window.update_idletasks()
		if fullscreen:
			try:
				window.wm_state('zoomed')
			except:
				pass

def savesize(window, settings, setting='window', size=True, closing=True):
	w,h,x,y,_ = parse_geometry(window.winfo_geometry())
	if size:
		z = ''
		if window.wm_state() == 'zoomed':
			z = '^'
			window.wm_state('normal')
			window.update_idletasks()
			w,h,x,y,_ = parse_geometry(window.winfo_geometry())
			if not closing:
				window.wm_state('zoomed')
		settings[setting] = '%dx%d+%d+%d%s' % (w,h,x,y,z)
	else:
		settings[setting] = '+%d+%d' % (x,y)
