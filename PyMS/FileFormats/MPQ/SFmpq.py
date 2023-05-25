
from ctypes import *
import os,sys

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
		try:
			_SFmpq = WinDLL(os.path.join(SFMPQ_DIR, library), RTLD_GLOBAL)
			break
		except Exception:
			pass
		try:
			_SFmpq = CDLL(os.path.join(SFMPQ_DIR, library), RTLD_GLOBAL)
			break
		except Exception:
			pass

SFMPQ_LOADED = (_SFmpq != None)

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

class SFMPQVERSION(Structure):
	_fields_ = [
		('Major',c_uint16),
		('Minor',c_uint16),
		('Revision',c_uint16),
		('Subrevision',c_uint16)
	]

class FILELISTENTRY(Structure):
	_fields_ = [
		('fileExists',c_uint32),
		('locale',c_uint32),
		('compressedSize',c_uint32),
		('fullSize',c_uint32),
		('flags',c_uint32),
		('fileName',c_char * 260)
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

class MPQHEADER(Structure):
	_fields_ = [
		('mpqId',c_int),
		('headerSize',c_int),
		('mpqSize',c_int),
		('unused',c_short),
		('blockSize',c_short),
		('hashTableOffset',c_int),
		('blockTableOffset',c_int),
		('hashTableSize',c_int),
		('blockTableSize',c_int),
	]

class BLOCKTABLEENTRY(Structure):
	_fields_ = [
		('fileOffset',c_int),
		('compressedSize',c_int),
		('fullSize',c_int),
		('flags',c_int),
	]

class HASHTABLEENTRY(Structure):
	_fields_ = [
		('nameHashA',c_int),
		('nameHashB',c_int),
		('locale',c_int),
		('blockTableIndex',c_int),
	]

class MPQFILE(Structure):
	pass

class MPQARCHIVE(Structure):
	pass

MPQFILE._fields_ = [
	('nextFile',POINTER(MPQFILE)),
	('prevFile',POINTER(MPQFILE)),
	('fileName',c_char * 260),
	('file',c_int),
	('parentArc',POINTER(MPQARCHIVE)),
	('blockEntry',POINTER(BLOCKTABLEENTRY)),
	('cryptKey',c_int),
	('filePointer',c_int),
	('unknown',c_int),
	('blockCount',c_int),
	('blockOffsets',POINTER(c_int)),
	('readStarted',c_int),
	('streaming',c_byte),
	('lastReadBlock',POINTER(c_byte)),
	('bytesRead',c_int),
	('bufferSize',c_int),
	('refCount',c_int),
	('hashEntry',POINTER(HASHTABLEENTRY)),
	('fileName',c_char_p),
]
MPQARCHIVE._fields_ = [
	('nextArc',POINTER(MPQARCHIVE)),
	('prevArc',POINTER(MPQARCHIVE)),
	('fileName',c_char * 260),
	('hFile',c_int),
	('flags',c_int),
	('priority',c_int),
	('lastReadFile',POINTER(MPQFILE)),
	('bufferSize',c_int),
	('mpqStart',c_int),
	('mpqEnd',c_int),
	('mpqHeader',POINTER(MPQHEADER)),
	('blockTable',POINTER(BLOCKTABLEENTRY)),
	('hashTable',POINTER(HASHTABLEENTRY)),
	('readOffset',c_int),
	('refCount',c_int),
	('sfMpqHeader',MPQHEADER),
	('sfFlags',c_int),
	('sfFileName',c_char_p),
	('sfExtraFlags',c_int),
]

class MPQHANDLE(c_void_p):
	def __repr__(self):
		return '<MPQHANDLE object at %s: %s>' % (hex(id(self)), hex(self.value))

if SFMPQ_LOADED:
	try:
		_SFmpq.GetLastError.restype = c_int32
	except:
		_SFmpq.GetLastError = None

	_SFmpq.MpqGetVersionString.restype = c_char_p
	_SFmpq.MpqGetVersion.restype = c_float
	_SFmpq.SFMpqGetVersionString.restype = c_char_p
	# _SFmpq.SFMpqGetVersionString2.argtypes = [c_char_p,c_int]
	_SFmpq.SFMpqGetVersion.restype = SFMPQVERSION
	
	_SFmpq.SFileOpenArchive.argtypes = [c_char_p,c_int32,c_uint32,POINTER(MPQHANDLE)]
	_SFmpq.SFileCloseArchive.argtypes = [MPQHANDLE]
	#_SFmpq.SFileOpenFileAsArchive.argtypes = [MPQHANDLE,c_char_p,c_int32,c_int32,POINTER(MPQHANDLE)]
	# _SFmpq.SFileGetArchiveName.argtypes = [MPQHANDLE,c_char_p,c_int32]
	_SFmpq.SFileOpenFile.argtypes = [c_char_p,POINTER(MPQHANDLE)]
	_SFmpq.SFileOpenFileEx.argtypes = [MPQHANDLE,c_char_p,c_uint32,POINTER(MPQHANDLE)]
	_SFmpq.SFileCloseFile.argtypes = [MPQHANDLE]
	_SFmpq.SFileGetFileSize.argtypes = [MPQHANDLE,POINTER(c_uint32)]
	_SFmpq.SFileGetFileSize.restype = c_uint32
	_SFmpq.SFileGetFileArchive.argtypes = [MPQHANDLE,POINTER(MPQHANDLE)]
	# _SFmpq.SFileGetFileName.argtypes = [MPQHANDLE,c_char_p,c_uint32]
	_SFmpq.SFileSetFilePointer.argtypes = [MPQHANDLE,c_int32,POINTER(c_int32),c_uint32]
	_SFmpq.SFileReadFile.argtypes = [MPQHANDLE,c_void_p,c_uint32,POINTER(c_uint32),c_void_p]
	_SFmpq.SFileSetLocale.argtypes = [c_uint32]
	_SFmpq.SFileSetLocale.restype = c_uint32
	_SFmpq.SFileGetBasePath.argtypes = [c_char_p,c_uint32]
	_SFmpq.SFileSetBasePath.argtypes = [c_char_p]

	_SFmpq.SFileGetFileInfo.argtypes = [MPQHANDLE,c_uint32]
	_SFmpq.SFileGetFileInfo.restype = c_size_t
	_SFmpq.SFileSetArchivePriority.argtypes = [MPQHANDLE,c_uint32]
	_SFmpq.SFileFindMpqHeader.argtypes = [c_void_p]
	_SFmpq.SFileFindMpqHeader.restype = c_uint32
	_SFmpq.SFileListFiles.argtypes = [MPQHANDLE,c_char_p,POINTER(FILELISTENTRY),c_uint32]

	_SFmpq.MpqOpenArchiveForUpdate.argtypes = [c_char_p,c_uint32,c_uint32]
	_SFmpq.MpqOpenArchiveForUpdate.restype = MPQHANDLE
	_SFmpq.MpqCloseUpdatedArchive.argtypes = [MPQHANDLE,c_uint32]
	_SFmpq.MpqCloseUpdatedArchive.restype = c_uint32
	_SFmpq.MpqAddFileToArchive.argtypes = [MPQHANDLE,c_char_p,c_char_p,c_uint32]
	_SFmpq.MpqAddWaveToArchive.argtypes = [MPQHANDLE,c_char_p,c_char_p,c_uint32,c_uint32]
	_SFmpq.MpqRenameFile.argtypes = [MPQHANDLE,c_char_p,c_char_p]
	_SFmpq.MpqDeleteFile.argtypes = [MPQHANDLE,c_char_p,c_char_p]
	_SFmpq.MpqCompactArchive.argtypes = [MPQHANDLE]

	_SFmpq.MpqOpenArchiveForUpdateEx.argtypes = [c_char_p,c_uint32,c_uint32,c_uint32]
	_SFmpq.MpqOpenArchiveForUpdateEx.restype = MPQHANDLE
	_SFmpq.MpqAddFileToArchiveEx.argtypes = [MPQHANDLE,c_char_p,c_char_p,c_uint32,c_uint32,c_uint32]
	_SFmpq.MpqAddFileFromBufferEx.argtypes = [MPQHANDLE,c_void_p,c_uint32,c_char_p,c_uint32,c_uint32]
	_SFmpq.MpqAddFileFromBuffer.argtypes = [MPQHANDLE,c_void_p,c_uint32,c_char_p,c_uint32]
	_SFmpq.MpqAddWaveFromBuffer.argtypes = [MPQHANDLE,c_void_p,c_uint32,c_char_p,c_uint32,c_uint32]
	_SFmpq.MpqRenameAndSetFileLocale.argtypes = [MPQHANDLE,c_char_p,c_char_p,c_int,c_int]
	_SFmpq.MpqDeleteFileWithLocale.argtypes = [MPQHANDLE,c_char_p,c_uint32]
	_SFmpq.MpqSetFileLocale.argtypes = [MPQHANDLE,c_char_p,c_uint32,c_uint32]

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

@debug_log
def SFGetLastError():
	# SFmpq only implements its own GetLastError on platforms other than windows
	if _SFmpq.GetLastError == None:
		return GetLastError()
	return _SFmpq.GetLastError()

@debug_log
def SFInvalidHandle(h): # type: (MPQHANDLE) -> bool
	return not isinstance(h, MPQHANDLE) or h.value in [None,0,-1]

@debug_log
def MpqGetVersionString(): # type: () -> str
	return _SFmpq.MpqGetVersionString()

@debug_log
def MpqGetVersion(): # type: () -> float
	return _SFmpq.MpqGetVersion()

@debug_log
def SFMpqGetVersionString(): # type: () -> str
	return _SFmpq.SFMpqGetVersionString()

@debug_log
def SFMpqGetVersion(): # type: () -> SFMPQVERSION
	return _SFmpq.SFMpqGetVersion()

@debug_log
def SFileOpenArchive(path, priority=0, flags=SFILE_OPEN_HARD_DISK_FILE): # type: (str, int, int) -> (MPQHANDLE | None)
	f = MPQHANDLE()
	if _SFmpq.SFileOpenArchive(path, priority, flags, byref(f)):
		return f

@debug_log
def SFileCloseArchive(mpq): # type: (MPQHANDLE) -> bool
	return _SFmpq.SFileCloseArchive(mpq)

@debug_log
def SFileOpenFileEx(mpq, path, search=SFILE_SEARCH_CURRENT_ONLY): # type: (MPQHANDLE, str, int) -> (MPQHANDLE | None)
	f = MPQHANDLE()
	if _SFmpq.SFileOpenFileEx(mpq if mpq else None, path, search, byref(f)):
		return f

@debug_log
def SFileCloseFile(file): # type: (MPQHANDLE) -> bool
	return _SFmpq.SFileCloseFile(file)

@debug_log
def SFileGetFileSize(file): # type: (MPQHANDLE) -> int
	return _SFmpq.SFileGetFileSize(file, None)

@debug_log
def SFileReadFile(file, read=None): # type: (MPQHANDLE, int) -> tuple[bytes | None, int]
	all = read == None
	if all:
		read = SFileGetFileSize(file)
		if read == -1:
			return (None, 0)
	data = create_string_buffer(read)
	r = c_uint32()
	total_read = 0
	while total_read < read:
		if _SFmpq.SFileReadFile(file, byref(data, total_read), read-total_read, byref(r), None):
			total_read += r.value
		else:
			return (None, 0)
	return (data.raw[:total_read],total_read)

@debug_log
def SFileSetLocale(locale): # type: (int) -> int
	return _SFmpq.SFileSetLocale(locale)

@debug_log
def SFileGetFileInfo(mpq, flags=SFILE_INFO_BLOCK_SIZE): # type: (MPQHANDLE, int) -> int
	return _SFmpq.SFileGetFileInfo(mpq, flags)

# listfiles is either a list of file lists or a file list itself depending on flags, either are seperated by newlines (\n \r or \r\n?)
@debug_log
def SFileListFiles(mpq, listfiles='', flags=0): # type: (MPQHANDLE, str, int) -> list[FILELISTENTRY]
	n = SFileGetFileInfo(mpq, SFILE_INFO_HASH_TABLE_SIZE)
	if n < 1:
		return []
	f = (FILELISTENTRY * n)()
	_SFmpq.SFileListFiles(mpq, listfiles, f, flags)
	return [e for e in f if e.fileExists]

@debug_log
def SFileSetArchivePriority(mpq, priority): # type: (MPQHANDLE, int) -> bool
	return _SFmpq.SFileSetArchivePriority(mpq, priority)

@debug_log
def MpqOpenArchiveForUpdate(path, flags=MOAU_OPEN_ALWAYS, maxfiles=1024): # type: (str, int, int) -> (MPQHANDLE)
	return _SFmpq.MpqOpenArchiveForUpdate(path, flags, maxfiles)

@debug_log
def MpqCloseUpdatedArchive(handle): # type: (MPQHANDLE) -> bool
	return _SFmpq.MpqCloseUpdatedArchive(handle, 0)

@debug_log
def MpqAddFileToArchive(mpq, source, dest, flags=MAFA_REPLACE_EXISTING): # type: (MPQHANDLE, str, str, int) -> bool
	return _SFmpq.MpqAddFileToArchive(mpq, source, dest, flags)

@debug_log
def MpqAddFileFromBufferEx(mpq, buffer, file, flags=MAFA_REPLACE_EXISTING, comptype=0, complevel=0): # type: (MPQHANDLE, bytes, str, int, int, int) -> bool
	return _SFmpq.MpqAddFileFromBufferEx(mpq, buffer, len(buffer), file, flags, comptype, complevel)

@debug_log
def MpqAddFileFromBuffer(mpq, buffer, file, flags=MAFA_REPLACE_EXISTING): # type: (MPQHANDLE, bytes, str, int) -> bool
	return _SFmpq.MpqAddFileFromBuffer(mpq, buffer, len(buffer), file, flags)

@debug_log
def MpqRenameFile(mpq, file_name, new_file_name): # type: (MPQHANDLE, str, str) -> bool
	return _SFmpq.MpqRenameFile(mpq, file_name, new_file_name)

@debug_log
def MpqCompactArchive(mpq): # type: (MPQHANDLE) -> bool
	return _SFmpq.MpqCompactArchive(mpq)

@debug_log
def MpqOpenArchiveForUpdateEx(mpq, flags=MOAU_OPEN_ALWAYS, maxfiles=1024, blocksize=3): # type: (str, int, int, int) -> MPQHANDLE
	return _SFmpq.MpqOpenArchiveForUpdateEx(mpq, flags, maxfiles, blocksize)

@debug_log
def MpqAddFileToArchiveEx(mpq, source, dest, flags=MAFA_REPLACE_EXISTING, comptype=0, complevel=0): # type: (MPQHANDLE, str, str, int, int, int) -> bool
	return _SFmpq.MpqAddFileToArchiveEx(mpq, source, dest, flags, comptype, complevel)

@debug_log
def MpqRenameAndSetFileLocale(mpq, oldname, newname, oldlocale, newlocale): # type: (MPQHANDLE, str, str, int, int) -> bool
	return _SFmpq.MpqRenameAndSetFileLocale(mpq, oldname, newname, oldlocale, newlocale)

@debug_log
def MpqDeleteFileWithLocale(mpq, file, locale): # type: (MPQHANDLE, str, int) -> bool
	return _SFmpq.MpqDeleteFileWithLocale(mpq, file, locale)

@debug_log
def MpqSetFileLocale(mpq, file, oldlocale, newlocale): # type: (MPQHANDLE, str, int, int) -> bool
	return _SFmpq.MpqSetFileLocale(mpq, file, oldlocale, newlocale)
