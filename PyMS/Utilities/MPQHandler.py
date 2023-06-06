
from ..FileFormats.MPQ.MPQ import MPQ, MPQFileEntry

from .setutils import PYMS_SETTINGS
from .fileutils import BadFile, SFile
from . import Assets

import os

from typing import BinaryIO

ReadFile = BinaryIO | SFile | BadFile

class MPQHandler(object):
	def __init__(self, mpq_paths=[], listfiles=None): # type: (list[str], list[str] | None) -> None
		self.mpqs = list(MPQ.of(mpq_path) for mpq_path in mpq_paths)
		if listfiles is None:
			self.listfiles = [Assets.data_file_path('Listfile.txt')]
		else:
			self.listfiles = listfiles
		self.open = False

	def mpq_paths(self): # type: () -> list[str]
		return list(mpq.path for mpq in self.mpqs)

	def clear(self): # type: () -> None
		if self.open:
			self.close_mpqs()
		self.mpqs = []

	def add_defaults(self): # type: () -> bool
		scdir = PYMS_SETTINGS.get('scdir', autosave=False)
		if not scdir or not os.path.isdir(scdir):
			return False
		changed = False
		for mpq_name in ['Patch_rt','BrooDat','StarDat']:
			mpq_path = os.path.join(scdir, '%s%smpq' % (mpq_name, os.extsep))
			if not os.path.exists(mpq_path) or not not [mpq for mpq in self.mpqs if mpq.path == mpq_path]:
				continue
			mpq = MPQ.of(mpq_path)
			try:
				mpq.open()
				mpq.close()
				self.mpqs.append(mpq)
				changed = True
			except:
				pass
		return changed

	def set_mpqs(self, mpq_paths): # type: (list[str]) -> None
		if self.open:
			# raise PyMSError('MPQ','Cannot set mpqs when the current mpqs are open.')
			self.close_mpqs()
		self.mpqs = list(MPQ.of(mpq_path) for mpq_path in mpq_paths)

	def open_mpqs(self): # type: () -> list[str]
		failed = []
		if MPQ.supported():
			self.open = True
			for mpq in self.mpqs:
				try:
					for listfile_path in self.listfiles:
						mpq.add_listfile(listfile_path)
					mpq.open()
				except:
					failed.append(mpq.path)
		return failed

	def close_mpqs(self): # type: () -> None
		self.open = False
		for mpq in self.mpqs:
			try:
				mpq.close()
			except:
				pass

	_SOURCE_FOLDER = 'FOLDER'
	_SOURCE_MPQ = 'MPQ'
	# Only get file from /PyMS/MPQ folder
	GET_FROM_FOLDER = [_SOURCE_FOLDER]
	# Only get file from MPQs
	GET_FROM_MPQ = [_SOURCE_MPQ]
	# Try to get file from /PyMS/MPQ folder, and fallback to MPQ
	GET_FROM_FOLDER_OR_MPQ = GET_FROM_FOLDER + GET_FROM_MPQ
	# Try to get file from MPQ, and fallback to /PyMS/MPQ folder
	GET_FROM_MPQ_OR_FOLDER = GET_FROM_MPQ + GET_FROM_FOLDER
	# TODO: Remove `folder` paramater in favour of `sources`
	# folder(True)=Get only from folder
	# folder(None)=Get from either, MPQ first, folder second
	# folder(False)=Get only from MPQ
	def get_file(self, path, folder=None, sources=GET_FROM_MPQ_OR_FOLDER): # type: (str, str | None, list[str]) -> ReadFile
		if folder is not None:
			sources = MPQHandler.GET_FROM_FOLDER if folder else MPQHandler.GET_FROM_MPQ
		file: ReadFile = BadFile(path)
		for source in sources:
			if source == MPQHandler._SOURCE_MPQ:
				file = self.get_file_mpq(path)
				if not isinstance(file, BadFile):
					return file
			elif source == MPQHandler._SOURCE_FOLDER:
				file = self.get_file_folder(path)
				if not isinstance(file, BadFile):
					return file
		return file

	def get_file_mpq(self, path): # type: (str) -> ReadFile
		file: SFile | BadFile = BadFile(path)
		if not MPQ.supported():
			return file
		path = Assets.mpq_ref_to_file_name(path)
		close = False
		if self.open == False:
			self.open_mpqs()
			close = True
		if not self.open:
			return file
		for mpq in self.mpqs:
			try:
				file = SFile(mpq.read_file(path), path)
				break
			except:
				pass
		if close:
			self.close_mpqs()
		return file

	def get_file_folder(self, path): # type: (str) -> ReadFile
		if path.startswith('MPQ:'):
			path = Assets.mpq_ref_to_file_path(path)
		if os.path.exists(path):
			return open(path, 'rb')
		return BadFile(path)

	def has_file(self, path, folder=None): # type: (str, str | None) -> bool
		in_mpq = path.startswith('MPQ:')
		if MPQ.supported() and not folder and in_mpq:
			file_name = Assets.mpq_ref_to_file_name(path)
			close = False
			if self.open == False:
				self.open_mpqs()
				close = True
			if not self.open:
				return False
			has_file = False
			for mpq in self.mpqs:
				try:
					if mpq.has_file(file_name):
						has_file = True
						break
				except:
					pass
			if close:
				self.close_mpqs()
			return has_file
		if folder != False:
			if in_mpq:
				return os.path.exists(Assets.mpq_ref_to_file_path(path))
			else:
				return os.path.exists(path)
		return False

	def list_files(self): # type: () -> list[MPQFileEntry]
		close = False
		if self.open == False:
			self.open_mpqs()
			close = True
		files = []
		for mpq in self.mpqs:
			try:
				for file in mpq.list_files():
					if not file in files:
						files.append(file)
			except:
				continue
		if close:
			self.close_mpqs()
		return files
