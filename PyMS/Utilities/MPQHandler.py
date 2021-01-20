
from utils import BASE_DIR
from setutils import PYMS_SETTINGS
from fileutils import BadFile
from ..FileFormats.MPQ.SFmpq import *

import os

class MPQHandler(object):
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
		if SFMPQ_LOADED:
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
		if SFMPQ_LOADED and not folder and mpq:
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
		if SFMPQ_LOADED and not folder and mpq:
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
                            # TODO: What is with `self.files`?
							if not e.fileName in self.files:
								self.files[e.fileName] = {}
							self.files[e.locale] = e
						else:
							files.append(e)
			if close:
				self.close_mpqs()
		return files
