
from ctypes import *
import os,sys

STORMLIB_DIR = None
if hasattr(sys, 'frozen'):
	STORMLIB_DIR = os.path.join(os.path.dirname(sys.executable) ,'PyMS','FileFormats','MPQ')
else:
	STORMLIB_DIR = os.path.dirname(__file__)

_StormLib = None
if STORMLIB_DIR:
	libraries = (
		'StormLib.dll',
		'StormLib64.dll',
		'StormLib.dylib',
	)
	for library in libraries:
		try:
			_StormLib = WinDLL(os.path.join(STORMLIB_DIR, library), RTLD_GLOBAL)
			break
		except Exception:
			pass
		try:
			_StormLib = CDLL(os.path.join(STORMLIB_DIR, library), RTLD_GLOBAL)
			break
		except Exception:
			pass

STORMLIB_LOADED = (_StormLib != None)

ERROR_AVI_FILE               = 10000  # Not a MPQ file, but an AVI file.
ERROR_UNKNOWN_FILE_KEY       = 10001  # Returned by SFileReadFile when can't find file key
ERROR_CHECKSUM_ERROR         = 10002  # Returned by SFileReadFile when sector CRC doesn't match
ERROR_INTERNAL_FILE          = 10003  # The given operation is not allowed on internal file
ERROR_BASE_FILE_MISSING      = 10004  # The file is present as incremental patch file, but base file is missing
ERROR_MARKED_FOR_DELETE      = 10005  # The file was marked as "deleted" in the MPQ
ERROR_FILE_INCOMPLETE        = 10006  # The required file part is missing
ERROR_UNKNOWN_FILE_NAMES     = 10007  # A name of at least one file is unknown
ERROR_CANT_FIND_PATCH_PREFIX = 10008  # StormLib was unable to find patch prefix for the patches
ERROR_FAKE_MPQ_HEADER        = 10009  # The header at this position is fake header

# Values for SFileCreateArchive
HASH_TABLE_SIZE_MIN     = 0x00000004  # Verified: If there is 1 file, hash table size is 4
HASH_TABLE_SIZE_DEFAULT = 0x00001000  # Default hash table size for empty MPQs
HASH_TABLE_SIZE_MAX     = 0x00080000  # Maximum acceptable hash table size

HASH_ENTRY_DELETED = 0xFFFFFFFE  # Block index for deleted entry in the hash table
HASH_ENTRY_FREE    = 0xFFFFFFFF  # Block index for free entry in the hash table

HET_ENTRY_DELETED = 0x80  # NameHash1 value for a deleted entry
HET_ENTRY_FREE    = 0x00  # NameHash1 value for free entry

# Values for SFileOpenArchive
# SFILE_OPEN_HARD_DISK_FILE = 2  # Open the archive on HDD
# SFILE_OPEN_CDROM_FILE     = 3  # Open the archive only if it is on CDROM

# Values for SFileOpenFile
SFILE_OPEN_FROM_MPQ     = 0x00000000  # Open the file from the MPQ archive
SFILE_OPEN_CHECK_EXISTS = 0xFFFFFFFC  # Only check whether the file exists
SFILE_OPEN_BASE_FILE    = 0xFFFFFFFD  # Reserved for StormLib internal use
SFILE_OPEN_ANY_LOCALE   = 0xFFFFFFFE  # Reserved for StormLib internal use
SFILE_OPEN_LOCAL_FILE   = 0xFFFFFFFF  # Open a local file

# Flags for TMPQArchive:: dwFlags. Used internally
# MPQ_FLAG_READ_ONLY        = 0x00000001  # If set, the MPQ has been open for read-only access
# MPQ_FLAG_CHANGED          = 0x00000002  # If set, the MPQ tables have been changed
# MPQ_FLAG_MALFORMED        = 0x00000004  # Malformed data structure detected (W3M map protectors)
# MPQ_FLAG_HASH_TABLE_CUT   = 0x00000008  # The hash table goes beyond EOF
# MPQ_FLAG_BLOCK_TABLE_CUT  = 0x00000010  # The hash table goes beyond EOF
# MPQ_FLAG_CHECK_SECTOR_CRC = 0x00000020  # Checking sector CRC when reading files
# MPQ_FLAG_SAVING_TABLES    = 0x00000040  # If set, we are saving MPQ internal files and MPQ tables
# MPQ_FLAG_PATCH            = 0x00000080  # If set, this MPQ is a patch archive
# MPQ_FLAG_WAR3_MAP         = 0x00000100  # If set, this MPQ is a Warcraft III map
# MPQ_FLAG_STARCRAFT_BETA   = 0x00000200  # If set, this MPQ is StarDat.mpq from Starcraft I BETA
# MPQ_FLAG_LISTFILE_NONE    = 0x00000400  # Set when no (listfile) was found in InvalidateInternalFiles
# MPQ_FLAG_LISTFILE_NEW     = 0x00000800  # Set when (listfile) invalidated by InvalidateInternalFiles
# MPQ_FLAG_LISTFILE_FORCE   = 0x00001000  # Save updated listfile on exit
# MPQ_FLAG_ATTRIBUTES_NONE  = 0x00002000  # Set when no (attributes) was found in InvalidateInternalFiles
# MPQ_FLAG_ATTRIBUTES_NEW   = 0x00004000  # Set when (attributes) invalidated by InvalidateInternalFiles
# MPQ_FLAG_SIGNATURE_NONE   = 0x00008000  # Set when no (signature) was found in InvalidateInternalFiles
# MPQ_FLAG_SIGNATURE_NEW    = 0x00010000  # Set when (signature) invalidated by InvalidateInternalFiles

# Values for TMPQArchive:: dwSubType
MPQ_SUBTYPE_MPQ = 0x00000000  # The file is a MPQ file (Blizzard games)
MPQ_SUBTYPE_SQP = 0x00000001  # The file is a SQP file (War of the Immortals)
MPQ_SUBTYPE_MPK = 0x00000002  # The file is a MPK file (Longwu Online)

# Return value for SFileGetFileSize and SFileSetFilePointer
SFILE_INVALID_SIZE       = 0xFFFFFFFF
SFILE_INVALID_POS        = 0xFFFFFFFF
SFILE_INVALID_ATTRIBUTES = 0xFFFFFFFF

# Flags for SFileAddFile
MPQ_FILE_IMPLODE          = 0x00000100  # Implode method (By PKWARE Data Compression Library)
MPQ_FILE_COMPRESS         = 0x00000200  # Compress methods (By multiple methods)
MPQ_FILE_ENCRYPTED        = 0x00010000  # Indicates whether file is encrypted
MPQ_FILE_FIX_KEY          = 0x00020000  # File decryption key has to be fixed
MPQ_FILE_PATCH_FILE       = 0x00100000  # The file is a patch file. Raw file data begin with TPatchInfo structure
MPQ_FILE_SINGLE_UNIT      = 0x01000000  # File is stored as a single unit,                rather than split into sectors (Thx, Quantam)
MPQ_FILE_DELETE_MARKER    = 0x02000000  # File is a deletion marker. Used in MPQ patches, indicating that the file no longer exists.
MPQ_FILE_SECTOR_CRC       = 0x04000000  # File has checksums for each sector.
                                       # Ignored if file is not compressed or imploded.
MPQ_FILE_SIGNATURE        = 0x10000000  # Present on STANDARD.SNP\(signature). The only occurence ever observed
MPQ_FILE_EXISTS           = 0x80000000  # Set if file exists, reset when the file was deleted
MPQ_FILE_REPLACEEXISTING  = 0x80000000  # Replace when the file exist (SFileAddFile)

MPQ_FILE_COMPRESS_MASK    = 0x0000FF00  # Mask for a file being compressed

MPQ_FILE_DEFAULT_INTERNAL = 0xFFFFFFFF  # Use default flags for internal files

MPQ_FILE_VALID_FLAGS      = (MPQ_FILE_IMPLODE       |  \
                             MPQ_FILE_COMPRESS      |  \
                             MPQ_FILE_ENCRYPTED     |  \
                             MPQ_FILE_FIX_KEY       |  \
                             MPQ_FILE_PATCH_FILE    |  \
                             MPQ_FILE_SINGLE_UNIT   |  \
                             MPQ_FILE_DELETE_MARKER |  \
                             MPQ_FILE_SECTOR_CRC    |  \
                             MPQ_FILE_SIGNATURE     |  \
                             MPQ_FILE_EXISTS)

MPQ_FILE_VALID_FLAGS_W3X  = (MPQ_FILE_IMPLODE       |  \
                             MPQ_FILE_COMPRESS      |  \
                             MPQ_FILE_ENCRYPTED     |  \
                             MPQ_FILE_FIX_KEY       |  \
                             MPQ_FILE_DELETE_MARKER |  \
                             MPQ_FILE_SECTOR_CRC    |  \
                             MPQ_FILE_SIGNATURE     |  \
                             MPQ_FILE_EXISTS)

MPQ_FILE_VALID_FLAGS_SCX  = (MPQ_FILE_IMPLODE       |  \
                             MPQ_FILE_COMPRESS      |  \
                             MPQ_FILE_ENCRYPTED     |  \
                             MPQ_FILE_FIX_KEY       |  \
                             MPQ_FILE_EXISTS)

# We need to mask out the upper 4 bits of the block table index.
# This is because it gets shifted out when calculating block table offset
# BlockTableOffset = pHash->dwBlockIndex << 0x04
# Malformed MPQ maps may contain block indexes like 0x40000001 or 0xF0000023
BLOCK_INDEX_MASK = 0x0FFFFFFF
#define MPQ_BLOCK_INDEX(pHash) ((pHash)->dwBlockIndex & BLOCK_INDEX_MASK)

# Compression types for multiple compressions
MPQ_COMPRESSION_HUFFMANN     = 0x01  # Huffmann compression (used on WAVE files only)
MPQ_COMPRESSION_ZLIB         = 0x02  # ZLIB compression
MPQ_COMPRESSION_PKWARE       = 0x08  # PKWARE DCL compression
MPQ_COMPRESSION_BZIP2        = 0x10  # BZIP2 compression (added in Warcraft III)
MPQ_COMPRESSION_SPARSE       = 0x20  # Sparse compression (added in Starcraft 2)
MPQ_COMPRESSION_ADPCM_MONO   = 0x40  # IMA ADPCM compression (mono)
MPQ_COMPRESSION_ADPCM_STEREO = 0x80  # IMA ADPCM compression (stereo)
MPQ_COMPRESSION_LZMA         = 0x12  # LZMA compression. Added in Starcraft 2. This value is NOT a combination of flags.
MPQ_COMPRESSION_NEXT_SAME    = 0xFFFFFFFF  # Same compression

# Constants for SFileAddWave
MPQ_WAVE_QUALITY_HIGH   = 0  # Best quality,   the worst compression
MPQ_WAVE_QUALITY_MEDIUM = 1  # Medium quality, medium compression
MPQ_WAVE_QUALITY_LOW    = 2  # Low quality,    the best compression

# Signatures for HET and BET table
HET_TABLE_SIGNATURE = 0x1A544548  # 'HET\x1a'
BET_TABLE_SIGNATURE = 0x1A544542  # 'BET\x1a'

# Decryption keys for MPQ tables
MPQ_KEY_HASH_TABLE  = 0xC3AF3770  # Obtained by HashString("(hash table)", MPQ_HASH_FILE_KEY)
MPQ_KEY_BLOCK_TABLE = 0xEC83B3A3  # Obtained by HashString("(block table)", MPQ_HASH_FILE_KEY)

LISTFILE_NAME       = "(listfile)"  # Name of internal listfile
SIGNATURE_NAME      = "(signature)"  # Name of internal signature
ATTRIBUTES_NAME     = "(attributes)"  # Name of internal attributes file
PATCH_METADATA_NAME = "(patch_metadata)"

MPQ_FORMAT_VERSION_1 = 0  # Up to The Burning Crusade
MPQ_FORMAT_VERSION_2 = 1  # The Burning Crusade and newer
MPQ_FORMAT_VERSION_3 = 2  # WoW Cataclysm Beta
MPQ_FORMAT_VERSION_4 = 3  # WoW Cataclysm and newer

# Flags for MPQ attributes
MPQ_ATTRIBUTE_CRC32     = 0x00000001  # The "(attributes)" contains CRC32 for each file
MPQ_ATTRIBUTE_FILETIME  = 0x00000002  # The "(attributes)" contains file time for each file
MPQ_ATTRIBUTE_MD5       = 0x00000004  # The "(attributes)" contains MD5 for each file
MPQ_ATTRIBUTE_PATCH_BIT = 0x00000008  # The "(attributes)" contains a patch bit for each file
MPQ_ATTRIBUTE_ALL       = 0x0000000F  # Summary mask

MPQ_ATTRIBUTES_V1 = 100  # (attributes) format version 1.00

# Flags for SFileOpenArchive
BASE_PROVIDER_FILE = 0x00000000  # Base data source is a file
BASE_PROVIDER_MAP  = 0x00000001  # Base data source is memory-mapped file
BASE_PROVIDER_HTTP = 0x00000002  # Base data source is a file on web server
BASE_PROVIDER_MASK = 0x0000000F  # Mask for base provider value

STREAM_PROVIDER_FLAT    = 0x00000000  # Stream is linear with no offset mapping
STREAM_PROVIDER_PARTIAL = 0x00000010  # Stream is partial file (.part)
STREAM_PROVIDER_MPQE    = 0x00000020  # Stream is an encrypted MPQ
STREAM_PROVIDER_BLOCK4  = 0x00000030  # 0x4000 per block, text MD5 after each block, max 0x2000 blocks per file
STREAM_PROVIDER_MASK    = 0x000000F0  # Mask for stream provider value

STREAM_FLAG_READ_ONLY   = 0x00000100  # Stream is read only
STREAM_FLAG_WRITE_SHARE = 0x00000200  # Allow write sharing when open for write
STREAM_FLAG_USE_BITMAP  = 0x00000400  # If the file has a file bitmap, load it and use it
STREAM_OPTIONS_MASK     = 0x0000FF00  # Mask for stream options

STREAM_PROVIDERS_MASK = 0x000000FF  # Mask to get stream providers
STREAM_FLAGS_MASK     = 0x0000FFFF  # Mask for all stream flags (providers+options)

MPQ_OPEN_NO_LISTFILE      = 0x00010000  # Don't load the internal listfile
MPQ_OPEN_NO_ATTRIBUTES    = 0x00020000  # Don't open the attributes
MPQ_OPEN_NO_HEADER_SEARCH = 0x00040000  # Don't search for the MPQ header past the begin of the file
MPQ_OPEN_FORCE_MPQ_V1     = 0x00080000  # Always open the archive as MPQ v 1.00, ignore the "wFormatVersion" variable in the header
MPQ_OPEN_CHECK_SECTOR_CRC = 0x00100000  # On files with MPQ_FILE_SECTOR_CRC,     the CRC will be checked when reading file
MPQ_OPEN_PATCH            = 0x00200000  # This archive is a patch MPQ. Used internally.
MPQ_OPEN_FORCE_LISTFILE   = 0x00400000  # Force add listfile even if there is none at the moment of opening
MPQ_OPEN_READ_ONLY        = STREAM_FLAG_READ_ONLY

# Flags for SFileCreateArchive
MPQ_CREATE_LISTFILE      = 0x00100000  # Also add the (listfile) file
MPQ_CREATE_ATTRIBUTES    = 0x00200000  # Also add the (attributes) file
MPQ_CREATE_SIGNATURE     = 0x00400000  # Also add the (signature) file
MPQ_CREATE_ARCHIVE_V1    = 0x00000000  # Creates archive of version 1 (size up to 4GB)
MPQ_CREATE_ARCHIVE_V2    = 0x01000000  # Creates archive of version 2 (larger than 4 GB)
MPQ_CREATE_ARCHIVE_V3    = 0x02000000  # Creates archive of version 3
MPQ_CREATE_ARCHIVE_V4    = 0x03000000  # Creates archive of version 4
MPQ_CREATE_ARCHIVE_VMASK = 0x0F000000  # Mask for archive version

FLAGS_TO_FORMAT_SHIFT = 24  # (MPQ_CREATE_ARCHIVE_V4 >> FLAGS_TO_FORMAT_SHIFT) => MPQ_FORMAT_VERSION_4

# Flags for SFileVerifyFile
SFILE_VERIFY_SECTOR_CRC = 0x00000001  # Verify sector checksum for the file, if available
SFILE_VERIFY_FILE_CRC   = 0x00000002  # Verify file CRC,                     if available
SFILE_VERIFY_FILE_MD5   = 0x00000004  # Verify file MD5,                     if available
SFILE_VERIFY_RAW_MD5    = 0x00000008  # Verify raw file MD5,                 if available
SFILE_VERIFY_ALL        = 0x0000000F  # Verify every checksum possible

# Return values for SFileVerifyFile
VERIFY_OPEN_ERROR            = 0x0001  # Failed to open the file
VERIFY_READ_ERROR            = 0x0002  # Failed to read all data from the file
VERIFY_FILE_HAS_SECTOR_CRC   = 0x0004  # File has sector CRC
VERIFY_FILE_SECTOR_CRC_ERROR = 0x0008  # Sector CRC check failed
VERIFY_FILE_HAS_CHECKSUM     = 0x0010  # File has CRC32
VERIFY_FILE_CHECKSUM_ERROR   = 0x0020  # CRC32 check failed
VERIFY_FILE_HAS_MD5          = 0x0040  # File has data MD5
VERIFY_FILE_MD5_ERROR        = 0x0080  # MD5 check failed
VERIFY_FILE_HAS_RAW_MD5      = 0x0100  # File has raw data MD5
VERIFY_FILE_RAW_MD5_ERROR    = 0x0200  # Raw MD5 check failed
VERIFY_FILE_ERROR_MASK       = (VERIFY_OPEN_ERROR | \
								VERIFY_READ_ERROR | \
								VERIFY_FILE_SECTOR_CRC_ERROR | \
								VERIFY_FILE_CHECKSUM_ERROR | \
								VERIFY_FILE_MD5_ERROR | \
								VERIFY_FILE_RAW_MD5_ERROR)

# Flags for SFileVerifyRawData (for MPQs version 4.0 or higher)
SFILE_VERIFY_MPQ_HEADER    = 0x0001  # Verify raw MPQ header
SFILE_VERIFY_HET_TABLE     = 0x0002  # Verify raw data of the HET table
SFILE_VERIFY_BET_TABLE     = 0x0003  # Verify raw data of the BET table
SFILE_VERIFY_HASH_TABLE    = 0x0004  # Verify raw data of the hash table
SFILE_VERIFY_BLOCK_TABLE   = 0x0005  # Verify raw data of the block table
SFILE_VERIFY_HIBLOCK_TABLE = 0x0006  # Verify raw data of the hi-block table
SFILE_VERIFY_FILE          = 0x0007  # Verify raw data of a file

# Signature types
SIGNATURE_TYPE_NONE   = 0x0000  # The archive has no signature in it
SIGNATURE_TYPE_WEAK   = 0x0001  # The archive has weak signature
SIGNATURE_TYPE_STRONG = 0x0002  # The archive has strong signature

# Return values for SFileVerifyArchive
ERROR_NO_SIGNATURE           = 0  # There is no signature in the MPQ
ERROR_VERIFY_FAILED          = 1  # There was an error during verifying signature (like no memory)
ERROR_WEAK_SIGNATURE_OK      = 2  # There is a weak signature and sign check passed
ERROR_WEAK_SIGNATURE_ERROR   = 3  # There is a weak signature but sign check failed
ERROR_STRONG_SIGNATURE_OK    = 4  # There is a strong signature and sign check passed
ERROR_STRONG_SIGNATURE_ERROR = 5  # There is a strong signature but sign check failed

MD5_DIGEST_SIZE = 0x10

SHA1_DIGEST_SIZE = 0x14  # 160 bits

LANG_NEUTRAL = 0x00  # Neutral locale

# Generic Errors
ERROR_SUCCESS             = 0
ERROR_FILE_NOT_FOUND      = 2     # ENOENT
ERROR_ACCESS_DENIED       = 1     # EPERM
ERROR_INVALID_HANDLE      = 9     # EBADF
ERROR_NOT_ENOUGH_MEMORY   = 12    # ENOMEM
ERROR_NOT_SUPPORTED       = 129   # ENOTSUP
ERROR_INVALID_PARAMETER   = 22    # EINVAL
ERROR_NEGATIVE_SEEK       = 29    # ESPIPE
ERROR_DISK_FULL           = 28    # ENOSPC
ERROR_ALREADY_EXISTS      = 17    # EEXIST
ERROR_INSUFFICIENT_BUFFER = 119   # ENOBUFS
ERROR_BAD_FORMAT          = 1000        # No such error code under Linux
ERROR_NO_MORE_FILES       = 1001        # No such error code under Linux
ERROR_HANDLE_EOF          = 1002        # No such error code under Linux
ERROR_CAN_NOT_COMPLETE    = 1003        # No such error code under Linux
ERROR_FILE_CORRUPT        = 1004        # No such error code under Linux

# Move method used by SFileSetFilePointer
FILE_BEGIN   = 0
FILE_CURRENT = 1
FILE_END     = 2

MAX_NAME_SIZE = 1024

# Info classes for archives used by SFileGetFileInfo
SFileMpqFileName              = 0  # Name of the archive file (TCHAR [])
SFileMpqStreamBitmap          = 1  # Array of bits,              each bit means availability of one block (BYTE [])
SFileMpqUserDataOffset        = 2  # Offset of the user data header (ULONGLONG)
SFileMpqUserDataHeader        = 3  # Raw (unfixed) user data header (TMPQUserData)
SFileMpqUserData              = 4  # MPQ USer data,          without the header (BYTE [])
SFileMpqHeaderOffset          = 5  # Offset of the MPQ header (ULONGLONG)
SFileMpqHeaderSize            = 6  # Fixed size of the MPQ header
SFileMpqHeader                = 7  # Raw (unfixed) archive header (TMPQHeader)
SFileMpqHetTableOffset        = 8  # Offset of the HET table,      relative to MPQ header (ULONGLONG)
SFileMpqHetTableSize          = 9  # Compressed size of the HET table (ULONGLONG)
SFileMpqHetHeader             = 10 # HET table header (TMPQHetHeader)
SFileMpqHetTable              = 11 # HET table as pointer. Must be freed using SFileFreeFileInfo
SFileMpqBetTableOffset        = 12 # Offset of the BET table,      relative to MPQ header (ULONGLONG)
SFileMpqBetTableSize          = 13 # Compressed size of the BET table (ULONGLONG)
SFileMpqBetHeader             = 14 # BET table header,        followed by the flags (TMPQBetHeader + DWORD[])
SFileMpqBetTable              = 15 # BET table as pointer. Must be freed using SFileFreeFileInfo
SFileMpqHashTableOffset       = 16 # Hash table offset,             relative to MPQ header (ULONGLONG)
SFileMpqHashTableSize64       = 17 # Compressed size of the hash table (ULONGLONG)
SFileMpqHashTableSize         = 18 # Size of the hash table,      in entries (DWORD)
SFileMpqHashTable             = 19 # Raw (unfixed) hash table (TMPQBlock [])
SFileMpqBlockTableOffset      = 20 # Block table offset,             relative to MPQ header (ULONGLONG)
SFileMpqBlockTableSize64      = 21 # Compressed size of the block table (ULONGLONG)
SFileMpqBlockTableSize        = 22 # Size of the block table,      in entries (DWORD)
SFileMpqBlockTable            = 23 # Raw (unfixed) block table (TMPQBlock [])
SFileMpqHiBlockTableOffset    = 24 # Hi-block table offset,            relative to MPQ header (ULONGLONG)
SFileMpqHiBlockTableSize64    = 25 # Compressed size of the hi-block table (ULONGLONG)
SFileMpqHiBlockTable          = 26 # The hi-block table (USHORT [])
SFileMpqSignatures            = 27 # Signatures present in the MPQ (DWORD)
SFileMpqStrongSignatureOffset = 28 # Byte offset of the strong signature, relative to begin of the file (ULONGLONG)
SFileMpqStrongSignatureSize   = 29 # Size of the strong signature (DWORD)
SFileMpqStrongSignature       = 30 # The strong signature (BYTE [])
SFileMpqArchiveSize64         = 31 # Archive size from the header (ULONGLONG)
SFileMpqArchiveSize           = 32 # Archive size from the header (DWORD)
SFileMpqMaxFileCount          = 33 # Max number of files in the archive (DWORD)
SFileMpqFileTableSize         = 34 # Number of entries in the file table (DWORD)
SFileMpqSectorSize            = 35 # Sector size (DWORD)
SFileMpqNumberOfFiles         = 36 # Number of files (DWORD)
SFileMpqRawChunkSize          = 37 # Size of the raw data chunk for MD5
SFileMpqStreamFlags           = 38 # Stream flags (DWORD)
SFileMpqFlags                 = 39 # Nonzero if the MPQ is read only (DWORD)
# Info classes for files used by SFileGetFileInfo
SFileInfoPatchChain           = 40 # Chain of patches where the file is (TCHAR [])
SFileInfoFileEntry            = 41 # The file entry for the file (TFileEntry)
SFileInfoHashEntry            = 42 # Hash table entry for the file (TMPQHash)
SFileInfoHashIndex            = 43 # Index of the hash table entry (DWORD)
SFileInfoNameHash1            = 44 # The first name hash in the hash table (DWORD)
SFileInfoNameHash2            = 45 # The second name hash in the hash table (DWORD)
SFileInfoNameHash3            = 46 # 64-bit file name hash for the HET/BET tables (ULONGLONG)
SFileInfoLocale               = 47 # File locale (DWORD)
SFileInfoFileIndex            = 48 # Block index (DWORD)
SFileInfoByteOffset           = 49 # File position in the archive (ULONGLONG)
SFileInfoFileTime             = 50 # File time (ULONGLONG)
SFileInfoFileSize             = 51 # Size of the file (DWORD)
SFileInfoCompressedSize       = 52 # Compressed file size (DWORD)
SFileInfoFlags                = 53 # File flags from (DWORD)
SFileInfoEncryptionKey        = 54 # File encryption key
SFileInfoEncryptionKeyRaw     = 55 # Unfixed value of the file key
SFileInfoCRC32                = 56 # CRC32 of the file


class MPQHANDLE(c_void_p):
	def __repr__(self):
		return '<MPQHANDLE object at %s: %s>' % (hex(id(self)), hex(self.value))

class SFILE_FIND_DATA(Structure):
	_fields_ = [
		('file_name', c_char * MAX_NAME_SIZE),
		('plain_name', c_char_p),
		('hash_index', c_uint32),
		('block_index', c_uint32),
		('file_size', c_uint32),
		('file_flags', c_uint32),
		('compressed_size', c_uint32),
		('file_time_lo', c_uint32),
		('file_time_hi', c_uint32),
		('locale', c_uint32),
	]

	def __init__(self):
		self.file_name = ''
		self.plain_name = ''
		self.hash_index = 0
		self.block_index = 0
		self.file_size = 0
		self.file_flags = 0
		self.compressed_size = 0
		self.file_time_lo = 0
		self.file_time_hi = 0
		self.locale = 0

class SFILE_CREATE_MPQ(Structure):
	_fields_ = [
		('size', c_uint32),
		('mpq_version', c_uint32),
		('user_data1', c_void_p),
		('user_data2', c_uint32),
		('stream_flags', c_uint32),
		('file_flags_listfile', c_uint32),
		('file_flags_attributes', c_uint32),
		('file_flags_signature', c_uint32),
		('attributes_flags', c_uint32),
		('sector_size', c_uint32),
		('raw_chunk_size', c_uint32),
		('max_file_count', c_uint32),
	]

	def __init__(self):
		self.size = 0
		self.mpq_version = 0
		self.user_data1 = None
		self.user_data2 = 0
		self.stream_flags = 0
		self.file_flags_listfile = 0
		self.file_flags_attributes = 0
		self.file_flags_signature = 0
		self.attributes_flags = 0
		self.sector_size = 0
		self.raw_chunk_size = 0
		self.max_file_count = 0

if STORMLIB_LOADED:
	# # UNICODE versions of the file access functions
	# TFileStream * FileStream_CreateFile(const TCHAR * szFileName, DWORD dwStreamFlags);
	# TFileStream * FileStream_OpenFile(const TCHAR * szFileName, DWORD dwStreamFlags);
	# const TCHAR * FileStream_GetFileName(TFileStream * pStream);
	# size_t FileStream_Prefix(const TCHAR * szFileName, DWORD * pdwProvider);

	# bool FileStream_SetCallback(TFileStream * pStream, SFILE_DOWNLOAD_CALLBACK pfnCallback, void * pvUserData);

	# bool FileStream_GetBitmap(TFileStream * pStream, void * pvBitmap, DWORD cbBitmap, DWORD * pcbLengthNeeded);
	# bool FileStream_Read(TFileStream * pStream, ULONGLONG * pByteOffset, void * pvBuffer, DWORD dwBytesToRead);
	# bool FileStream_Write(TFileStream * pStream, ULONGLONG * pByteOffset, const void * pvBuffer, DWORD dwBytesToWrite);
	# bool FileStream_SetSize(TFileStream * pStream, ULONGLONG NewFileSize);
	# bool FileStream_GetSize(TFileStream * pStream, ULONGLONG * pFileSize);
	# bool FileStream_GetPos(TFileStream * pStream, ULONGLONG * pByteOffset);
	# bool FileStream_GetTime(TFileStream * pStream, ULONGLONG * pFT);
	# bool FileStream_GetFlags(TFileStream * pStream, LPDWORD pdwStreamFlags);
	# bool FileStream_Replace(TFileStream * pStream, TFileStream * pNewStream);
	# void FileStream_Close(TFileStream * pStream);

	# #-----------------------------------------------------------------------------
	# # Functions prototypes for Storm.dll

	# # Typedefs for functions exported by Storm.dll
	# typedef LCID  (WINAPI * SFILESETLOCALE)(LCID);
	# typedef bool  (WINAPI * SFILEOPENARCHIVE)(const char *, DWORD, DWORD, HANDLE *);
	# typedef bool  (WINAPI * SFILECLOSEARCHIVE)(HANDLE);
	# typedef bool  (WINAPI * SFILEOPENFILEEX)(HANDLE, const char *, DWORD, HANDLE *);
	# typedef bool  (WINAPI * SFILECLOSEFILE)(HANDLE);
	# typedef DWORD (WINAPI * SFILEGETFILESIZE)(HANDLE, LPDWORD);
	# typedef DWORD (WINAPI * SFILESETFILEPOINTER)(HANDLE, LONG, LONG *, DWORD);
	# typedef bool  (WINAPI * SFILEREADFILE)(HANDLE, void *, DWORD, LPDWORD, LPOVERLAPPED);

	# #-----------------------------------------------------------------------------
	# # Functions for manipulation with StormLib global flags

	# # Alternate marker support. This is for MPQs masked as DLLs (*.asi), which
	# # patch Storm.dll at runtime. Call before SFileOpenArchive
	# bool   WINAPI SFileSetArchiveMarkers(PSFILE_MARKERS pMarkers);

	# # Call before SFileOpenFileEx
	# LCID   WINAPI SFileGetLocale();
	_StormLib.SFileGetLocale.restype = c_uint32

	# LCID   WINAPI SFileSetLocale(LCID lcNewLocale);
	_StormLib.SFileSetLocale.argtypes = [c_uint32]
	_StormLib.SFileSetLocale.restype = c_uint32

	# #-----------------------------------------------------------------------------
	# # Functions for archive manipulation

	# bool   WINAPI SFileOpenArchive(const TCHAR * szMpqName, DWORD dwPriority, DWORD dwFlags, HANDLE * phMpq);
	_StormLib.SFileOpenArchive.argtypes = [c_char_p, c_int32, c_uint32, POINTER(MPQHANDLE)]
	_StormLib.SFileOpenArchive.restype = c_bool

	# bool   WINAPI SFileCreateArchive(const TCHAR * szMpqName, DWORD dwCreateFlags, DWORD dwMaxFileCount, HANDLE * phMpq);
	_StormLib.SFileCreateArchive.argtypes = [c_char_p, c_int32, c_uint32, POINTER(MPQHANDLE)]
	_StormLib.SFileCreateArchive.restype = c_bool

	# bool   WINAPI SFileCreateArchive2(const TCHAR * szMpqName, PSFILE_CREATE_MPQ pCreateInfo, HANDLE * phMpq);
	_StormLib.SFileCreateArchive2.argtypes = [c_char_p, POINTER(SFILE_CREATE_MPQ), POINTER(MPQHANDLE)]
	_StormLib.SFileCreateArchive2.restype = c_bool

	# bool   WINAPI SFileSetDownloadCallback(HANDLE hMpq, SFILE_DOWNLOAD_CALLBACK DownloadCB, void * pvUserData);

	# bool   WINAPI SFileFlushArchive(HANDLE hMpq);
	_StormLib.SFileFlushArchive.argtypes = [MPQHANDLE]
	_StormLib.SFileFlushArchive.restype = c_bool

	# bool   WINAPI SFileCloseArchive(HANDLE hMpq);
	_StormLib.SFileCloseArchive.argtypes = [MPQHANDLE]
	_StormLib.SFileCloseArchive.restype = c_bool

	# # Adds another listfile into MPQ. The currently added listfile(s) remain,
	# # so you can use this API to combining more listfiles.
	# # Note that this function is internally called by SFileFindFirstFile
	# DWORD  WINAPI SFileAddListFile(HANDLE hMpq, const TCHAR * szListFile);
	_StormLib.SFileAddListFile.argtypes = [MPQHANDLE, c_char_p]
	_StormLib.SFileAddListFile.restype = c_uint32

	# # Archive compacting
	# bool   WINAPI SFileSetCompactCallback(HANDLE hMpq, SFILE_COMPACT_CALLBACK CompactCB, void * pvUserData);

	# bool   WINAPI SFileCompactArchive(HANDLE hMpq, const TCHAR * szListFile, bool bReserved);
	_StormLib.SFileCompactArchive.argtypes = [MPQHANDLE, c_char_p, c_bool]
	_StormLib.SFileCompactArchive.restype = c_bool

	# # Changing the maximum file count
	# DWORD  WINAPI SFileGetMaxFileCount(HANDLE hMpq);
	_StormLib.SFileGetMaxFileCount.argtypes = [MPQHANDLE]
	_StormLib.SFileGetMaxFileCount.restype = c_uint32

	# bool   WINAPI SFileSetMaxFileCount(HANDLE hMpq, DWORD dwMaxFileCount);
	_StormLib.SFileSetMaxFileCount.argtypes = [MPQHANDLE, c_uint32]
	_StormLib.SFileSetMaxFileCount.restype = c_bool

	# # Changing (attributes) file
	# DWORD  WINAPI SFileGetAttributes(HANDLE hMpq);
	_StormLib.SFileGetAttributes.argtypes = [MPQHANDLE]
	_StormLib.SFileGetAttributes.restype = c_uint32

	# bool   WINAPI SFileSetAttributes(HANDLE hMpq, DWORD dwFlags);
	_StormLib.SFileSetAttributes.argtypes = [MPQHANDLE, c_uint32]
	_StormLib.SFileSetAttributes.restype = c_bool

	# bool   WINAPI SFileUpdateFileAttributes(HANDLE hMpq, const char * szFileName);
	_StormLib.SFileUpdateFileAttributes.argtypes = [MPQHANDLE, c_char_p]
	_StormLib.SFileUpdateFileAttributes.restype = c_bool

	# #-----------------------------------------------------------------------------
	# # Functions for manipulation with patch archives

	# bool   WINAPI SFileOpenPatchArchive(HANDLE hMpq, const TCHAR * szPatchMpqName, const char * szPatchPathPrefix, DWORD dwFlags);
	_StormLib.SFileOpenPatchArchive.argtypes = [MPQHANDLE, c_char_p, c_char_p, c_uint32]
	_StormLib.SFileOpenPatchArchive.restype = c_bool

	# bool   WINAPI SFileIsPatchedArchive(HANDLE hMpq);
	_StormLib.SFileIsPatchedArchive.argtypes = [MPQHANDLE]
	_StormLib.SFileIsPatchedArchive.restype = c_bool

	# #-----------------------------------------------------------------------------
	# # Functions for file manipulation

	# # Reading from MPQ file
	# bool   WINAPI SFileHasFile(HANDLE hMpq, const char * szFileName);
	_StormLib.SFileHasFile.argtypes = [MPQHANDLE, c_char_p]
	_StormLib.SFileHasFile.restype = c_bool
	
	# bool   WINAPI SFileOpenFileEx(HANDLE hMpq, const char * szFileName, DWORD dwSearchScope, HANDLE * phFile);
	_StormLib.SFileOpenFileEx.argtypes = [MPQHANDLE, c_char_p, c_uint32, POINTER(MPQHANDLE)]
	_StormLib.SFileOpenFileEx.restype = c_bool

	# DWORD  WINAPI SFileGetFileSize(HANDLE hFile, LPDWORD pdwFileSizeHigh);
	_StormLib.SFileGetFileSize.argtypes = [MPQHANDLE, POINTER(c_uint32)]
	_StormLib.SFileGetFileSize.restype = c_uint32

	# DWORD  WINAPI SFileSetFilePointer(HANDLE hFile, LONG lFilePos, LONG * plFilePosHigh, DWORD dwMoveMethod);
	_StormLib.SFileSetFilePointer.argtypes = [MPQHANDLE, c_int32, POINTER(c_int32), c_uint32]
	_StormLib.SFileSetFilePointer.restype = c_uint32

	# bool   WINAPI SFileReadFile(HANDLE hFile, void * lpBuffer, DWORD dwToRead, LPDWORD pdwRead, LPOVERLAPPED lpOverlapped);
	_StormLib.SFileReadFile.argtypes = [MPQHANDLE, c_void_p, c_uint32, POINTER(c_uint32), c_void_p]
	_StormLib.SFileReadFile.restype = c_bool

	# bool   WINAPI SFileCloseFile(HANDLE hFile);
	_StormLib.SFileCloseFile.argtypes = [MPQHANDLE]
	_StormLib.SFileCloseFile.restype = c_bool

	# # Retrieve information about an archive or about a file within the archive
	# bool   WINAPI SFileGetFileInfo(HANDLE hMpqOrFile, SFileInfoClass InfoClass, void * pvFileInfo, DWORD cbFileInfo, LPDWORD pcbLengthNeeded);
	_StormLib.SFileGetFileInfo.argtypes = [MPQHANDLE, c_int32, c_void_p, c_uint32, POINTER(c_uint32)]
	_StormLib.SFileGetFileInfo.restype = c_bool

	# bool   WINAPI SFileGetFileName(HANDLE hFile, char * szFileName);
	_StormLib.SFileGetFileName.argtypes = [MPQHANDLE, c_char_p]
	_StormLib.SFileGetFileName.restype = c_bool

	# bool   WINAPI SFileFreeFileInfo(void * pvFileInfo, SFileInfoClass InfoClass);

	# # High-level extract function
	# bool   WINAPI SFileExtractFile(HANDLE hMpq, const char * szToExtract, const TCHAR * szExtracted, DWORD dwSearchScope);

	# #-----------------------------------------------------------------------------
	# # Functions for file and archive verification

	# # Generates file CRC32
	# bool   WINAPI SFileGetFileChecksums(HANDLE hMpq, const char * szFileName, LPDWORD pdwCrc32, char * pMD5);

	# # Verifies file against its checksums stored in (attributes) attributes (depending on dwFlags).
	# # For dwFlags, use one or more of MPQ_ATTRIBUTE_MD5
	# DWORD  WINAPI SFileVerifyFile(HANDLE hMpq, const char * szFileName, DWORD dwFlags);

	# # Verifies raw data of the archive. Only works for MPQs version 4 or newer
	# DWORD  WINAPI SFileVerifyRawData(HANDLE hMpq, DWORD dwWhatToVerify, const char * szFileName);

	# # Verifies the signature, if present
	# bool   WINAPI SFileSignArchive(HANDLE hMpq, DWORD dwSignatureType);
	# DWORD  WINAPI SFileVerifyArchive(HANDLE hMpq);

	# #-----------------------------------------------------------------------------
	# # Functions for file searching

	# HANDLE WINAPI SFileFindFirstFile(HANDLE hMpq, const char * szMask, SFILE_FIND_DATA * lpFindFileData, const TCHAR * szListFile);
	_StormLib.SFileFindFirstFile.argtypes = [MPQHANDLE, c_char_p, POINTER(SFILE_FIND_DATA), c_char_p]
	_StormLib.SFileFindFirstFile.restype = MPQHANDLE

	# bool   WINAPI SFileFindNextFile(HANDLE hFind, SFILE_FIND_DATA * lpFindFileData);
	_StormLib.SFileFindNextFile.argtypes = [MPQHANDLE, POINTER(SFILE_FIND_DATA)]
	_StormLib.SFileFindNextFile.restype = c_bool

	# bool   WINAPI SFileFindClose(HANDLE hFind);
	_StormLib.SFileFindClose.argtypes = [MPQHANDLE]
	_StormLib.SFileFindClose.restype = c_bool

	# HANDLE WINAPI SListFileFindFirstFile(HANDLE hMpq, const TCHAR * szListFile, const char * szMask, SFILE_FIND_DATA * lpFindFileData);
	# bool   WINAPI SListFileFindNextFile(HANDLE hFind, SFILE_FIND_DATA * lpFindFileData);
	# bool   WINAPI SListFileFindClose(HANDLE hFind);

	# # Locale support
	# DWORD  WINAPI SFileEnumLocales(HANDLE hMpq, const char * szFileName, LCID * plcLocales, LPDWORD pdwMaxLocales, DWORD dwSearchScope);

	# #-----------------------------------------------------------------------------
	# # Support for adding files to the MPQ

	# bool   WINAPI SFileCreateFile(HANDLE hMpq, const char * szArchivedName, ULONGLONG FileTime, DWORD dwFileSize, LCID lcLocale, DWORD dwFlags, HANDLE * phFile);
	_StormLib.SFileCreateFile.argtypes = [MPQHANDLE, c_char_p, c_ulonglong, c_uint32, c_uint32, c_uint32, POINTER(MPQHANDLE)]
	_StormLib.SFileCreateFile.restype = c_bool

	# bool   WINAPI SFileWriteFile(HANDLE hFile, const void * pvData, DWORD dwSize, DWORD dwCompression);
	_StormLib.SFileWriteFile.argtypes = [MPQHANDLE, c_void_p, c_uint32, c_uint32]
	_StormLib.SFileWriteFile.restype = c_bool

	# bool   WINAPI SFileFinishFile(HANDLE hFile);
	_StormLib.SFileFinishFile.argtypes = [MPQHANDLE]
	_StormLib.SFileFinishFile.restype = c_bool

	# bool   WINAPI SFileAddFileEx(HANDLE hMpq, const TCHAR * szFileName, const char * szArchivedName, DWORD dwFlags, DWORD dwCompression, DWORD dwCompressionNext);
	_StormLib.SFileAddFileEx.argtypes = [MPQHANDLE, c_char_p, c_char_p, c_uint32, c_uint32, c_uint32]
	_StormLib.SFileAddFileEx.restype = c_bool

	# bool   WINAPI SFileAddFile(HANDLE hMpq, const TCHAR * szFileName, const char * szArchivedName, DWORD dwFlags);
	# _StormLib.SFileAddFile.argtypes = [MPQHANDLE, c_char_p, c_char_p, c_uint32]
	# _StormLib.SFileAddFile.restype = c_bool

	# bool   WINAPI SFileAddWave(HANDLE hMpq, const TCHAR * szFileName, const char * szArchivedName, DWORD dwFlags, DWORD dwQuality);
	# _StormLib.SFileAddWave.argtypes = [MPQHANDLE, c_char_p, c_char_p, c_uint32, c_uint32]
	# _StormLib.SFileAddWave.restype = c_bool

	# bool   WINAPI SFileRemoveFile(HANDLE hMpq, const char * szFileName, DWORD dwSearchScope);
	_StormLib.SFileRemoveFile.argtypes = [MPQHANDLE, c_char_p, c_uint32]
	_StormLib.SFileRemoveFile.restype = c_bool

	# bool   WINAPI SFileRenameFile(HANDLE hMpq, const char * szOldFileName, const char * szNewFileName);
	_StormLib.SFileRenameFile.argtypes = [MPQHANDLE, c_char_p, c_char_p]
	_StormLib.SFileRenameFile.restype = c_bool

	# bool   WINAPI SFileSetFileLocale(HANDLE hFile, LCID lcNewLocale);
	_StormLib.SFileSetFileLocale.argtypes = [MPQHANDLE, c_uint32]
	_StormLib.SFileSetFileLocale.restype = c_bool

	# bool   WINAPI SFileSetDataCompression(DWORD DataCompression);
	# _StormLib.SFileSetDataCompression.argtypes = [c_uint32]
	# _StormLib.SFileSetDataCompression.restype = c_bool

	# bool   WINAPI SFileSetAddFileCallback(HANDLE hMpq, SFILE_ADDFILE_CALLBACK AddFileCB, void * pvUserData);

	# #-----------------------------------------------------------------------------
	# # Compression and decompression

	# int    WINAPI SCompImplode    (void * pvOutBuffer, int * pcbOutBuffer, void * pvInBuffer, int cbInBuffer);
	# int    WINAPI SCompExplode    (void * pvOutBuffer, int * pcbOutBuffer, void * pvInBuffer, int cbInBuffer);
	# int    WINAPI SCompCompress   (void * pvOutBuffer, int * pcbOutBuffer, void * pvInBuffer, int cbInBuffer, unsigned uCompressionMask, int nCmpType, int nCmpLevel);
	# int    WINAPI SCompDecompress (void * pvOutBuffer, int * pcbOutBuffer, void * pvInBuffer, int cbInBuffer);
	# int    WINAPI SCompDecompress2(void * pvOutBuffer, int * pcbOutBuffer, void * pvInBuffer, int cbInBuffer);
	# int    WINAPI SCompDecompress_SC1B(void * pvOutBuffer, int * pcbOutBuffer, void * pvInBuffer, int cbInBuffer);

	# #-----------------------------------------------------------------------------
	# # Non-Windows support for SetLastError/GetLastError

	# void  SetLastError(DWORD dwErrCode);
	# try:
	# 	_StormLib.SetLastError.argtypes = [c_uint32]
	# except:
	# 	_StormLib.SetLastError = None

	# DWORD GetLastError();
	try:
		_StormLib.GetLastError.restype = c_uint32
	except:
		_StormLib.GetLastError = None

def SFInvalidHandle(h):
	return not isinstance(h, MPQHANDLE) or h.value in [None,0,-1]

def SFileGetLocale():
	return _StormLib.SFileGetLocale()

def SFileSetLocale(locale): # type: (int) -> int
	return _StormLib.SFileSetLocale(locale)

def SFileOpenArchive(mpq_path, priority=0, flags=STREAM_FLAG_READ_ONLY): # type: (str, int, int) -> (MPQHANDLE | None)
	h = MPQHANDLE()
	if _StormLib.SFileOpenArchive(mpq_path, priority, flags, byref(h)):
		return h

def SFileCreateArchive(mpq_path, flags=0, max_files=1024): # type: (str, int, int) -> (MPQHANDLE | None)
	h = MPQHANDLE()
	if _StormLib.SFileCreateArchive(mpq_path, flags, max_files, byref(h)):
		return h

def SFileCreateArchive2(mpq_path, create_info): # type: (str, SFILE_CREATE_MPQ) -> (MPQHANDLE | None)
	create_info.size = sizeof(SFILE_CREATE_MPQ)
	h = MPQHANDLE()
	if _StormLib.SFileCreateArchive2(mpq_path, byref(create_info), byref(h)):
		return h

def SFileFlushArchive(mpq): # type: (MPQHANDLE) -> bool
	return _StormLib.SFileFlushArchive(mpq)

def SFileCloseArchive(mpq): # type: (MPQHANDLE) -> bool
	return _StormLib.SFileCloseArchive(mpq)

def SFileAddListFile(mpq, listfile_path): # type: (MPQHANDLE, str) -> int
	return _StormLib.SFileAddListFile(mpq, listfile_path)

def SFileCompactArchive(mpq, listfile_path=None): # type: (MPQHANDLE, str) -> bool
	return _StormLib.SFileCompactArchive(mpq, listfile_path, True)

def SFileGetMaxFileCount(mpq): # type: (MPQHANDLE) -> int
	return _StormLib.SFileGetMaxFileCount(mpq)

def SFileSetMaxFileCount(mpq, file_count): # type: (MPQHANDLE, int) -> bool
	return _StormLib.SFileSetMaxFileCount(mpq, file_count)

def SFileGetAttributes(mpq): # type: (MPQHANDLE) -> int
	return _StormLib.SFileGetAttributes(mpq)

def SFileSetAttributes(mpq, attributes): # type: (MPQHANDLE, int) -> bool
	return _StormLib.SFileSetAttributes(mpq, attributes)

def SFileUpdateFileAttributes(mpq, attributes_file_path): # type: (MPQHANDLE, str) -> bool
	return _StormLib.SFileUpdateFileAttributes(mpq, attributes_file_path)

def SFileOpenPatchArchive(mpq, patch_mpq_path, patch_path_prefix, flags=0): # type: (MPQHANDLE, str, str, int) -> bool
	return _StormLib.SFileOpenPatchArchive(mpq, patch_mpq_path, patch_path_prefix, flags)

def SFileIsPatchedArchive(mpq): # type: (MPQHANDLE) -> bool
	return _StormLib.SFileIsPatchedArchive(mpq)

def SFileHasFile(mpq, file_name): # type: (MPQHANDLE, str) -> bool
	return _StormLib.SFileHasFile(mpq, file_name)

def SFileOpenFileEx(mpq, file_name, search=SFILE_OPEN_FROM_MPQ): # type: (MPQHANDLE, str, int) -> (MPQHANDLE | None)
	h = MPQHANDLE()
	if _StormLib.SFileOpenFileEx(mpq, file_name, search, byref(h)):
		return h

def SFileGetFileSize(file): # type: (MPQHANDLE) -> (int | None)
	size = _StormLib.SFileGetFileSize(file, None)
	if size == SFILE_INVALID_SIZE:
		return None
	return size

def SFileSetFilePointer(file, position, move_method=FILE_BEGIN): # type: (MPQHANDLE, int, int) -> (int | None)
	size = _StormLib.SFileSetFilePointer(file, position, None, move_method)
	if size == SFILE_INVALID_SIZE:
		return None
	return size

def SFileReadFile(file, read=None): # type: (MPQHANDLE, int) -> (tuple[bytes | None, int])
	all = read == None
	if all:
		read = SFileGetFileSize(file)
		if read == -1:
			return (None, 0)
	data = create_string_buffer(read)
	r = c_uint32()
	total_read = 0
	while total_read < read:
		if _StormLib.SFileReadFile(file, byref(data, total_read), read-total_read, byref(r), None):
			total_read += r.value
		else:
			return (None, 0)
	return (data.raw[:total_read],total_read)

def SFileCloseFile(file): # type: (MPQHANDLE) -> bool
	return _StormLib.SFileCloseFile(file)

def SFileGetFileInfo(mpq, info_class): # type: (MPQHANDLE, int) -> (int | long | str | None)
	info_container = None
	if info_class == SFileMpqBlockTableSize:
		info_container = c_uint32()
	# TODO: Implement more info types
	if info_container == None:
		raise NotImplementedError('Info class %d not implemented in SFileGetFileInfo' % info_class)
	length_needed = c_uint32()
	if not _StormLib.SFileGetFileInfo(mpq, info_class, byref(info_container), sizeof(info_container), byref(length_needed)):
		return None
	if isinstance(info_container, c_uint):
		return info_container.value

def SFileGetFileName(file): # type: (MPQHANDLE) -> (str | None)
	name = create_string_buffer(MAX_NAME_SIZE)
	if _StormLib.SFileGetFileName(file, byref(name)):
		return str(name.raw)

def SFileFindFirstFile(mpq, find_mask, listfile_path=None): # type: (MPQHANDLE, str, str) -> (tuple[MPQHANDLE | None, SFILE_FIND_DATA | None])
	file_data = SFILE_FIND_DATA()
	find_handle = _StormLib.SFileFindFirstFile(mpq, find_mask, byref(file_data), listfile_path)
	if not SFInvalidHandle(find_handle):
		return (find_handle, file_data)
	return (None, None)

def SFileFindNextFile(find_handle): # type: (MPQHANDLE) -> (SFILE_FIND_DATA | None)
	file_data = SFILE_FIND_DATA()
	if _StormLib.SFileFindNextFile(find_handle, byref(file_data)):
		return file_data

def SFileFindClose(find_handle): # type: (MPQHANDLE) -> bool
	return _StormLib.SFileFindClose(find_handle)

def SFileCreateFile(mpq, file_name, file_time, file_size, locale, flags): # type: (MPQHANDLE, str, int, int, int, int) -> (MPQHANDLE | None)
	h = MPQHANDLE()
	if _StormLib.SFileCreateFile(mpq, file_name, file_time, file_size, locale, flags, byref(h)):
		return h

def SFileWriteFile(file, data, compression): # type: (MPQHANDLE, bytes, int) -> (bool)
	return _StormLib.SFileWriteFile(file, data, len(data), compression)

def SFileFinishFile(file): # type: (MPQHANDLE) -> (bool)
	return _StormLib.SFileFinishFile(file)

def SFileAddFileEx(mpq, file_path, file_name, flags=MPQ_FILE_REPLACEEXISTING, compression=0, compression_next=MPQ_COMPRESSION_NEXT_SAME): # type: (MPQHANDLE, str, str, int, int, int) -> (bool)
	return _StormLib.SFileAddFileEx(mpq, file_path, file_name, flags, compression, compression_next)

def SFileRemoveFile(mpq, file_name): # type: (MPQHANDLE, str) -> (bool)
	return _StormLib.SFileRemoveFile(mpq, file_name, 0)

def SFileRenameFile(mpq, file_name, new_file_name): # type: (MPQHANDLE, str, str) -> (bool)
	return _StormLib.SFileRenameFile(mpq, file_name, new_file_name)

def SFileSetFileLocale(file, locale): # type: (MPQHANDLE, int) -> (bool)
	return _StormLib.SFileSetFileLocale(file, locale)

# def SFSetLastError(error): # type: (int) -> None
# 	# StormLib only implements its own SetLastError on platforms other than windows
# 	if _StormLib.SetLastError == None:
# 		windll.kernel32.SetLastError(error)
# 	return _StormLib.SetLastError(error)

def SFGetLastError():
	# StormLib only implements its own GetLastError on platforms other than windows
	if _StormLib.GetLastError == None:
		return GetLastError()
	return _StormLib.GetLastError()
