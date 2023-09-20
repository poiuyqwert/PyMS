
from __future__ import annotations

from ..FileFormats.MPQ.MPQ import MPQ, MPQFileEntry

from . import Assets
from .PyMSError import PyMSError
from . import Config

import os, io

from typing import BinaryIO

class MPQHandler(object):
	def __init__(self, mpqs_config: Config.List[str] | None = None, listfiles: list[str] | None = None) -> None:
		self.mpqs_config = mpqs_config
		self.mpqs: list[MPQ] = []
		if listfiles is None:
			self.listfiles = [Assets.data_file_path('Listfile.txt')]
		else:
			self.listfiles = listfiles
		self.open = False
		self.refresh()

	def refresh(self) -> None:
		if self.open:
			self.close_mpqs()
		if self.mpqs_config is None or not self.mpqs_config.data:
			self.add_defaults()
		else:
			self.mpqs = list(MPQ.of(mpq_path) for mpq_path in self.mpqs_config.data)

	def clear(self) -> None:
		if self.open:
			self.close_mpqs()
		self.mpqs = []

	def add_defaults(self) -> None:
		from .setutils import PYMS_CONFIG
		scdir = PYMS_CONFIG.scdir.path
		if scdir is None or not os.path.isdir(scdir):
			return
		for mpq_name in ['Patch_rt','BrooDat','StarDat']:
			mpq_path = os.path.join(scdir, '%s%smpq' % (mpq_name, os.extsep))
			if not os.path.exists(mpq_path) or not not [mpq for mpq in self.mpqs if mpq.path == mpq_path]:
				continue
			mpq = MPQ.of(mpq_path)
			try:
				mpq.open()
				mpq.close()
				self.mpqs.append(mpq)
				if self.mpqs_config is not None:
					self.mpqs_config.data.append(mpq_path)
			except:
				pass

	def open_mpqs(self) -> list[str]:
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

	def close_mpqs(self) -> None:
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
	def get_file(self, path: str, folder: bool | None = None, sources: list[str] = GET_FROM_MPQ_OR_FOLDER) -> BinaryIO | None:
		if folder is not None:
			sources = MPQHandler.GET_FROM_FOLDER if folder else MPQHandler.GET_FROM_MPQ
		file: BinaryIO | None = None
		for source in sources:
			if source == MPQHandler._SOURCE_MPQ:
				file = self.get_file_mpq(path)
				if file:
					return file
			elif source == MPQHandler._SOURCE_FOLDER:
				file = self.get_file_folder(path)
				if file:
					return file
		return file

	def load_file(self, path: str, folder: bool | None = None, sources: list[str] = GET_FROM_MPQ_OR_FOLDER) -> BinaryIO:
		file = self.get_file(path, folder, sources)
		if not file:
			raise PyMSError('Load', f"Couldn't load '{path}' from MPQ")
		return file

	def get_file_mpq(self, path: str) -> BinaryIO | None:
		file: BinaryIO | None = None
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
				file = io.BytesIO(mpq.read_file(path))
				break
			except:
				pass
		if close:
			self.close_mpqs()
		return file

	def get_file_folder(self, path: str) -> BinaryIO | None:
		if path.startswith('MPQ:'):
			path = Assets.mpq_ref_to_file_path(path)
		if os.path.exists(path):
			return open(path, 'rb')
		return None

	def has_file(self, path: str, folder: str | None = None) -> bool:
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

	def list_files(self) -> list[MPQFileEntry]:
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
