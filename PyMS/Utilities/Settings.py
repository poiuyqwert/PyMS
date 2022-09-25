
from .utils import isstr
from .WarnDialog import WarnDialog
from .UIKit import FileDialog, HORIZONTAL, parse_geometry, parse_resizable
from . import Assets
from .fileutils import check_allow_overwrite_internal_file

import os, copy, json

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
				value = default()
			if not isinstance(default, list):
				value = []
			return value
		self.get(key, get_default)

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

	def load_pane_size(self, key, panedwindow, default=None, index=0):
		if not key in self and default == None:
			return
		panedwindow.update()
		axis = 0 if panedwindow.cget('orient') == HORIZONTAL else 1
		size = [0,0]
		size[axis] = self.get(key, default)
		panedwindow.sash_place(index, *size)

	def load_pane_sizes(self, key, panedwindow, defaults):
		axis = 0 if panedwindow.cget('orient') == HORIZONTAL else 1
		o = 0
		panedwindow.update()
		for n,s in enumerate(self.get(key, defaults)[:len(panedwindow.panes())-1]):
			size = [0,0]
			o += s
			size[axis] = o
			panedwindow.sash_place(n, *size)

	def save_window_size(self, key, window, closing=True):
		resizable_w,resizable_h = parse_resizable(window.resizable())
		w,h,x,y,_ = parse_geometry(window.winfo_geometry())
		if resizable_w or resizable_h:
			z = ''
			if window.is_maximized():
				z = '^'
				window.wm_state('normal')
				window.update_idletasks()
				w,h,x,y,_ = parse_geometry(window.winfo_geometry())
				if not closing:
					window.wm_state('zoomed')
					window.update_idletasks()
			self[key] = '%sx%s+%d+%d%s' % (w,h,x,y,z)
		else:
			self[key] = '+%d+%d' % (x,y)

	def load_window_size(self, key, window, position=None, default_center=True, default_size=None):
		geometry = self.get(key)
		if geometry:
			w,h,x,y,fullscreen = parse_geometry(geometry)
			if position:
				x,y = position
			resizable_w,resizable_h = parse_resizable(window.resizable())
			can_fullscreen = (resizable_w and resizable_h)
			if (resizable_w or resizable_h) and w != None and h != None:
				cur_w,cur_h,_,_,_ = parse_geometry(window.winfo_geometry())
				min_w,min_h = window.minsize()
				# max_w,max_h = window.maxsize()
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
			if fullscreen and can_fullscreen:
				try:
					window.wm_state('zoomed')
				except:
					pass
		else:
			window.update_idletasks()
			w,h,x,y,_ = parse_geometry(window.winfo_geometry())
			geometry = ''
			if default_size:
				w,h = default_size
				geometry = '%dx%d' % default_size
			else:
				geometry = '%dx%d' % (w,h)
			if position:
				geometry += '+%d+%d' % position
			elif default_center or geometry:
				window.update_idletasks()
				screen_w = window.winfo_screenwidth()
				screen_h = window.winfo_screenheight()
				geometry += '+%d+%d' % ((screen_w-w)/2,(screen_h-h)/2)
			window.geometry(geometry)

	def _process_filetypes(self, filetypes, include_all_filetype):
		if include_all_filetype and filetypes:
			for _, check_ext in filetypes:
				if check_ext == '*':
					break
			else:
				filetypes = list(filetypes)
				filetypes.append(('All Files', '*'))
		return filetypes

	def _process_extension(self, ext, filetypes):
		if not ext and filetypes:
			ext = filetypes[0][1]
		if ext:
			if ';' in ext:
				ext = ext.split(';')[0]
			if os.extsep in ext:
				ext = os.path.splitext(ext)[1]
		return ext

	def _select_file(self, parent, key, title, ext, filetypes, filename, store, include_all_filetype, save):
		dialog = FileDialog.asksaveasfilename if save else FileDialog.askopenfilename
		filetypes = self._process_filetypes(filetypes, include_all_filetype)
		ext = self._process_extension(ext, filetypes)
		initialfile = None
		if filename:
			try:
				initialfile = os.path.basename(filename) or None
			except:
				pass
		parent._pyms__window_blocking = True
		kwargs = {}
		if filetypes:
			kwargs['filetypes'] = filetypes
		if ext:
			kwargs['defaultextension'] = ext
		if initialfile:
			kwargs['initialfile'] = initialfile
		path = dialog(parent=parent, title=title, initialdir=self.get(key, Assets.base_dir, autosave=store), **kwargs)
		if save and path and not check_allow_overwrite_internal_file(path):
			path = None
		parent._pyms__window_blocking = False
		if path and store:
			self[key] = os.path.dirname(path)
		return path

	def select_save_file(self, parent, key='save', title='Save File', ext=None, filetypes=None, filename=None, store=True, include_all_filetype=True):
		return self._select_file(parent, key, title, ext, filetypes, filename, store, include_all_filetype, True)

	def select_open_file(self, parent, key='open', title='Open File', ext=None, filetypes=None, store=True, include_all_filetype=True):
		return self._select_file(parent, key, title, ext, filetypes, None, store, include_all_filetype, False)

	def select_open_files(self, parent, key='open', title='Open Files', ext=None, filetypes=None, store=True, include_all_filetype=True):
		filetypes = self._process_filetypes(filetypes, include_all_filetype)
		ext = self._process_extension(ext, filetypes)
		parent._pyms__window_blocking = True
		kwargs = {}
		if filetypes:
			kwargs['filetypes'] = filetypes
		if ext:
			kwargs['defaultextension'] = ext
		paths = FileDialog.askopenfilename(parent=parent, title=title, initialdir=self.get(key, Assets.base_dir, autosave=store), multiple=True, **kwargs)
		parent._pyms__window_blocking = False
		if isstr(paths):
			if paths:
				paths = [paths]
			else:
				paths = []
		if paths:
			paths = sorted(paths)
			if store:
				self[key] = os.path.dirname(paths[0])
		return paths

	def select_directory(self, parent, key='dir', title='Select Folder', store=True):
		parent._pyms__window_blocking = True
		path = FileDialog.askdirectory(parent=parent, title=title, initialdir=self.get(key, Assets.base_dir, autosave=store))
		parent._pyms__window_blocking = False
		if path and store:
			self[key] = path
		return path

	def warn(self, key, parent, message, title='Warning!'):
		if self.get(key):
			return
		w = WarnDialog(parent, message, title, show_dont_warn=True)
		if w.dont_warn.get():
			self[key] = True

class SettingEncoder(json.JSONEncoder):
	def default(self, obj):
		if isinstance(obj, SettingDict):
			return obj.__dict__['_settings']
		return json.JSONEncoder.default(self, obj)

class Settings(SettingDict):
	def __init__(self, program, settings_version):
		self.__dict__['path'] = Assets.settings_file_path(program)
		self.__dict__['version'] = settings_version
		try:
			with open(self.__dict__['path'], 'r') as f:
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
			with open(self.__dict__['path'], 'w') as f:
				json.dump(self, f, sort_keys=True, indent=4, cls=SettingEncoder)
		except:
			pass
        