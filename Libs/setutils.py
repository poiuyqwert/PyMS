from utils import *
from fileutils import *
from SFmpq import *
from Libs import PCX,FNT,GRP,PAL,TBL,AIBIN,DAT,IScriptBIN

from Tkinter import *
from tkMessageBox import *

import re, os, json, copy

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

class SettingDict(object):
	def __init__(self, settings=None):
		if not isinstance(settings, dict):
			settings = {}
		self.__dict__['_settings'] = settings
	def __getattr__(self, key):
		return self[key]
	def __setattr__(self, key, value):
		self[key] = value
	def __delattr__(self, key):
		del self[key]
	def __len__(self):
		return len(self.__dict__['_settings'])
	def __getitem__(self, key):
		if not key in self.__dict__['_settings']:
			self.__dict__['_settings'][key] = SettingDict()
		return self.__dict__['_settings'][key]
	def __setitem__(self, key, value):
		if isinstance(value, dict):
			value = SettingDict(value)
		self.__dict__['_settings'][key] = value
	def __delitem__(self, key):
		if key in self.__dict__['_settings']:
			del self.__dict__['_settings'][key]
	def __iter__(self):
		return self.__dict__['_settings'].__iter__()
	def __contains__(self, key):
		return key in self.__dict__['_settings']
	def __copy__(self):
		return SettingDict(dict(self.__dict__['_settings']))
	def copy(self):
		return copy.copy(self)
	def __deepcopy__(self, memo):
		if id(self) in memo:
			return memo[id(self)]
		result = SettingDict()
		memo[id(self)] = result
		for key,value in self.iteritems():
			result[key] = copy.deepcopy(value, memo)
		return result
	def deepcopy(self):
		return copy.deepcopy(self)
	def iteritems(self):
		return self.__dict__['_settings'].iteritems()
	def keys(self):
		return self.__dict__['_settings'].keys()
	def values(self):
		return self.__dict__['_settings'].values()
	def update(self, settings, set=False):
		if set:
			self.__dict__['_settings'] = copy.deepcopy(settings.__dict__['_settings'])
		else:
			for key,value in settings.iteritems():
				if isinstance(value, SettingDict):
					if key in self:
						self[key].update(value, set=set)
					else:
						self[key] = copy.deepcopy(value)
				else:
					self[key] = value
	def set_defaults(self, settings):
		for key,value in settings.iteritems():
			if not key in self:
				self[key] = value
	def get(self, key, default=None, autosave=True):
		if not key in self.__dict__['_settings']:
			if callable(default):
				default = default()
			if not autosave:
				return default
			self.__dict__['_settings'][key] = default
		return self.__dict__['_settings'][key]
	def get_list(self, key, default=None, autosave=True):
		def get_default():
			if callable(default):
				default = default()
			if not isinstance(default, list):
				default = []
			return default
		self.get(key, get_default)
	def set_defaults(self, defaults):
		for key,value in defaults.iteritems():
			if not key in self:
				self[key] = value
	def save_pane_size(self, key, panedwindow, index=0):
		axis = 0 if panedwindow.cget('orient') == HORIZONTAL else 1
		self[key] = panedwindow.sash_coord(index)[axis]
	def save_pane_sizes(self, key, panedwindow):
		axis = 0 if panedwindow.cget('orient') == HORIZONTAL else 1
		sizes = []
		o = 0
		for n in range(len(panedwindow.panes())-1):
			c = panedwindow.sash_coord(n)[axis]
			sizes.append(c - o)
			o = c
		self[key] = sizes
	def load_pane_size(self, key, panedwindow, default, index=0):
		axis = 0 if panedwindow.cget('orient') == HORIZONTAL else 1
		size = [0,0]
		size[axis] = self.get(key, default)
		panedwindow.sash_place(index, *size)
	def load_pane_sizes(self, key, panedwindow, defaults):
		axis = 0 if panedwindow.cget('orient') == HORIZONTAL else 1
		o = 0
		for n,s in enumerate(self.get(key, defaults)[:len(panedwindow.panes())-1]):
			size = [0,0]
			o += s
			size[axis] = o
			panedwindow.sash_place(n, *size)
	def save_window_size(self, key, window, closing=True):
		resizable_w,resizable_h = (bool(v) for v in window.resizable().split(' '))
		w,h,x,y,f = parse_geometry(window.winfo_geometry())
		if resizable_w or resizable_h:
			z = ''
			if window.wm_state() == 'zoomed':
				z = '^'
				window.wm_state('normal')
				window.update_idletasks()
				w,h,x,y,_ = parse_geometry(window.winfo_geometry())
				if not closing:
					window.wm_state('zoomed')
			self[key] = '%sx%s+%d+%d%s' % (w,h,x,y,z)
		else:
			self[key] = '+%d+%d' % (x,y)
	def load_window_size(self, key, window, position=None, default_center=True, default_size=None):
		geometry = self.get(key)
		if geometry:
			w,h,x,y,fullscreen = parse_geometry(geometry)
			if position:
				x,y = position
			resizable_w,resizable_h = (bool(v) for v in window.resizable().split(' '))
			can_fullscreen = (resizable_w and resizable_h)
			if (resizable_w or resizable_h) and w != None and h != None:
				cur_w,cur_h,_,_,_ = parse_geometry(window.winfo_geometry())
				min_w,min_h = window.minsize()
				max_w,max_h = window.maxsize()
				screen_w = window.winfo_screenwidth()
				screen_h = window.winfo_screenheight()
				if resizable_w:
					if x+w > screen_w:
						x = screen_w-w
					if x < 0:
						x = 0
					w = max(min_w,min(screen_w,w))
				else:
					w = cur_w
				if resizable_h:
					if y+h > screen_h:
						y = screen_h-h
					if y < 0:
						y = 0
					h = max(min_h,min(screen_h,h))
				else:
					h = cur_h
				window.geometry('%dx%d+%d+%d' % (w,h, x,y))
			else:
				window.geometry('+%d+%d' % (x,y))
			window.update_idletasks()
			try:
				if fullscreen and can_fullscreen:
					window.wm_state('zoomed')
				else:
					window.wm_state('normal')
			except:
				pass
		else:
			w,h,x,y,fullscreen = parse_geometry(window.winfo_geometry())
			geometry = ''
			if default_size:
				w,h = default_size
				geometry = '%dx%d' % default_size
			if position:
				geometry += '+%d+%d' % position
			elif default_center or geometry:
				window.update_idletasks()
				screen_w = window.winfo_screenwidth()
				screen_h = window.winfo_screenheight()
				geometry += '+%d+%d' % ((screen_w-w)/2,(screen_h-h)/2)
			if geometry:
				window.geometry(geometry)
	def select_file(self, key, parent, title, ext, filetypes, save=False, store=True):
		dialog = tkFileDialog.asksaveasfilename if save else tkFileDialog.askopenfilename
		parent._pyms__window_blocking = True
		path = dialog(parent=parent, title=title, defaultextension=ext, filetypes=filetypes, initialdir=self.get(key, BASE_DIR, autosave=store))
		parent._pyms__window_blocking = False
		if path and store:
			self[key] = os.path.dirname(path)
		return path
	def select_files(self, key, parent, title, ext, filetypes, store=True):
		if len(filetypes) == 1 and filetypes[0][1] == '*':
			filetypes = None
		parent._pyms__window_blocking = True
		if filetypes == None:
			paths = tkFileDialog.askopenfilename(parent=parent, title=title, defaultextension=ext, initialdir=self.get(key, BASE_DIR, autosave=store), multiple=True)
		else:
			paths = tkFileDialog.askopenfilename(parent=parent, title=title, defaultextension=ext, filetypes=filetypes, initialdir=self.get(key, BASE_DIR, autosave=store), multiple=True)
		parent._pyms__window_blocking = False
		if isstr(paths):
			if paths:
				paths = [paths]
			else:
				paths = []
		if paths and store:
			self[key] = os.path.dirname(paths[0])
		return paths
	def select_directory(self, key, parent, title, store=True):
		parent._pyms__window_blocking = True
		path = tkFileDialog.askdirectory(parent=parent, title=title, initialdir=self.get(key, BASE_DIR, autosave=store))
		parent._pyms__window_blocking = False
		if path and store:
			self[key] = path
		return path
class SettingEncoder(json.JSONEncoder):
	def default(self, obj):
		if isinstance(obj, SettingDict):
			return obj.__dict__['_settings']
		return json.JSONEncoder.default(self, obj)
class Settings(SettingDict):
	def __init__(self, program, settings_version):
		self.__dict__['path'] = os.path.join(BASE_DIR,'Settings','%s.txt' % program)
		self.__dict__['version'] = settings_version
		try:
			with file(self.__dict__['path'], 'r') as f:
				settings = json.load(f, object_hook=lambda o: SettingDict(o)).__dict__['_settings']
			if settings:
				version = settings.get('version', '?')
				if version != settings_version:
					settings = {}
		except:
			settings = {}
		SettingDict.__init__(self, settings)

	def save(self):
		try:
			self.version = self.__dict__['version']
			with file(self.__dict__['path'], 'w') as f:
				json.dump(self, f, sort_keys=True, indent=4, cls=SettingEncoder)
		except:
			pass

PYMS_SETTINGS = Settings('PyMS', '1')

if win_reg and not 'scdir' in PYMS_SETTINGS:
	try:
		h = OpenKey(HKEY_LOCAL_MACHINE, 'SOFTWARE\\Blizzard Entertainment\\Starcraft')
		path = QueryValueEx(h, 'InstallPath')[0]
		if os.path.isdir(path):
			PYMS_SETTINGS.scdir = path
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
	w,h,x,y,f = parse_geometry(window.winfo_geometry())
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

def check_update(window, program):
	VERSIONS_URL = 'https://raw.githubusercontent.com/poiuyqwert/PyMS/master/Libs/versions.json'
	remindme = PYMS_SETTINGS.get('remindme', True)
	if remindme == True or remindme != VERSIONS['PyMS']:
		try:
			versions = json.loads(urllib.urlopen(VERSIONS_URL).read())
			PyMS_version = versions['PyMS']
			program_version = versions[program]
		except:
			return
		if VERSIONS['PyMS'] < PyMS_version or VERSIONS[program] < program_version:
			def callback():
				if hasattr(window, '_pyms__window_blocking') and window._pyms__window_blocking:
					window.after(1000, callback)
					return
				UpdateDialog(window,program,versions)
			window.after(1, callback)
class UpdateDialog(PyMSDialog):
	def __init__(self, parent, program, versions):
		self.program = program
		self.versions = versions
		PyMSDialog.__init__(self, parent, 'New Version Found', resizable=(False, False))

	def widgetize(self):
		if VERSIONS[self.program] < self.versions[self.program]:
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

class MPQHandler:
	def __init__(self, mpqs=[], listfiles=None):
		self.mpqs = list(mpqs)
		if listfiles == None:
			self.listfiles = [os.path.join(BASE_DIR,'Libs','Data','Listfile.txt')]
		else:
			self.listfiles = listfiles
		self.handles = {}
		self.open = False
		MpqInitialize()

	def clear(self):
		if self.open:
			self.close_mpqs()
		self.mpqs = []

	def add_defaults(self):
		changed = False
		scdir = PYMS_SETTINGS.get('scdir', autosave=False)
		if scdir and os.path.isdir(scdir):
			for f in ['Patch_rt','BrooDat','StarDat']:
				p = os.path.join(scdir, '%s%smpq' % (f,os.extsep))
				if os.path.exists(p) and not p in self.mpqs:
					h = SFileOpenArchive(p)
					if not SFInvalidHandle(h):
						SFileCloseArchive(h)
						self.mpqs.append(p)
						changed = True
		return changed

	def set_mpqs(self, mpqs):
		if self.open:
			# raise PyMSError('MPQ','Cannot set mpqs when the current mpqs are open.')
			self.close_mpqs()
		self.mpqs = list(mpqs)

	def open_mpqs(self):
		missing = [[],[]]
		if not FOLDER:
			handles = {}
			self.open = True
			for p,m in enumerate(self.mpqs):
				if not os.path.exists(m):
					missing[0].append(m)
					continue
				handles[m] = MpqOpenArchiveForUpdateEx(m, MOAU_OPEN_EXISTING | MOAU_READ_ONLY)
				if SFInvalidHandle(handles[m]):
					missing[1].append(m)
				elif self.open == True:
					self.open = handles[m]
			self.handles = handles
		return missing

	def missing(self, missing):
		t = ''
		if missing[0]:
			t = 'Could not find:\n\t' + '\n\t'.join(missing[0])
		if missing[1]:
			t += 'Error loading:\n\t' + '\n\t'.join(missing[1])
		return t

	def close_mpqs(self):
		self.open = False
		for h in self.handles.values():
			if not SFInvalidHandle(h):
				MpqCloseUpdatedArchive(h)
		self.handles = {}

	# folder(True)=Get only from folder,folder(None)=Get from either, MPQ first, folder second,folder(False)=Get only from MPQ
	def get_file(self, path, folder=None):
		mpq = path.startswith('MPQ:')
		if mpq:
			op = path
			path = path[4:].split('\\')
		if not FOLDER and not folder and mpq:
			if self.open == False:
				self.open_mpqs()
				close = True
			else:
				close = False
			if self.open and self.open != True:
				f = SFileOpenFileEx(None, '\\'.join(path), SFILE_SEARCH_ALL_OPEN)
				if not SFInvalidHandle(f):
					r = SFileReadFile(f)
					SFileCloseFile(f)
					p = SFile(r[0], '\\'.join(path))
					return p
			if close:
				self.close_mpqs()
		if folder != False:
			if mpq:
				p = os.path.join(BASE_DIR, 'Libs', 'MPQ', *path)
				if os.path.exists(p):
					return open(p, 'rb')
			elif os.path.exists(path):
				return open(path, 'rb')
		if mpq:
			return BadFile(op)
		return BadFile(path)

	def has_file(self, path, folder=None):
		mpq = path.startswith('MPQ:')
		if mpq:
			path = path[4:].split('\\')
		if not FOLDER and not folder and mpq:
			if self.open == False:
				self.open_mpqs()
				close = True
			else:
				close = False
			if self.open and self.open != True:
				f = SFileOpenFileEx(self.open, '\\'.join(path), SFILE_SEARCH_ALL_OPEN)
				if not SFInvalidHandle(f):
					SFileCloseFile(f)
					return True
			if close:
				self.close_mpqs()
		if folder != False:
			if mpq:
				return os.path.exists(os.path.join(BASE_DIR, 'Libs', 'MPQ', *path))
			else:
				return os.path.exists(path)
		return False

	# Type: 0 = structs, 1 = dict
	def list_files(self, type=0, handles=None):
		if type == 1:
			files = {}
		else:
			files = []
		if self.mpqs:
			if handles == None:
				handles = self.handles.values()
			elif isinstance(handles, int):
				handles = [handles]
			if self.open == False:
				self.open_mpqs()
				close = True
			else:
				close = False
			for h in handles:
				for e in SFileListFiles(h, '\r\n'.join(self.listfiles)):
					if e.fileExists:
						if type == 1:
							if not e.fileName in self.files:
								self.files[e.fileName] = {}
							self.files[e.locale] = e
						else:
							files.append(e)
			if close:
				self.close_mpqs()
		return files

class MpqSelect(PyMSDialog):
	def __init__(self, parent, mpqhandler, filetype, search, settings, open_type='Open'):
		self.mpqhandler = mpqhandler
		self.search = StringVar()
		self.search.set(search)
		self.search.trace('w', self.updatesearch)
		self.settings = settings
		self.regex = IntVar()
		self.regex.set(0)
		self.files = []
		self.file = None
		self.resettimer = None
		self.searchtimer = None
		self.open_type = open_type
		PyMSDialog.__init__(self, parent, self.open_type + ' a ' + filetype)

	def widgetize(self):
		listframe = Frame(self, bd=2, relief=SUNKEN)
		scrollbar = Scrollbar(listframe)
		self.listbox = Listbox(listframe, width=35, height=10, bd=0, yscrollcommand=scrollbar.set, exportselection=0, activestyle=DOTBOX)
		bind = [
			('<MouseWheel>', self.scroll),
			('<Home>', lambda a,i=0: self.move(a,i)),
			('<End>', lambda a,i=END: self.move(a,i)),
			('<Shift-Up>', lambda e,i=0: self.movestring(e,i)),
			('<Up>', lambda a,i=-1: self.move(a,i)),
			('<Left>', lambda a,i=-1: self.move(a,i)),
			('<Shift-Down>', lambda e,i=1: self.movestring(e,i)),
			('<Down>', lambda a,i=1: self.move(a,i)),
			('<Right>', lambda a,i=-1: self.move(a,i)),
			('<Prior>', lambda a,i=-10: self.move(a,i)),
			('<Next>', lambda a,i=10: self.move(a,i)),
		]
		for b in bind:
			listframe.bind(*b)
		scrollbar.config(command=self.listbox.yview)
		scrollbar.pack(side=RIGHT, fill=Y)
		self.listbox.pack(side=LEFT, fill=BOTH, expand=1)
		listframe.pack(fill=BOTH, padx=1, pady=1, expand=1)
		listframe.focus_set()
		s = Frame(self)
		if isinstance(self.settings, SettingDict):
			history = self.settings.settings.get('mpqselecthistory',[])[::-1]
		else:
			history = self.settings.get('mpqselecthistory',[])[::-1]
		self.textdrop = TextDropDown(s, self.search, history)
		self.textdrop.entry.c = self.textdrop.entry['bg']
		self.textdrop.pack(side=LEFT, fill=X, padx=1, pady=2)
		self.open = Button(s, text=self.open_type, width=10, command=self.ok)
		self.open.pack(side=RIGHT, padx=1, pady=3)
		s.pack(fill=X)
		s = Frame(self)
		Radiobutton(s, text='Wildcard', variable=self.regex, value=0, command=self.updatelist).pack(side=LEFT, padx=1, pady=2)
		Radiobutton(s, text='Regex', variable=self.regex, value=1, command=self.updatelist).pack(side=LEFT, padx=1, pady=2)
		Button(s, text='Cancel', width=10, command=self.cancel).pack(side=RIGHT, padx=1, pady=3)
		s.pack(fill=X)

		self.listfiles()
		self.updatelist()

		return self.open

	def setup_complete(self):
		if isinstance(self.settings, SettingDict):
			self.settings.windows.settings.load_window_size('mpqselect', self)
		elif 'mpqselectwindow' in self.settings:
			loadsize(self, self.settings, 'mpqselectwindow', True)

	def scroll(self, e):
		if e.delta > 0:
			self.listbox.yview('scroll', -2, 'units')
		else:
			self.listbox.yview('scroll', 2, 'units')

	def move(self, e, a):
		if a == END:
			a = self.listbox.size()-2
		elif a not in [0,END]:
			a = max(min(self.listbox.size()-1, int(self.listbox.curselection()[0]) + a),0)
		self.listbox.select_clear(0,END)
		self.listbox.select_set(a)
		self.listbox.see(a)

	def listfiles(self):
		filelists = os.path.join(BASE_DIR,'Libs','Data','Listfile.txt')
		self.files = []
		self.mpqhandler.open_mpqs()
		for h in self.mpqhandler.handles.values():
			for e in SFileListFiles(h, filelists):
				if e.fileName and not e.fileName in self.files:
					self.files.append(e.fileName)
		self.mpqhandler.close_mpqs()
		m = os.path.join(BASE_DIR,'Libs','MPQ','')
		for p in os.walk(m):
			folder = p[0].replace(m,'')
			for f in p[2]:
				a = '%s\\%s' % (folder,f)
				if not a in self.files:
					self.files.append(a)
		self.files.sort()

	def updatelist(self):
		if self.searchtimer:
			self.after_cancel(self.searchtimer)
			self.searchtimer = None
		self.listbox.delete(0,END)
		s = self.search.get()
		if not self.regex.get():
			s = '^' + re.escape(s).replace('\\?','.').replace('\\*','.+?') + '$'
		try:
			r = re.compile(s)
		except:
			self.resettimer = self.after(1000, self.updatecolor)
			self.textdrop.entry['bg'] = '#FFB4B4'
		else:
			for f in filter(lambda p: r.match(p), self.files):
				self.listbox.insert(END,f)
		if self.listbox.size():
			self.listbox.select_set(0)
			self.open['state'] = NORMAL
		else:
			self.open['state'] = DISABLED

	def updatecolor(self):
		if self.resettimer:
			self.after_cancel(self.resettimer)
			self.resettimer = None
		self.textdrop.entry['bg'] = self.textdrop.entry.c

	def updatesearch(self, *_):
		if self.searchtimer:
			self.after_cancel(self.searchtimer)
		self.searchtimer = self.after(200, self.updatelist)

	def ok(self):
		f = self.listbox.get(self.listbox.curselection()[0])
		self.file = 'MPQ:' + f
		if isinstance(self.settings, SettingDict):
			history = self.settings.settings.get('mpqselecthistory', [])
		else:
			if not 'mpqselecthistory' in self.settings:
				self.settings['mpqselecthistory'] = []
			history = self.settings['mpqselecthistory']
		if f in history:
			history.remove(f)
		history.append(f)
		if len(history) > 10:
			del history[0]
		PyMSDialog.ok(self)

	def dismiss(self):
		if isinstance(self.settings, SettingDict):
			self.settings.windows.settings.save_window_size('mpqselect', self)
		else:
			savesize(self, self.settings, 'mpqselectwindow')
		PyMSDialog.dismiss(self)

# TODO: Update settings handling once all programs use Settings objects
class MPQSettings(Frame):
	def __init__(self, parent, mpqs, settings, setdlg=None):
		if setdlg == None:
			self.setdlg = parent.parent
		else:
			self.setdlg = setdlg
		self.mpqs = list(mpqs)
		self.settings = settings
		Frame.__init__(self, parent)
		Label(self, text='MPQ Settings:', font=('Courier', -12, 'bold'), anchor=W).pack(fill=X)
		Label(self, text="Files will be read from the highest priority MPQ that contains them.\nThe higher an MPQ is on the list the higher its priority.", anchor=W, justify=LEFT).pack(fill=X)
		self.listframe = Frame(self, bd=2, relief=SUNKEN)
		scrollbar = Scrollbar(self.listframe)
		self.listbox = Listbox(self.listframe, width=35, height=1, bd=0, yscrollcommand=scrollbar.set, exportselection=0, activestyle=DOTBOX)
		bind = [
			('<MouseWheel>', self.scroll),
			('<Home>', lambda a,i=0: self.move(a,i)),
			('<End>', lambda a,i=END: self.move(a,i)),
			('<Shift-Up>', lambda e,i=0: self.movestring(e,i)),
			('<Up>', lambda a,i=-1: self.move(a,i)),
			('<Left>', lambda a,i=-1: self.move(a,i)),
			('<Shift-Down>', lambda e,i=1: self.movestring(e,i)),
			('<Down>', lambda a,i=1: self.move(a,i)),
			('<Right>', lambda a,i=-1: self.move(a,i)),
			('<Prior>', lambda a,i=-10: self.move(a,i)),
			('<Next>', lambda a,i=10: self.move(a,i)),
		]
		for b in bind:
			self.listframe.bind(*b)
		scrollbar.config(command=self.listbox.yview)
		scrollbar.pack(side=RIGHT, fill=Y)
		self.listbox.pack(side=LEFT, fill=BOTH, expand=1)
		self.listframe.pack(fill=BOTH, padx=1, pady=1, expand=1)
		for mpq in self.mpqs:
			self.listbox.insert(END,mpq)
		if self.listbox.size():
			self.listbox.select_set(0)

		buttons = [
			('add', self.add, 'Add MPQ (Insert)', NORMAL, 'Insert', LEFT),
			('remove', self.remove, 'Remove MPQ (Delete)', DISABLED, 'Delete', LEFT),
			('opendefault', self.adddefault, "Add default StarCraft MPQ's (Shift+Insert)", NORMAL, 'Shift+Insert', LEFT),
			('up', lambda e=None,i=0: self.movempq(e,i), 'Move MPQ Up (Shift+Up)', DISABLED, 'Shift+Up', RIGHT),
			('down', lambda e=None,i=1: self.movempq(e,i), 'Move MPQ Down (Shift+Down)', DISABLED, 'Shift+Down', RIGHT),
		]
		self.buttons = {}
		toolbar = Frame(self)
		for btn in buttons:
			if isinstance(btn, tuple):
				image = PhotoImage(file=os.path.join(BASE_DIR,'Images','%s.gif' % btn[0]))
				button = Button(toolbar, image=image, width=20, height=20, command=btn[1], state=btn[3])
				button.image = image
				button.tooltip = Tooltip(button, btn[2])
				button.pack(side=btn[5], padx=[0,10][btn[0] == 'opendefault'])
				self.buttons[btn[0]] = button
				a = btn[4]
				if a:
					if not a.startswith('F'):
						self.bind('<%s%s>' % (a[:-1].replace('Ctrl','Control').replace('+','-'), a[-1].lower()), btn[1])
					else:
						self.bind('<%s>' % a, btn[1])
			else:
				Frame(toolbar, width=btn).pack(side=LEFT)
		toolbar.pack(fill=X, padx=51, pady=1)

		self.action_states()

	def activate(self):
		self.listframe.focus_set()

	def action_states(self):
		select = [NORMAL,DISABLED][not self.listbox.curselection()]
		for btn in ['remove','up','down']:
			self.buttons[btn]['state'] = select

	def scroll(self, e):
		if e.delta > 0:
			self.listbox.yview('scroll', -2, 'units')
		else:
			self.listbox.yview('scroll', 2, 'units')

	def move(self, e, a):
		if a == END:
			a = self.listbox.size()-2
		elif a not in [0,END]:
			a = max(min(self.listbox.size()-1, int(self.listbox.curselection()[0]) + a),0)
		self.listbox.select_clear(0,END)
		self.listbox.select_set(a)
		self.listbox.see(a)

	def movempq(self, key=None, dir=0):
		if key and self.buttons[['up','down'][dir]]['state'] != NORMAL:
			return
		i = int(self.listbox.curselection()[0])
		if i == [0,self.listbox.size()-1][dir]:
			return
		s = self.listbox.get(i)
		n = i + [-1,1][dir]
		self.mpqs[i] = self.mpqs[n]
		self.mpqs[n] = s
		self.listbox.delete(i)
		self.listbox.insert(n, s)
		self.listbox.select_clear(0, END)
		self.listbox.select_set(n)
		self.listbox.see(n)
		self.setdlg.edited = True

	def select_files(self):
		if isinstance(self.settings, SettingDict):
			return self.settings.lastpath.settings.select_files('mpqs', self, "Add MPQ's", '.mpq', [('MPQ Files','*.mpq'),('All Files','*')])
		else:
			path = self.settings.get('lastpath', BASE_DIR)
			file = tkFileDialog.askopenfilename(parent=self, title="Add MPQ's", defaultextension='.mpq', filetypes=[('MPQ Files','*.mpq'),('All Files','*')], initialdir=path, multiple=True)
			if file:
				self.settings['lastpath'] = os.path.dirname(file[0])
			return file

	def add(self, key=None, add=None):
		if add == None:
			n,s = 0,0
			add = self.select_files()
		else:
			n,s = END,self.listbox.size()
		if add:
			error = []
			for i in add:
				if not i in self.mpqs:
					h = SFileOpenArchive(i)
					if not SFInvalidHandle(h):
						SFileCloseFile(h)
						if n == END:
							self.mpqs.append(i)
						else:
							self.mpqs.insert(int(n),i)
						self.listbox.insert(n,i)
			self.listbox.select_clear(0,END)
			self.listbox.select_set(s)
			self.listbox.see(s)
			self.action_states()
			self.setdlg.edited = True

	def remove(self, key=None):
		if key and self.buttons['remove']['state'] != NORMAL:
			return
		i = int(self.listbox.curselection()[0])
		del self.mpqs[i]
		self.listbox.delete(i)
		if self.listbox.size():
			i = min(i,self.listbox.size()-1)
			self.listbox.select_set(i)
			self.listbox.see(i)
		self.action_states()
		self.setdlg.edited = True

	def adddefault(self, key=None):
		scdir = PYMS_SETTINGS.get('scdir', autosave=False)
		if not scdir or not os.path.isdir(scdir):
			scdir = PYMS_SETTINGS.select_directory('scdir', self, 'Choose StarCraft Directory', store=False)
		if scdir and os.path.isdir(scdir):
			a = []
			for f in ['Patch_rt','BrooDat','StarDat']:
				p = os.path.join(scdir, '%s%smpq' % (f,os.extsep))
				if os.path.exists(p) and not p in self.mpqs:
					a.append(p)
			if len(a) == 3 and not 'scdir' in PYMS_SETTINGS:
				PYMS_SETTINGS.scdir = scdir
				PYMS_SETTINGS.save()
			if a:
				self.add(add=a)

# TODO: Update settings handling once all programs use Settings objects
class SettingsPanel(Frame):
	types = {
		'PCX':(PCX.PCX,'PCX','pcx',[('StarCraft Special Palette','*.pcx'),('All Files','*')]),
		'FNT':(FNT.FNT,'FNT','fnt',[('StarCraft FNT','*.fnt'),('All Files','*')]),
		'GRP':(GRP.GRP,'GRP','grp',[('StarCraft GRP','*.grp'),('All Files','*')]),
		'CacheGRP':(GRP.CacheGRP,'GRP','grp',[('StarCraft GRP','*.grp'),('All Files','*')]),
		'Palette':(PAL.Palette,'Palette','pal',[('RIFF, JASC, and StarCraft PAL','*.pal'),('StarCraft Tileset WPE','*.wpe'),('ZSoft PCX','*.pcx'),('All Files','*')]),
		'WPE':(PAL.Palette,'Palette','wpe',[('StarCraft Tileset WPE','*.wpe'),('RIFF, JASC, and StarCraft PAL','*.pal'),('ZSoft PCX','*.pcx'),('All Files','*')]),
		'TBL':(TBL.TBL,'TBL','tbl',[('StarCraft TBL Files','*.tbl'),('All Files','*')]),
		'AIBIN':(AIBIN.AIBIN,'aiscript.bin','bin',[('AI Scripts','*.bin'),('All Files','*')]),
		'UnitsDAT':(DAT.UnitsDAT,'units.dat','dat',[('StarCraft DAT files','*.dat'),('All Files','*')]),
		'WeaponsDAT':(DAT.WeaponsDAT,'weapons.dat','dat',[('StarCraft DAT files','*.dat'),('All Files','*')]),
		'FlingyDAT':(DAT.FlingyDAT,'flingy.dat','dat',[('StarCraft DAT files','*.dat'),('All Files','*')]),
		'SpritesDAT':(DAT.SpritesDAT,'sprites.dat','dat',[('StarCraft DAT files','*.dat'),('All Files','*')]),
		'ImagesDAT':(DAT.ImagesDAT,'images.dat','dat',[('StarCraft DAT files','*.dat'),('All Files','*')]),
		'UpgradesDAT':(DAT.UpgradesDAT,'uupgrades.dat','dat',[('StarCraft DAT files','*.dat'),('All Files','*')]),
		'TechDAT':(DAT.TechDAT,'techdata.dat','dat',[('StarCraft DAT files','*.dat'),('All Files','*')]),
		'SoundsDAT':(DAT.SoundsDAT,'sfxdata.dat','dat',[('StarCraft DAT files','*.dat'),('All Files','*')]),
		'IScript':(IScriptBIN.IScriptBIN,'iscript.bin','bin',[('IScripts','*.bin'),('All Files','*')]),
	}

	def __init__(self, parent, entries, settings, mpqhandler, setdlg=None):
		if setdlg == None:
			self.setdlg = parent.parent
		else:
			self.setdlg = setdlg
		self.settings = settings
		self.mpqhandler = mpqhandler
		self.find = PhotoImage(file=os.path.join(BASE_DIR,'Images','find.gif'))
		self.variables = {}
		inmpq = False
		Frame.__init__(self, parent)
		for entry in entries:
			if len(entry) == 5:
				f,e,v,t,c = entry
			else:
				f,e,v,t = entry
				c = None
			self.variables[f] = (IntVar(),StringVar(),[])
			if isinstance(v, tuple) or isinstance(v, list):
				profileKey,valueKey = v
				if issubclass(settings, SettingDict):
					profile = settings.settings.get(profileKey, autosave=False)
					v = settings.settings.profiles[profile].get(valueKey, autosave=False)
				else:
					profile = settings[profileKey]
					v = settings['profiles'][profile][valueKey]
			elif isinstance(settings, SettingDict):
				v = settings.settings.files.get(v)
			else:
				v = settings[v]
			m = v.startswith('MPQ:')
			self.variables[f][0].set(m)
			if m:
				self.variables[f][1].set(v[4:])
			else:
				self.variables[f][1].set(v)
			self.variables[f][1].trace('w', self.edited)
			datframe = Frame(self)
			if isstr(e):
				Label(datframe, text=f, font=('Courier', -12, 'bold'), anchor=W).pack(fill=X, expand=1)
				Label(datframe, text=e, anchor=W).pack(fill=X, expand=1)
			elif e:
				Label(datframe, text=f, font=('Courier', -12, 'bold'), anchor=W).pack(fill=X, expand=1)
			else:
				Label(datframe, text=f, anchor=W).pack(fill=X, expand=1)
			entryframe = Frame(datframe)
			e = Entry(entryframe, textvariable=self.variables[f][1], state=DISABLED)
			b = Button(entryframe, image=self.find, width=20, height=20, command=lambda f=f,t=self.types[t],e=e,c=c: self.setting(f,t,e,c))
			self.variables[f][2].extend([e,b])
			if not t == 'Palette':
				inmpq = True
				y = Checkbutton(entryframe, text='', variable=self.variables[f][0])
				self.variables[f][2].append(y)
				y.pack(side=LEFT)
			e.pack(side=LEFT, fill=X, expand=1)
			e.xview(END)
			b.pack(side=LEFT, padx=1)
			entryframe.pack(fill=X, expand=1)
			datframe.pack(side=TOP, fill=X)
		if inmpq:
			Label(self, text='Check the checkbox beside an entry to use a file in the MPQs').pack(fill=X)

	def edited(self, *_):
		if hasattr(self.setdlg, 'edited'):
			self.setdlg.edited = True

	def select_file(self, t, e, f):
		if isinstance(self.settings, SettingDict):
			return self.settings.lastpath.settings.select_file(t, self, "Open a " + t, '.' + e, f)
		else:
			path = self.settings.get('lastpath', BASE_DIR)
			file = tkFileDialog.askopenfilename(parent=self, title="Open a " + t, defaultextension='.' + e, filetypes=f, initialdir=path)
			if file:
				self.settings['lastpath'] = os.path.dirname(file)
			return file

	def setting(self, f, t, e, cb):
		file = ''
		if self.variables[f][0].get():
			m = MpqSelect(self.setdlg, self.mpqhandler, t[1], '*.' + t[2], self.settings)
			if m.file:
				self.mpqhandler.open_mpqs()
				if t[1] == 'FNT':
					file = (self.mpqhandler.get_file(m.file, False),self.mpqhandler.get_file(m.file, True))
				else:
					file = self.mpqhandler.get_file(m.file)
				self.mpqhandler.close_mpqs()
		else:
			file = self.select_file(t[1],t[2],t[3])
		if file:
			c = t[0]()
			if t[1] == 'FNT':
				try:
					c.load_file(file[0])
					self.variables[f][1].set(file[0].file)
				except PyMSError:
					try:
						c.load_file(file[1])
						self.variables[f][1].set(file[0].file)
					except PyMSError, err:
						ErrorDialog(self.setdlg, err)
						return
			else:
				try:
					c.load_file(file)
				except PyMSError, e:
					ErrorDialog(self.setdlg, e)
					return
				self.variables[f][1].set(file)
			e.xview(END)
			if cb:
				cb(c)
			else:
				self.setdlg.edited = True

	def save(self, d, m, settings):
		for s in d[1]:
			v = ['','MPQ:'][self.variables[s[0]][0].get()] + self.variables[s[0]][1].get().replace(m,'MPQ:',1)
			if isinstance(settings, SettingDict):
				settings.settings.files[s[2]] = v
			else:
				settings[s[2]] = v

# TODO: Update settings handling once all programs use Settings objects
class SettingsDialog(PyMSDialog):
	def __init__(self, parent, data, min_size, err=None, mpqs=True, settings=None):
		self.min_size = min_size
		self.data = data
		self.pages = []
		self.err = err
		self.mpqs = mpqs
		self.edited = False
		self.settings = parent.settings if settings == None else settings
		PyMSDialog.__init__(self, parent, 'Settings')

	def widgetize(self):
		self.minsize(*self.min_size)
		if self.data:
			self.tabs = Notebook(self)
			if self.mpqs:
				self.mpqsettings = MPQSettings(self.tabs, self.parent.mpqhandler.mpqs, self.settings)
				self.tabs.add_tab(self.mpqsettings, 'MPQ Settings')
			for d in self.data:
				if isinstance(d[1],list):
					self.pages.append(SettingsPanel(self.tabs, d[1], self.settings, self.parent.mpqhandler))
				else:
					self.pages.append(d[1](self.tabs))
				self.tabs.add_tab(self.pages[-1], d[0])
			self.tabs.pack(fill=BOTH, expand=1, padx=5, pady=5)
		else:
			self.mpqsettings = MPQSettings(self, self.parent.mpqhandler.mpqs, self.settings, self)
			self.mpqsettings.pack(fill=BOTH, expand=1, padx=5, pady=5)
		btns = Frame(self)
		ok = Button(btns, text='Ok', width=10, command=self.ok)
		ok.pack(side=LEFT, padx=3, pady=3)
		Button(btns, text='Cancel', width=10, command=self.cancel).pack(side=LEFT, padx=3, pady=3)
		btns.pack()
		if self.err:
			self.after(1, self.showerr)
		return ok

	def setup_complete(self):
		if isinstance(self.settings, SettingDict):
			self.settings.windows.settings.load_window_size('main', self)
		elif 'settingswindow' in self.settings:
			loadsize(self, self.settings, 'settingswindow', True)

	def showerr(self):
		ErrorDialog(self, self.err)

	def cancel(self):
		if self.err and askyesno(parent=self, title='Exit?', message="One or more files required for this program can not be found and must be chosen. Canceling will close the program, do you wish to continue?"):
			self.parent.after(1, self.parent.exit)
			PyMSDialog.ok(self)
		elif not self.edited or askyesno(parent=self, title='Cancel?', message="Are you sure you want to cancel?\nAll unsaved changes will be lost."):
			PyMSDialog.ok(self)

	def save_settings(self):
		if self.mpqs:
			old_mpqs = self.parent.mpqhandler.mpqs
			self.parent.mpqhandler.set_mpqs(self.mpqsettings.mpqs)
		m = os.path.join(BASE_DIR,'Libs','MPQ','')
		if self.data:
			for p,d in zip(self.pages,self.data):
				p.save(d,m,self.settings)

	def ok(self):
		if self.edited:
			old_mpqs = None
			old_settings = copy.deepcopy(self.settings)
			self.save_settings()
			if hasattr(self.parent, 'open_files'):
				e = self.parent.open_files()
				if e:
					if old_mpqs != None:
						self.parent.mpqhandler.set_mpqs(old_mpqs)
					if isinstance(self.settings, SettingDict):
						self.settings.update(old_settings, set=True)
					else:
						self.settings = old_settings
						self.parent.settings = old_settings
					ErrorDialog(self, e)
					return
			if isinstance(self.settings, SettingDict):
				self.settings.settings.mpqs = self.parent.mpqhandler.mpqs
			else:
				self.settings['mpqs'] = self.parent.mpqhandler.mpqs
		PyMSDialog.ok(self)

	def dismiss(self):
		if isinstance(self.settings, SettingDict):
			self.settings.windows.settings.save_window_size('main', self)
		else:
			savesize(self, self.settings, 'settingswindow', True)
		PyMSDialog.dismiss(self)
