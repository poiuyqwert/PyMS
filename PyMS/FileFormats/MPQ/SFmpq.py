
import ctypes, os, sys

SFMPQ_DIR = None
if hasattr(sys, 'frozen'):
	SFMPQ_DIR = os.path.join(os.path.dirname(sys.executable) ,'PyMS','FileFormats','MPQ')
else:
	SFMPQ_DIR = os.path.dirname(__file__)

_SFmpq = None
if SFMPQ_DIR:
	libraries = (
		'SFmpq.dll',
		'SFmpq64.dll',
		'SFmpq.dylib',
	)
	for library in libraries:
		if hasattr(ctypes, 'WinDLL'):
			try:
				_SFmpq = ctypes.WinDLL(os.path.join(SFMPQ_DIR, library), ctypes.RTLD_GLOBAL)
				break
			except:
				pass
		try:
			_SFmpq = ctypes.CDLL(os.path.join(SFMPQ_DIR, library), ctypes.RTLD_GLOBAL)
			break
		except:
			pass

SFMPQ_LOADED = (_SFmpq is not None)

MPQ_ERROR_MPQ_INVALID     = 0x85200065
MPQ_ERROR_FILE_NOT_FOUND  = 0x85200066
MPQ_ERROR_DISK_FULL       = 0x85200068 #Physical write file to MPQ failed
MPQ_ERROR_HASH_TABLE_FULL = 0x85200069
MPQ_ERROR_ALREADY_EXISTS  = 0x8520006A
MPQ_ERROR_BAD_OPEN_MODE   = 0x8520006C #When MOAU_READ_ONLY is used without MOAU_OPEN_EXISTING

MPQ_ERROR_COMPACT_ERROR = 0x85300001

# MpqOpenArchiveForUpdate flags
MOAU_CREATE_NEW          = 0x00 #If archive does not exist,                                            it will be created. If it exists,        the function will fail
MOAU_CREATE_ALWAYS       = 0x08 #Will always create a new archive
MOAU_OPEN_EXISTING       = 0x04 #If archive exists,                                                    it will be opened. If it does not exist, the function will fail
MOAU_OPEN_ALWAYS         = 0x20 #If archive exists,                                                    it will be opened. If it does not exist, it will be created
MOAU_READ_ONLY           = 0x10 #Must be used with MOAU_OPEN_EXISTING. Archive will be opened without write access
MOAU_MAINTAIN_ATTRIBUTES = 0x02 #Will be used in a future version to create the (attributes) file
MOAU_MAINTAIN_LISTFILE   = 0x01 #Creates and maintains a list of files in archive when they are added, replaced,                                or deleted

# MpqOpenArchiveForUpdateEx constants
DEFAULT_BLOCK_SIZE     = 3 # 512 << number = block size
USE_DEFAULT_BLOCK_SIZE = 0xFFFFFFFF # Use default block size that is defined internally

# MpqAddFileToArchive flags
MAFA_EXISTS           = 0x80000000 #This flag will be added if not present
MAFA_UNKNOWN40000000  = 0x40000000 #Unknown flag
MAFA_MODCRYPTKEY      = 0x00020000 #Used with MAFA_ENCRYPT. Uses an encryption key based on file position and size
MAFA_ENCRYPT          = 0x00010000 #Encrypts the file. The file is still accessible when using this, so the use of this has depreciated
MAFA_COMPRESS         = 0x00000200 #File is to be compressed when added. This is used for most of the compression methods
MAFA_COMPRESS2        = 0x00000100 #File is compressed with standard compression only (was used in Diablo 1)
MAFA_REPLACE_EXISTING = 0x00000001 #If file already exists,                                          it will be replaced

# MpqAddFileToArchiveEx compression flags
MAFA_COMPRESS_STANDARD = 0x08 #Standard PKWare DCL compression
MAFA_COMPRESS_DEFLATE  = 0x02 #ZLib's deflate compression
MAFA_COMPRESS_WAVE     = 0x81 #Standard wave compression
MAFA_COMPRESS_WAVE2    = 0x41 #Unused wave compression

# Flags for individual compression types used for wave compression
MAFA_COMPRESS_WAVECOMP1 = 0x80 #Main compressor for standard wave compression
MAFA_COMPRESS_WAVECOMP2 = 0x40 #Main compressor for unused wave compression
MAFA_COMPRESS_WAVECOMP3 = 0x01 #Secondary compressor for wave compression

# ZLib deflate compression level constants (used with MpqAddFileToArchiveEx and MpqAddFileFromBufferEx)
Z_NO_COMPRESSION      = 0
Z_BEST_SPEED          = 1
Z_BEST_COMPRESSION    = 9
Z_DEFAULT_COMPRESSION = -1 #Default level is 6 with current ZLib version

# MpqAddWaveToArchive quality flags
MAWA_QUALITY_HIGH   = 1 #Higher compression, lower quality
MAWA_QUALITY_MEDIUM = 0 #Medium compression, medium quality
MAWA_QUALITY_LOW    = 2 #Lower compression,  higher quality

# SFileGetFileInfo flags
SFILE_INFO_BLOCK_SIZE      = 0x01 #Block size in MPQ
SFILE_INFO_HASH_TABLE_SIZE = 0x02 #Hash table size in MPQ
SFILE_INFO_NUM_FILES       = 0x03 #Number of files in MPQ
SFILE_INFO_TYPE            = 0x04 #Is MPQHANDLE a file or an MPQ?
SFILE_INFO_SIZE            = 0x05 #Size of MPQ or uncompressed file
SFILE_INFO_COMPRESSED_SIZE = 0x06 #Size of compressed file
SFILE_INFO_FLAGS           = 0x07 #File flags (compressed, etc.), file attributes if a file not in an archive
SFILE_INFO_PARENT          = 0x08 #Handle of MPQ that file is in
SFILE_INFO_POSITION        = 0x09 #Position of file pointer in files
SFILE_INFO_LOCALEID        = 0x0A #Locale ID of file in MPQ
SFILE_INFO_PRIORITY        = 0x0B #Priority of open MPQ
SFILE_INFO_HASH_INDEX      = 0x0C #Hash table index of file in MPQ
SFILE_INFO_BLOCK_INDEX     = 0x0D #Block table index of file in MPQ

# Return values of SFileGetFileInfo when SFILE_INFO_TYPE flag is used
SFILE_TYPE_MPQ  = 0x01
SFILE_TYPE_FILE = 0x02

# SFileListFiles flags
SFILE_LIST_MEMORY_LIST  = 0x01 # Specifies that lpFilelists is a file list from memory, rather than being a list of file lists
SFILE_LIST_ONLY_KNOWN   = 0x02 # Only list files that the function finds a name for
SFILE_LIST_ONLY_UNKNOWN = 0x04 # Only list files that the function does not find a name for

# SFileOpenArchive flags
SFILE_OPEN_HARD_DISK_FILE = 0x0000 #Open archive without regard to the drive type it resides on
SFILE_OPEN_CD_ROM_FILE    = 0x0001 #Open the archive only if it is on a CD-ROM
SFILE_OPEN_ALLOW_WRITE    = 0x8000 #Open file with write access

# SFileOpenFileEx search scopes
SFILE_SEARCH_CURRENT_ONLY = 0x00 #Used with SFileOpenFileEx; only the archive with the handle specified will be searched for the file
SFILE_SEARCH_ALL_OPEN     = 0x01 #SFileOpenFileEx will look through all open archives for the file. This flag also allows files outside the archive to be used

class SFMPQVERSION(ctypes.Structure):
	_fields_ = [
		('Major',ctypes.c_uint16),
		('Minor',ctypes.c_uint16),
		('Revision',ctypes.c_uint16),
		('Subrevision',ctypes.c_uint16)
	]

class FILELISTENTRY(ctypes.Structure):
	_fields_ = [
		('fileExists',ctypes.c_uint32),
		('locale',ctypes.c_uint32),
		('compressedSize',ctypes.c_uint32),
		('fullSize',ctypes.c_uint32),
		('flags',ctypes.c_uint32),
		('fileName',ctypes.c_char * 260)
	]

	def __init__(self):
		self.fileExists = 0
		self.locale = 0
		self.compressedSize = 0
		self.fullSize = 0
		self.flags = 0
		self.fileName =''

	def get_compression_ratio(self):
		if self.fullSize:
			return self.compressedSize / float(self.fullSize)
		return 0

	def __getitem__(self, k):
		return [self.fileExists,self.locale,self.compressedSize,self.get_compression_ratio(),self.fullSize,self.flags,self.fileName][k]

	def __str__(self):
		return str([self.fileExists,self.locale,self.compressedSize,self.get_compression_ratio(),self.fullSize,self.flags,self.fileName])

	def __eq__(self, other):
		if not isinstance(other, FILELISTENTRY):
			return
		return self.fileName == other.fileName and self.locale == other.locale

class MPQHEADER(ctypes.Structure):
	_fields_ = [
		('mpqId',ctypes.c_int),
		('headerSize',ctypes.c_int),
		('mpqSize',ctypes.c_int),
		('unused',ctypes.c_short),
		('blockSize',ctypes.c_short),
		('hashTableOffset',ctypes.c_int),
		('blockTableOffset',ctypes.c_int),
		('hashTableSize',ctypes.c_int),
		('blockTableSize',ctypes.c_int),
	]

class BLOCKTABLEENTRY(ctypes.Structure):
	_fields_ = [
		('fileOffset',ctypes.c_int),
		('compressedSize',ctypes.c_int),
		('fullSize',ctypes.c_int),
		('flags',ctypes.c_int),
	]

class HASHTABLEENTRY(ctypes.Structure):
	_fields_ = [
		('nameHashA',ctypes.c_int),
		('nameHashB',ctypes.c_int),
		('locale',ctypes.c_int),
		('blockTableIndex',ctypes.c_int),
	]

class MPQFILE(ctypes.Structure):
	pass

class MPQARCHIVE(ctypes.Structure):
	pass

MPQFILE._fields_ = [
	('nextFile',ctypes.POINTER(MPQFILE)),
	('prevFile',ctypes.POINTER(MPQFILE)),
	('fileName',ctypes.c_char * 260),
	('file',ctypes.c_int),
	('parentArc',ctypes.POINTER(MPQARCHIVE)),
	('blockEntry',ctypes.POINTER(BLOCKTABLEENTRY)),
	('cryptKey',ctypes.c_int),
	('filePointer',ctypes.c_int),
	('unknown',ctypes.c_int),
	('blockCount',ctypes.c_int),
	('blockOffsets',ctypes.POINTER(ctypes.c_int)),
	('readStarted',ctypes.c_int),
	('streaming',ctypes.c_byte),
	('lastReadBlock',ctypes.POINTER(ctypes.c_byte)),
	('bytesRead',ctypes.c_int),
	('bufferSize',ctypes.c_int),
	('refCount',ctypes.c_int),
	('hashEntry',ctypes.POINTER(HASHTABLEENTRY)),
	('fileName',ctypes.c_char_p),
]
MPQARCHIVE._fields_ = [
	('nextArc',ctypes.POINTER(MPQARCHIVE)),
	('prevArc',ctypes.POINTER(MPQARCHIVE)),
	('fileName',ctypes.c_char * 260),
	('hFile',ctypes.c_int),
	('flags',ctypes.c_int),
	('priority',ctypes.c_int),
	('lastReadFile',ctypes.POINTER(MPQFILE)),
	('bufferSize',ctypes.c_int),
	('mpqStart',ctypes.c_int),
	('mpqEnd',ctypes.c_int),
	('mpqHeader',ctypes.POINTER(MPQHEADER)),
	('blockTable',ctypes.POINTER(BLOCKTABLEENTRY)),
	('hashTable',ctypes.POINTER(HASHTABLEENTRY)),
	('readOffset',ctypes.c_int),
	('refCount',ctypes.c_int),
	('sfMpqHeader',MPQHEADER),
	('sfFlags',ctypes.c_int),
	('sfFileName',ctypes.c_char_p),
	('sfExtraFlags',ctypes.c_int),
]

class MPQHANDLE(ctypes.c_void_p):
	def __repr__(self):
		return '<MPQHANDLE object at %s: %s>' % (hex(id(self)), hex(self.value))

if _SFmpq is not None:
	try:
		_SFmpq.GetLastError.restype = ctypes.c_int32
	except:
		_SFmpq.GetLastError = None

	_SFmpq.MpqGetVersionString.restype = ctypes.c_char_p
	_SFmpq.MpqGetVersion.restype = ctypes.c_float
	_SFmpq.SFMpqGetVersionString.restype = ctypes.c_char_p
	# _SFmpq.SFMpqGetVersionString2.argtypes = [ctypes.c_char_p,ctypes.c_int]
	_SFmpq.SFMpqGetVersion.restype = SFMPQVERSION
	
	_SFmpq.SFileOpenArchive.argtypes = [ctypes.c_char_p,ctypes.c_int32,ctypes.c_uint32,ctypes.POINTER(MPQHANDLE)]
	_SFmpq.SFileCloseArchive.argtypes = [MPQHANDLE]
	#_SFmpq.SFileOpenFileAsArchive.argtypes = [MPQHANDLE,ctypes.c_char_p,ctypes.c_int32,ctypes.c_int32,ctypes.POINTER(MPQHANDLE)]
	# _SFmpq.SFileGetArchiveName.argtypes = [MPQHANDLE,ctypes.c_char_p,ctypes.c_int32]
	_SFmpq.SFileOpenFile.argtypes = [ctypes.c_char_p,ctypes.POINTER(MPQHANDLE)]
	_SFmpq.SFileOpenFileEx.argtypes = [MPQHANDLE,ctypes.c_char_p,ctypes.c_uint32,ctypes.POINTER(MPQHANDLE)]
	_SFmpq.SFileCloseFile.argtypes = [MPQHANDLE]
	_SFmpq.SFileGetFileSize.argtypes = [MPQHANDLE,ctypes.POINTER(ctypes.c_uint32)]
	_SFmpq.SFileGetFileSize.restype = ctypes.c_uint32
	_SFmpq.SFileGetFileArchive.argtypes = [MPQHANDLE,ctypes.POINTER(MPQHANDLE)]
	# _SFmpq.SFileGetFileName.argtypes = [MPQHANDLE,ctypes.c_char_p,ctypes.c_uint32]
	_SFmpq.SFileSetFilePointer.argtypes = [MPQHANDLE,ctypes.c_int32,ctypes.POINTER(ctypes.c_int32),ctypes.c_uint32]
	_SFmpq.SFileReadFile.argtypes = [MPQHANDLE,ctypes.c_void_p,ctypes.c_uint32,ctypes.POINTER(ctypes.c_uint32),ctypes.c_void_p]
	_SFmpq.SFileSetLocale.argtypes = [ctypes.c_uint32]
	_SFmpq.SFileSetLocale.restype = ctypes.c_uint32
	_SFmpq.SFileGetBasePath.argtypes = [ctypes.c_char_p,ctypes.c_uint32]
	_SFmpq.SFileSetBasePath.argtypes = [ctypes.c_char_p]

	_SFmpq.SFileGetFileInfo.argtypes = [MPQHANDLE,ctypes.c_uint32]
	_SFmpq.SFileGetFileInfo.restype = ctypes.c_size_t
	_SFmpq.SFileSetArchivePriority.argtypes = [MPQHANDLE,ctypes.c_uint32]
	_SFmpq.SFileFindMpqHeader.argtypes = [ctypes.c_void_p]
	_SFmpq.SFileFindMpqHeader.restype = ctypes.c_uint32
	_SFmpq.SFileListFiles.argtypes = [MPQHANDLE,ctypes.c_char_p,ctypes.POINTER(FILELISTENTRY),ctypes.c_uint32]

	_SFmpq.MpqOpenArchiveForUpdate.argtypes = [ctypes.c_char_p,ctypes.c_uint32,ctypes.c_uint32]
	_SFmpq.MpqOpenArchiveForUpdate.restype = MPQHANDLE
	_SFmpq.MpqCloseUpdatedArchive.argtypes = [MPQHANDLE,ctypes.c_uint32]
	_SFmpq.MpqCloseUpdatedArchive.restype = ctypes.c_uint32
	_SFmpq.MpqAddFileToArchive.argtypes = [MPQHANDLE,ctypes.c_char_p,ctypes.c_char_p,ctypes.c_uint32]
	_SFmpq.MpqAddWaveToArchive.argtypes = [MPQHANDLE,ctypes.c_char_p,ctypes.c_char_p,ctypes.c_uint32,ctypes.c_uint32]
	_SFmpq.MpqRenameFile.argtypes = [MPQHANDLE,ctypes.c_char_p,ctypes.c_char_p]
	_SFmpq.MpqDeleteFile.argtypes = [MPQHANDLE,ctypes.c_char_p,ctypes.c_char_p]
	_SFmpq.MpqCompactArchive.argtypes = [MPQHANDLE]

	_SFmpq.MpqOpenArchiveForUpdateEx.argtypes = [ctypes.c_char_p,ctypes.c_uint32,ctypes.c_uint32,ctypes.c_uint32]
	_SFmpq.MpqOpenArchiveForUpdateEx.restype = MPQHANDLE
	_SFmpq.MpqAddFileToArchiveEx.argtypes = [MPQHANDLE,ctypes.c_char_p,ctypes.c_char_p,ctypes.c_uint32,ctypes.c_uint32,ctypes.c_uint32]
	_SFmpq.MpqAddFileFromBufferEx.argtypes = [MPQHANDLE,ctypes.c_void_p,ctypes.c_uint32,ctypes.c_char_p,ctypes.c_uint32,ctypes.c_uint32]
	_SFmpq.MpqAddFileFromBuffer.argtypes = [MPQHANDLE,ctypes.c_void_p,ctypes.c_uint32,ctypes.c_char_p,ctypes.c_uint32]
	_SFmpq.MpqAddWaveFromBuffer.argtypes = [MPQHANDLE,ctypes.c_void_p,ctypes.c_uint32,ctypes.c_char_p,ctypes.c_uint32,ctypes.c_uint32]
	_SFmpq.MpqRenameAndSetFileLocale.argtypes = [MPQHANDLE,ctypes.c_char_p,ctypes.c_char_p,ctypes.c_int,ctypes.c_int]
	_SFmpq.MpqDeleteFileWithLocale.argtypes = [MPQHANDLE,ctypes.c_char_p,ctypes.c_uint32]
	_SFmpq.MpqSetFileLocale.argtypes = [MPQHANDLE,ctypes.c_char_p,ctypes.c_uint32,ctypes.c_uint32]

DEBUG = False
def debug_log(func):
	if DEBUG:
		def do_log(*args, **kwargs):
			result = func(*args, **kwargs)
			print(("Func  : %s" % func.__name__))
			print(("Args  : %s" % (args,)))
			print(("kwargs: %s" % kwargs))
			print(("Result: %s" % (result,)))
			return result
		return do_log
	else:
		return func

def _file_name(file_name: str | bytes) -> bytes:
	if isinstance(file_name, str):
		return file_name.encode('utf-8')
	return file_name

@debug_log
def SFGetLastError():
	assert _SFmpq is not None
	# SFmpq only implements its own GetLastError on platforms other than windows
	if _SFmpq.GetLastError is None:
		return ctypes.GetLastError()
	return _SFmpq.GetLastError()

@debug_log
def SFInvalidHandle(h: MPQHANDLE) -> bool:
	return not isinstance(h, MPQHANDLE) or h.value in [None,0,-1]

@debug_log
def MpqGetVersionString() -> str:
	assert _SFmpq is not None
	return _SFmpq.MpqGetVersionString()

@debug_log
def MpqGetVersion() -> float:
	assert _SFmpq is not None
	return _SFmpq.MpqGetVersion()

@debug_log
def SFMpqGetVersionString() -> str:
	assert _SFmpq is not None
	return _SFmpq.SFMpqGetVersionString()

@debug_log
def SFMpqGetVersion() -> SFMPQVERSION:
	assert _SFmpq is not None
	return _SFmpq.SFMpqGetVersion()

@debug_log
def SFileOpenArchive(path: str, priority: int = 0, flags: int = SFILE_OPEN_HARD_DISK_FILE) -> MPQHANDLE | None:
	assert _SFmpq is not None
	f = MPQHANDLE()
	if not _SFmpq.SFileOpenArchive(path.encode('utf-8'), priority, flags, ctypes.byref(f)):
		return None
	return f

@debug_log
def SFileCloseArchive(mpq: MPQHANDLE) -> bool:
	assert _SFmpq is not None
	return _SFmpq.SFileCloseArchive(mpq)

@debug_log
def SFileOpenFileEx(mpq: MPQHANDLE, path: str, search: int = SFILE_SEARCH_CURRENT_ONLY) -> MPQHANDLE | None:
	assert _SFmpq is not None
	f = MPQHANDLE()
	if not _SFmpq.SFileOpenFileEx(mpq if mpq else None, path.encode('utf-8'), search, ctypes.byref(f)):
		return None
	return f

@debug_log
def SFileCloseFile(file: MPQHANDLE) -> bool:
	assert _SFmpq is not None
	return _SFmpq.SFileCloseFile(file)

@debug_log
def SFileGetFileSize(file: MPQHANDLE) -> int | None:
	assert _SFmpq is not None
	size = _SFmpq.SFileGetFileSize(file, None)
	if size == -1:
		return None
	return size

@debug_log
def SFileReadFile(file: MPQHANDLE, read: int | None = None) -> tuple[bytes | None, int]:
	assert _SFmpq is not None
	if read is None:
		read = SFileGetFileSize(file)
		if read is None:
			return (None, 0)
	data = ctypes.create_string_buffer(read)
	r = ctypes.c_uint32()
	total_read = 0
	while total_read < read:
		if _SFmpq.SFileReadFile(file, ctypes.byref(data, total_read), read-total_read, ctypes.byref(r), None):
			total_read += r.value
		else:
			return (None, 0)
	return (data.raw[:total_read],total_read)

@debug_log
def SFileSetLocale(locale: int) -> int:
	assert _SFmpq is not None
	return _SFmpq.SFileSetLocale(locale)

@debug_log
def SFileGetFileInfo(mpq: MPQHANDLE, flags: int = SFILE_INFO_BLOCK_SIZE) -> int:
	assert _SFmpq is not None
	return _SFmpq.SFileGetFileInfo(mpq, flags)

# listfiles is either a list of file lists or a file list itself depending on flags, either are seperated by newlines (\n \r or \r\n?)
@debug_log
def SFileListFiles(mpq: MPQHANDLE, listfiles: str = '', flags: int = 0) -> list[FILELISTENTRY]:
	assert _SFmpq is not None
	n = SFileGetFileInfo(mpq, SFILE_INFO_HASH_TABLE_SIZE)
	if n < 1:
		return []
	f = (FILELISTENTRY * n)()
	_SFmpq.SFileListFiles(mpq, listfiles.encode('utf-8'), f, flags)
	return [e for e in f if e.fileExists]

@debug_log
def SFileSetArchivePriority(mpq: MPQHANDLE, priority: int) -> bool:
	assert _SFmpq is not None
	return _SFmpq.SFileSetArchivePriority(mpq, priority)

@debug_log
def MpqOpenArchiveForUpdate(path: str, flags: int = MOAU_OPEN_ALWAYS, maxfiles: int = 1024) -> MPQHANDLE:
	assert _SFmpq is not None
	return _SFmpq.MpqOpenArchiveForUpdate(path.encode('utf-8'), flags, maxfiles)

@debug_log
def MpqCloseUpdatedArchive(handle: MPQHANDLE) -> bool:
	assert _SFmpq is not None
	return _SFmpq.MpqCloseUpdatedArchive(handle, 0)

@debug_log
def MpqAddFileToArchive(mpq: MPQHANDLE, source: str, dest: str | bytes, flags: int = MAFA_REPLACE_EXISTING) -> bool:
	assert _SFmpq is not None
	return _SFmpq.MpqAddFileToArchive(mpq, source.encode('utf-8'), _file_name(dest), flags)

@debug_log
def MpqAddFileFromBufferEx(mpq: MPQHANDLE, buffer: bytes, file: str | bytes, flags: int = MAFA_REPLACE_EXISTING, comptype: int = 0, complevel: int = 0) -> bool:
	assert _SFmpq is not None
	return _SFmpq.MpqAddFileFromBufferEx(mpq, buffer, len(buffer), _file_name(file), flags, comptype, complevel)

@debug_log
def MpqAddFileFromBuffer(mpq: MPQHANDLE, buffer: bytes, file: str | bytes, flags: int = MAFA_REPLACE_EXISTING) -> bool:
	assert _SFmpq is not None
	return _SFmpq.MpqAddFileFromBuffer(mpq, buffer, len(buffer), _file_name(file), flags)

@debug_log
def MpqRenameFile(mpq: MPQHANDLE, file_name: str | bytes, new_file_name: str | bytes) -> bool:
	assert _SFmpq is not None
	return _SFmpq.MpqRenameFile(mpq, _file_name(file_name), _file_name(new_file_name))

@debug_log
def MpqCompactArchive(mpq: MPQHANDLE) -> bool:
	assert _SFmpq is not None
	return _SFmpq.MpqCompactArchive(mpq)

@debug_log
def MpqOpenArchiveForUpdateEx(mpq_path: str, flags: int = MOAU_OPEN_ALWAYS, maxfiles: int = 1024, blocksize: int = 3) -> MPQHANDLE:
	assert _SFmpq is not None
	return _SFmpq.MpqOpenArchiveForUpdateEx(mpq_path.encode('utf-8'), flags, maxfiles, blocksize)

@debug_log
def MpqAddFileToArchiveEx(mpq: MPQHANDLE, source: str, dest: str | bytes, flags: int = MAFA_REPLACE_EXISTING, comptype: int = 0, complevel: int = 0) -> bool:
	assert _SFmpq is not None
	return _SFmpq.MpqAddFileToArchiveEx(mpq, source.encode('utf-8'), _file_name(dest), flags, comptype, complevel)

@debug_log
def MpqRenameAndSetFileLocale(mpq: MPQHANDLE, oldname: str | bytes, newname: str | bytes, oldlocale: int, newlocale: int) -> bool:
	assert _SFmpq is not None
	return _SFmpq.MpqRenameAndSetFileLocale(mpq, _file_name(oldname), _file_name(newname), oldlocale, newlocale)

@debug_log
def MpqDeleteFileWithLocale(mpq: MPQHANDLE, file: str | bytes, locale: int) -> bool:
	assert _SFmpq is not None
	return _SFmpq.MpqDeleteFileWithLocale(mpq, _file_name(file), locale)

@debug_log
def MpqSetFileLocale(mpq: MPQHANDLE, file: str | bytes, oldlocale: int, newlocale: int) -> bool:
	assert _SFmpq is not None
	return _SFmpq.MpqSetFileLocale(mpq, _file_name(file), oldlocale, newlocale)
