
from . import StormLib as _StormLib
from . import SFmpq as _SFmpq

import re as _re
import os as _os

from ...Utilities.PyMSError import PyMSError

class MPQLibrary:
	# default = 0

	stormlib = 1
	sfmpq = 2

	@staticmethod
	def name(library): # type: (int) -> str
		if library == MPQLibrary.stormlib:
			return 'StormLib'
		elif library == MPQLibrary.sfmpq:
			return 'SFmpq'
		else:
			return 'None'

class MPQLocale:
	neutral    = 0 # Neutral (English US)
	chinese    = 1028 # 0x404 (Taiwan)
	czech      = 1029 # 0x405
	german     = 1031 # 0x407
	english    = 1032 # 0x409
	spanish    = 1034 # 0x40A
	french     = 1036 # 0x40C
	italian    = 1040 # 0x410 
	japanese   = 1041 # 0x411
	korean     = 1042 # 0x412
	polish     = 1045 # 0x415
	portuguese = 1046 # 0x416
	russian    = 1049 # 0x419
	english_uk = 2056 # 0x808

class MPQCompressionFlag:
	none       = 0

	huffman    = (1 << 0) # 0x01
	zlib       = (1 << 1) # 0x02
	pkware     = (1 << 3) # 0x08
	wav_mono   = (1 << 6) # 0x40
	wav_stereo = (1 << 7) # 0x80
	
	implode    = (1 << 15) # This translates to a file flag, not a compression type

class MPQFileFlag:
	none          = 0

	encrypted     = (1 << 0)
	mod_crypt_key = (1 << 1)

class MPQInternalFile:
	attributes = "(attributes)"
	listfile = "(listfile)"
	signature = "(signature)"

class MPQFileEntry(object):
	def __init__(self, file_name=None, locale=None):
		self.file_name = file_name # type: str
		self.full_size = None # type: int
		self.compressed_size = None # type: int
		self.locale = locale # type: int
		# `compressed` includes if it is using "implode", and not just "compress"
		self.compressed = None # type: bool 
		self.encrypted = None # type: bool 
		self.mod_crypt_key = None # type: bool 
		self.flags = None

	def get_compression_ratio(self):
		if self.full_size:
			return self.compressed_size / float(self.full_size)
		return 0

	def __eq__(self, other):
		if not isinstance(other, MPQFileEntry):
			return
		return self.file_name == other.file_name and self.locale == other.locale

	def __repr__(self):
		return "<MPQFileEntry object at %s: '%s', locale %d, flags %08X>" % (hex(id(self)), self.file_name, self.locale, self.flags)

	def __lt__(self, other): # type: (MPQFileEntry) -> bool
		if not isinstance(other, MPQFileEntry):
			raise Exception("Can't compare `%s` to `%s`", self.__class__.__name__, other.__class__.__name__)
		if self.file_name == other.file_name:
			return self.locale < other.locale
		return self.file_name < other.file_name

# MPQ is an abstract class. Use `MPQ.of()` to get a type-erased, concrete, implementation.
# A different implementation will be returned depending on supported libraries
class MPQ(object):
	@staticmethod
	def of(mpq_path): # type: (str) -> MPQ
		if _StormLib.STORMLIB_LOADED:
			return StormLibMPQ(mpq_path)
		elif _SFmpq.SFMPQ_LOADED:
			return SFMPQ(mpq_path)
		else:
			raise PyMSError('MPQ', "Couldn't load StormLib or SFmpq")

	@staticmethod
	def default_library(): # type: () -> (int | None)
		if _StormLib.STORMLIB_LOADED:
			return MPQLibrary.stormlib
		elif _SFmpq.SFMPQ_LOADED:
			return MPQLibrary.sfmpq
		else:
			return None

	@staticmethod
	def supported(): # type: () -> bool
		return MPQ.default_library() != None

	def __init__(self, path): # type: (str) -> MPQ
		self.path = path

	class _WithContextManager(object):
		def __init__(self, mpq, auto_close): # type: (MPQ, bool) -> MPQ._WithContextManager
			self.mpq = mpq
			self.auto_close = auto_close

		def __enter__(self):
			return self

		def __exit__(self, exc_type, exc_value, traceback):
			if self.auto_close:
				self.mpq.close()
			return False

	def library(self): # type: () -> int
		raise NotImplementedError(self.__class__.__name__ + '.library()')

	def is_open(self): # type: () -> bool
		raise NotImplementedError(self.__class__.__name__ + '.is_open()')

	def is_read_only(self): # type: () -> (bool | None)
		raise NotImplementedError(self.__class__.__name__ + '.is_read_only()')

	def open(self, read_only=True): # type: (bool) -> MPQ._WithContextManager
		raise NotImplementedError(self.__class__.__name__ + '.close()')

	# `sector_size_shift` is used like `512 << sector_size_shift` to calculate the `sector_size`
	def create(self, max_files=1024, sector_size_shift=3, stay_open=True): # type: (int, int, bool) -> MPQ._WithContextManager
		raise NotImplementedError(self.__class__.__name__ + '.create()')

	def open_or_create(self, max_files=1024, sector_size_shift=3): # type: (int, int) -> MPQ._WithContextManager
		if _os.path.exists(self.path):
			return self.open(read_only=False)
		else:
			return self.create(max_files, sector_size_shift)

	def close(self):
		raise NotImplementedError(self.__class__.__name__ + '.close()')

	def used_block_count(self): # () -> int
		raise NotImplementedError(self.__class__.__name__ + '.used_block_count()')

	def add_listfile(self, listfile_path): # type: (str) -> None
		raise NotImplementedError(self.__class__.__name__ + '.add_listfile()')

	def list_files(self, filter=None): # type: (str | _re.Pattern[str]) -> list[MPQFileEntry]
		raise NotImplementedError(self.__class__.__name__ + '.list_files()')

	def has_file(self, file_name, locale=MPQLocale.neutral): # type: (str, int) -> bool
		raise NotImplementedError(self.__class__.__name__ + '.has_file()')

	def read_file(self, file_name, locale=MPQLocale.neutral): # type: (str, int) -> bytes
		raise NotImplementedError(self.__class__.__name__ + '.read_file()')

	# `compression_level` may not be supported by all implementations
	def add_file(self, file_path, file_name, locale=MPQLocale.neutral, flags=MPQFileFlag.none, compression=MPQCompressionFlag.none, compression_level=0): # type: (str, str, int, int, int, int) -> None
		raise NotImplementedError(self.__class__.__name__ + '.add_file()')

	# `compression_level` may not be supported by all implementations
	def add_data(self, data, file_name, locale=MPQLocale.neutral, flags=MPQFileFlag.none, compression=MPQCompressionFlag.none, compression_level=0): # type: (bytes, str, int, int, int, int) -> None
		raise NotImplementedError(self.__class__.__name__ + '.add_data()')

	def rename_file(self, file_name, new_file_name, locale=MPQLocale.neutral): # type: (str, str, int) -> None
		raise NotImplementedError(self.__class__.__name__ + '.rename_file()')

	def change_file_locale(self, file_name, locale, new_locale): # type: (str, int, int) -> None
		raise NotImplementedError(self.__class__.__name__ + '.change_file_locale()')

	def delete_file(self, file_name, locale=MPQLocale.neutral): # type: (str, int) -> None
		raise NotImplementedError(self.__class__.__name__ + '.delete_file()')

	def compact(self):
		raise NotImplementedError(self.__class__.__name__ + '.compact()')

	def flush(self):
		raise NotImplementedError(self.__class__.__name__ + '.flush()')

class StormLibMPQ(MPQ):
	def __init__(self, path): # type: (str) -> MPQ
		MPQ.__init__(self, path)
		self.mpq_handle = None # type: _StormLib.MPQHANDLE
		self.read_only = True
		self.listfiles = []

	def library(self): # type: () -> int
		return MPQLibrary.stormlib

	def is_open(self): # type: () -> bool
		return (self.mpq_handle != None)

	def is_read_only(self): # type: () -> (bool | None)
		if not self.is_open():
			return None
		return self.read_only

	def _add_listfiles(self):
		if not self.is_open():
			return
		for listfile_path in self.listfiles:
			error = _StormLib.SFileAddListFile(self.mpq_handle, listfile_path)
			if error:
				raise PyMSError('MPQ', "Error adding listfile '%s' (%d)" % (listfile_path, error))

	def open(self, read_only=True): # type: (bool) -> MPQ._WithContextManager
		auto_close = False
		if not self.is_open():
			mpq_handle = _StormLib.SFileOpenArchive(self.path, flags=(_StormLib.STREAM_FLAG_READ_ONLY if read_only else 0))
			if _StormLib.SFInvalidHandle(mpq_handle):
				raise PyMSError('MPQ', "Error opening MPQ '%s' (%d)" % (self.path, _StormLib.SFGetLastError()))
			self.mpq_handle = mpq_handle
			self.read_only = read_only
			self._add_listfiles()
			auto_close = True
		elif not read_only and self.read_only:
			raise PyMSError('MPQ', "MPQ is already open as read-only")
		return MPQ._WithContextManager(self, auto_close)

	def create(self, max_files=1024, sector_size_shift=3, stay_open=True): # type: (int, int, bool) -> MPQ._WithContextManager
		if self.mpq_handle:
			raise PyMSError('MPQ', "MPQ is already open")
		
		create_info = _StormLib.SFILE_CREATE_MPQ()
		# CreateInfo.dwMpqVersion   = (dwCreateFlags & MPQ_CREATE_ARCHIVE_VMASK) >> FLAGS_TO_FORMAT_SHIFT;
		create_info.mpq_version = _StormLib.MPQ_FORMAT_VERSION_1
		# CreateInfo.dwStreamFlags  = STREAM_PROVIDER_FLAT | BASE_PROVIDER_FILE;
		create_info.stream_flags = _StormLib.STREAM_PROVIDER_FLAT | _StormLib.BASE_PROVIDER_FILE
		# CreateInfo.dwFileFlags1   = (dwCreateFlags & MPQ_CREATE_LISTFILE)   ? MPQ_FILE_DEFAULT_INTERNAL : 0;
		create_info.file_flags_listfile = _StormLib.MPQ_FILE_DEFAULT_INTERNAL
		# CreateInfo.dwFileFlags2   = (dwCreateFlags & MPQ_CREATE_ATTRIBUTES) ? MPQ_FILE_DEFAULT_INTERNAL : 0;
		create_info.file_flags_signature = 0
		# CreateInfo.dwFileFlags3   = (dwCreateFlags & MPQ_CREATE_SIGNATURE)  ? MPQ_FILE_DEFAULT_INTERNAL : 0;
		create_info.file_flags_attributes = 0
		# CreateInfo.dwAttrFlags    = (dwCreateFlags & MPQ_CREATE_ATTRIBUTES) ? (MPQ_ATTRIBUTE_CRC32 | MPQ_ATTRIBUTE_FILETIME | MPQ_ATTRIBUTE_MD5) : 0;
		create_info.attributes_flags = 0
		# CreateInfo.dwSectorSize   = (CreateInfo.dwMpqVersion >= MPQ_FORMAT_VERSION_3) ? 0x4000 : 0x1000;
		create_info.sector_size = (512 << sector_size_shift)
		# CreateInfo.dwRawChunkSize = (CreateInfo.dwMpqVersion >= MPQ_FORMAT_VERSION_4) ? 0x4000 : 0;
		create_info.raw_chunk_size = 0
		# CreateInfo.dwMaxFileCount = dwMaxFileCount;
		create_info.max_file_count = max_files

		mpq_handle = _StormLib.SFileCreateArchive2(self.path, create_info)
		if _StormLib.SFInvalidHandle(mpq_handle):
			raise PyMSError('MPQ', "Error creating MPQ '%s' (%d)" % (self.path, _StormLib.SFGetLastError()))
		self.mpq_handle = mpq_handle
		self.read_only = False
		if stay_open:
			self._add_listfiles()
		else:
			self.close()

		return MPQ._WithContextManager(self, auto_close=True)

	def close(self):
		if not self.is_open():
			return
		if not _StormLib.SFileCloseArchive(self.mpq_handle):
			raise PyMSError('MPQ', "Error closing MPQ (%d)" % _StormLib.SFGetLastError())
		self.mpq_handle = None

	def _check_open_status(self, editing): # type: (bool) -> None
		if not self.is_open():
			raise PyMSError('MPQ', "MPQ is not open")
		if editing and self.is_read_only():
			raise PyMSError('MPQ', "MPQ is open as read-only")

	def used_block_count(self): # () -> int
		self._check_open_status(editing=False)

		count = _StormLib.SFileGetFileInfo(self.mpq_handle, _StormLib.SFileMpqBlockTableSize)
		if count == None:
			raise PyMSError('MPQ', "Error getting block count (%d)" % _StormLib.SFGetLastError())
		return count

	def add_listfile(self, listfile_path): # type: (str) -> None
		if listfile_path in self.listfiles:
			return
		# TODO: Check if file exists?
		self.listfiles.append(listfile_path)
		if self.mpq_handle:
			error = _StormLib.SFileAddListFile(self.mpq_handle, listfile_path)
			if error:
				raise PyMSError('MPQ', "Error adding listfile '%s' (%d)" % (listfile_path, error))

	def list_files(self, filter=None): # type: (str | _re.Pattern[str]) -> list[MPQFileEntry]
		self._check_open_status(editing=False)

		mask = '*'
		regex = None
		if isinstance(filter, str):
			mask = filter
		elif isinstance(filter, _re._pattern_type):
			regex = filter
		
		find_handle,file_data = _StormLib.SFileFindFirstFile(self.mpq_handle, mask)
		if _StormLib.SFInvalidHandle(find_handle):
			return []

		def file_entry_from_file_data(file_data): # type: (_StormLib.SFILE_FIND_DATA) -> (MPQFileEntry)
			file_entry = MPQFileEntry()
			file_entry.file_name = file_data.file_name
			file_entry.full_size = file_data.file_size
			file_entry.compressed_size = file_data.compressed_size
			file_entry.locale = file_data.locale
			file_entry.flags = file_data.file_flags
			file_entry.compressed = (file_data.file_flags & _StormLib.MPQ_FILE_IMPLODE) == _StormLib.MPQ_FILE_IMPLODE or (file_data.file_flags & _StormLib.MPQ_FILE_COMPRESS) == _StormLib.MPQ_FILE_COMPRESS
			file_entry.encrypted = (file_data.file_flags & _StormLib.MPQ_FILE_ENCRYPTED) == _StormLib.MPQ_FILE_ENCRYPTED
			file_entry.mod_crypt_key = (file_data.file_flags & _StormLib.MPQ_FILE_FIX_KEY) == _StormLib.MPQ_FILE_FIX_KEY
			return file_entry

		results = []
		try:
			while file_data:
				if not regex or regex.match(file_data.file_name):
					file_entry = file_entry_from_file_data(file_data)
					results.append(file_entry)
				file_data = _StormLib.SFileFindNextFile(find_handle)
		except:
			raise
		finally:
			_StormLib.SFileFindClose(find_handle)
		
		return results

	def has_file(self, file_name, locale=MPQLocale.neutral): # type: (str, int) -> bool
		self._check_open_status(editing=False)
		_StormLib.SFileSetLocale(locale)
		
		return _StormLib.SFileHasFile(self.mpq_handle, file_name)

	def read_file(self, file_name, locale=MPQLocale.neutral): # type: (str, int) -> bytes
		self._check_open_status(editing=False)
		_StormLib.SFileSetLocale(locale)
		
		file_handle = _StormLib.SFileOpenFileEx(self.mpq_handle, file_name)
		if _StormLib.SFInvalidHandle(file_handle):
			raise PyMSError('MPQ', "Error opening file '%s' (%d)" % (file_name, _StormLib.SFGetLastError()))

		try:
			data,_ = _StormLib.SFileReadFile(file_handle)
		except:
			raise
		finally:
			_StormLib.SFileCloseFile(file_handle)
		if not data:
			raise PyMSError('MPQ', "Error reading file '%s' (%d)" % (file_name, _StormLib.SFGetLastError()))

		return data

	def _storm_file_settings(self, flags, compression): # type: (int, int) -> tuple[int, int]
		storm_flags = _StormLib.MPQ_FILE_REPLACEEXISTING
		storm_compression = compression

		if storm_compression & MPQCompressionFlag.implode:
			storm_flags |= _StormLib.MPQ_FILE_IMPLODE
			storm_compression = MPQCompressionFlag.none
		elif storm_compression:
			storm_flags |= _StormLib.MPQ_FILE_COMPRESS
		if flags & MPQFileFlag.encrypted:
			storm_flags |= _StormLib.MPQ_FILE_ENCRYPTED
		if flags & MPQFileFlag.mod_crypt_key:
			storm_flags |= _StormLib.MPQ_FILE_FIX_KEY

		return (storm_flags, storm_compression)

	# `compression_level` is not supported
	def add_file(self, file_path, file_name, locale=MPQLocale.neutral, flags=MPQFileFlag.none, compression=MPQCompressionFlag.none, compression_level=0): # type: (bytes, str, int, int, int, int) -> None
		self._check_open_status(editing=True)
		_StormLib.SFileSetLocale(locale)

		storm_flags, storm_compression = self._storm_file_settings(flags, compression)
		if not _StormLib.SFileAddFileEx(self.mpq_handle, file_path, file_name, storm_flags, storm_compression):
			raise PyMSError('MPQ', "Error adding file '%s' (%d)" % (file_name, _StormLib.SFGetLastError()))

	# `compression_level` is not supported
	def add_data(self, data, file_name, locale=MPQLocale.neutral, flags=MPQFileFlag.none, compression=MPQCompressionFlag.none, compression_level=0): # type: (bytes, str, int, int, int, int) -> None
		self._check_open_status(editing=True)

		storm_flags, storm_compression = self._storm_file_settings(flags, compression)
		file_handle = _StormLib.SFileCreateFile(self.mpq_handle, file_name, 0, len(data), locale, storm_flags)
		if _StormLib.SFInvalidHandle(file_handle):
			raise PyMSError('MPQ', "Error creating file '%s' (%d)" % (file_name, _StormLib.SFGetLastError()))

		try:
			if not _StormLib.SFileWriteFile(file_handle, data, storm_compression):
				raise PyMSError('MPQ', "Error writing data to file '%s' (%d)" % (file_name, _StormLib.SFGetLastError()))
		except:
			raise
		finally:
			_StormLib.SFileFinishFile(file_handle)

	def rename_file(self, file_name, new_file_name, locale=MPQLocale.neutral): # type: (str, str, int) -> None
		self._check_open_status(editing=True)
		_StormLib.SFileSetLocale(locale)

		if not _StormLib.SFileRenameFile(self.mpq_handle, file_name, new_file_name):
			raise PyMSError('MPQ', "Error renaming file '%s' to '%s' (%d)" % (file_name, new_file_name, _StormLib.SFGetLastError()))

	def change_file_locale(self, file_name, locale, new_locale): # type: (str, int, int) -> None
		self._check_open_status(editing=True)
		_StormLib.SFileSetLocale(locale)
		
		file_handle = _StormLib.SFileOpenFileEx(self.mpq_handle, file_name)
		if _StormLib.SFInvalidHandle(file_handle):
			raise PyMSError('MPQ', "Error opening file '%s' (%d)" % (file_name, _StormLib.SFGetLastError()))

		try:
			if not _StormLib.SFileSetFileLocale(file_handle, new_locale):
				raise PyMSError('MPQ', "Error setting locale of file '%s' with locale %d to locale %d (%d)" % (file_name, locale, new_locale, _StormLib.SFGetLastError()))
		except:
			raise
		finally:
			_StormLib.SFileCloseFile(file_handle)

	def delete_file(self, file_name, locale=MPQLocale.neutral): # type: (str, int) -> None
		self._check_open_status(editing=True)
		_StormLib.SFileSetLocale(locale)

		if not _StormLib.SFileRemoveFile(self.mpq_handle, file_name):
			raise PyMSError('MPQ', "Error deleting file '%s' (%d)" % (file_name, _StormLib.SFGetLastError()))

	def compact(self):
		self._check_open_status(editing=True)

		if not _StormLib.SFileCompactArchive(self.mpq_handle):
			raise PyMSError('MPQ', "Error compacting MPQ (%d)" % _StormLib.SFGetLastError())

	def flush(self):
		if not self.is_open() or self.is_read_only():
			return
		_StormLib.SFileFlushArchive(self.mpq_handle)

class SFMPQ(MPQ):
	def __init__(self, path): # type: (str) -> MPQ
		MPQ.__init__(self, path)
		self.mpq_handle = None # type: _StormLib.MPQHANDLE
		self.read_only = True
		self.listfiles = []

	def library(self): # type: () -> int
		return MPQLibrary.sfmpq

	def is_open(self): # type: () -> bool
		return (self.mpq_handle != None)

	def is_read_only(self): # type: () -> (bool | None)
		if not self.is_open():
			return None
		return self.read_only

	def open(self, read_only=True): # type: (bool) -> MPQ._WithContextManager
		auto_close = False
		if not self.is_open():
			if read_only:
				mpq_handle = _SFmpq.SFileOpenArchive(self.path)
			else:
				mpq_handle = _SFmpq.MpqOpenArchiveForUpdate(self.path, _SFmpq.MOAU_OPEN_EXISTING | _SFmpq.MOAU_MAINTAIN_LISTFILE)
			if _SFmpq.SFInvalidHandle(mpq_handle):
				raise PyMSError('MPQ', "Error opening MPQ '%s' (%d)" % (self.path, _SFmpq.SFGetLastError()))
			self.mpq_handle = mpq_handle
			self.read_only = read_only
			auto_close = True
		elif not read_only and self.read_only:
			raise PyMSError('MPQ', "MPQ is already open as read-only")
		return MPQ._WithContextManager(self, auto_close)

	def create(self, max_files=1024, sector_size_shift=3, stay_open=True): # type: (int, int, bool) -> MPQ._WithContextManager
		if self.mpq_handle:
			raise PyMSError('MPQ', "MPQ is already open")

		mpq_handle = _SFmpq.MpqOpenArchiveForUpdateEx(self.path, _SFmpq.MOAU_CREATE_ALWAYS | _SFmpq.MOAU_MAINTAIN_LISTFILE, max_files, sector_size_shift)
		if _SFmpq.SFInvalidHandle(mpq_handle):
			raise PyMSError('MPQ', "Error creating MPQ '%s' (%d)" % (self.path, _SFmpq.SFGetLastError()))
		self.mpq_handle = mpq_handle
		self.read_only = False
		if not stay_open:
			self.close()

		return MPQ._WithContextManager(self, auto_close=True)

	def close(self):
		if not self.is_open():
			return
		if not _SFmpq.SFileCloseArchive(self.mpq_handle):
			raise PyMSError('MPQ', "Error closing MPQ (%d)" % _SFmpq.SFGetLastError())
		self.mpq_handle = None

	def _check_open_status(self, editing): # type: (bool) -> None
		if not self.is_open():
			raise PyMSError('MPQ', "MPQ is not open")
		if editing and self.is_read_only():
			raise PyMSError('MPQ', "MPQ is open as read-only")

	def used_block_count(self): # () -> int
		self._check_open_status(editing=False)

		count = _SFmpq.SFileGetFileInfo(self.mpq_handle, _SFmpq.SFILE_INFO_NUM_FILES)
		if count == None:
			raise PyMSError('MPQ', "Error getting block count (%d)" % _SFmpq.SFGetLastError())
		return count

	def add_listfile(self, listfile_path): # type: (str) -> None
		if listfile_path in self.listfiles:
			return
		# TODO: Check if file exists?
		self.listfiles.append(listfile_path)

	def list_files(self, filter=None): # type: (str | _re.Pattern[str]) -> list[MPQFileEntry]
		self._check_open_status(editing=False)

		regex = None
		if isinstance(filter, str) and filter.replace('*',''):
			regex = _re.compile('^' + _re.escape(filter).replace('\\?','.').replace('\\*','.*') + '$')
		elif isinstance(filter, _re._pattern_type):
			regex = filter
		
		list_entries = _SFmpq.SFileListFiles(self.mpq_handle, str('\r\n'.join(self.listfiles)))

		def file_entry_from_file_list_entry(file_list_entry): # type: (_SFmpq.FILELISTENTRY) -> (MPQFileEntry)
			file_entry = MPQFileEntry()
			file_entry.file_name = file_list_entry.fileName
			file_entry.full_size = file_list_entry.fullSize
			file_entry.compressed_size = file_list_entry.compressedSize
			file_entry.locale = file_list_entry.locale
			file_entry.flags = file_list_entry.flags
			file_entry.compressed = (file_list_entry.flags & _SFmpq.MAFA_COMPRESS2) == _SFmpq.MAFA_COMPRESS2 or (file_list_entry.flags & _SFmpq.MAFA_COMPRESS) == _SFmpq.MAFA_COMPRESS
			file_entry.encrypted = (file_list_entry.flags & _SFmpq.MAFA_ENCRYPT) == _SFmpq.MAFA_ENCRYPT
			file_entry.mod_crypt_key = (file_list_entry.flags & _SFmpq.MAFA_MODCRYPTKEY) == _SFmpq.MAFA_MODCRYPTKEY
			return file_entry

		return list(file_entry_from_file_list_entry(list_entry) for list_entry in list_entries if list_entry.fileExists and (regex == None or regex.match(list_entry.fileName)))

	def has_file(self, file_name, locale=MPQLocale.neutral): # type: (str, int) -> bool
		self._check_open_status(editing=False)
		_SFmpq.SFileSetLocale(locale)

		file_handle = _SFmpq.SFileOpenFileEx(self.mpq_handle, file_name)
		has_file = not _SFmpq.SFInvalidHandle(file_handle)
		_SFmpq.SFileCloseFile(file_handle)
		return has_file

	def read_file(self, file_name, locale=MPQLocale.neutral): # type: (str, int) -> bytes
		self._check_open_status(editing=False)
		_SFmpq.SFileSetLocale(locale)

		file_handle = _SFmpq.SFileOpenFileEx(self.mpq_handle, file_name)
		if _SFmpq.SFInvalidHandle(file_handle):
			raise PyMSError('MPQ', "Error opening file '%s' (%d)" % (file_name, _SFmpq.SFGetLastError()))

		try:
			data,_ = _SFmpq.SFileReadFile(file_handle)
		except:
			raise
		finally:
			_SFmpq.SFileCloseFile(file_handle)
		if not data:
			raise PyMSError('MPQ', "Error reading file '%s' (%d)" % (file_name, _SFmpq.SFGetLastError()))

		return data

	def _sfmpq_file_settings(self, flags, compression): # type: (int, int) -> tuple[int, int]
		sfmpq_flags = _SFmpq.MAFA_REPLACE_EXISTING
		sfmpq_compression = compression

		if sfmpq_compression & MPQCompressionFlag.implode:
			sfmpq_flags |= _SFmpq.MAFA_COMPRESS2
			sfmpq_compression = MPQCompressionFlag.none
		elif sfmpq_compression:
			sfmpq_flags |= _SFmpq.MAFA_COMPRESS
		if flags & MPQFileFlag.encrypted:
			sfmpq_flags |= _SFmpq.MAFA_ENCRYPT
		if flags & MPQFileFlag.mod_crypt_key:
			sfmpq_flags |= _SFmpq.MAFA_MODCRYPTKEY

		return (sfmpq_flags, sfmpq_compression)

	def add_file(self, file_path, file_name, locale=MPQLocale.neutral, flags=MPQFileFlag.none, compression=MPQCompressionFlag.none, compression_level=0): # type: (bytes, str, int, int, int, int) -> None
		self._check_open_status(editing=True)
		_SFmpq.SFileSetLocale(locale)

		sfmpq_flags, sfmpq_compression = self._sfmpq_file_settings(flags, compression)
		if not _SFmpq.MpqAddFileToArchiveEx(self.mpq_handle, file_path, file_name, sfmpq_flags, sfmpq_compression, compression_level):
			raise PyMSError('MPQ', "Error adding file '%s' (%d)" % (file_name, _SFmpq.SFGetLastError()))

	def add_data(self, data, file_name, locale=MPQLocale.neutral, flags=MPQFileFlag.none, compression=MPQCompressionFlag.none, compression_level=0): # type: (bytes, str, int, int, int, int) -> None
		self._check_open_status(editing=True)
		_SFmpq.SFileSetLocale(locale)

		sfmpq_flags, sfmpq_compression = self._sfmpq_file_settings(flags, compression)
		if not _SFmpq.MpqAddFileFromBufferEx(self.mpq_handle, data, file_name, sfmpq_flags, sfmpq_compression, compression_level):
			raise PyMSError('MPQ', "Error adding data to file '%s' (%d)" % (file_name, _SFmpq.SFGetLastError()))

	def rename_file(self, file_name, new_file_name, locale=MPQLocale.neutral): # type: (str, str, int) -> None
		self._check_open_status(editing=True)
		_SFmpq.SFileSetLocale(locale)

		if not _SFmpq.MpqRenameFile(self.mpq_handle, file_name, new_file_name):
			raise PyMSError('MPQ', "Error renaming file '%s' to '%s' (%d)" % (file_name, new_file_name, _SFmpq.SFGetLastError()))

	def change_file_locale(self, file_name, locale, new_locale): # type: (str, int, int) -> None
		self._check_open_status(editing=True)

		if not _SFmpq.MpqSetFileLocale(self.mpq_handle, file_name, locale, new_locale):
			raise PyMSError('MPQ', "Error setting locale of file '%s' with locale %d to locale %d (%d)" % (file_name, locale, new_locale, _SFmpq.SFGetLastError()))

	def delete_file(self, file_name, locale=MPQLocale.neutral): # type: (str, int) -> None
		self._check_open_status(editing=True)

		if not _SFmpq.MpqDeleteFileWithLocale(self.mpq_handle, file_name, locale):
			raise PyMSError('MPQ', "Error deleting file '%s' (%d)" % (file_name, _SFmpq.SFGetLastError()))

	def compact(self):
		self._check_open_status(editing=True)

		if not _SFmpq.MpqCompactArchive(self.mpq_handle):
			raise PyMSError('MPQ', "Error compacting MPQ (%d)" % _SFmpq.SFGetLastError())

	def flush(self):
		if not self.is_open() or self.is_read_only():
			return
		self.close()
		self.open(read_only=False)
