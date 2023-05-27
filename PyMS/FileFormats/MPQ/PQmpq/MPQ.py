
# MPQ functionality based off of SFmpq (by Quantam and ShadowFlare), which is based off StormLib (by Ladislav Zezula)

from . import MPQCrypt, MPQComp

from ....Utilities.PyMSError import PyMSError
from ....Utilities.Struct import *
from ....Utilities.utils import flags_code

import re, math, struct

from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from typing import TextIO, BinaryIO

class MPQHeaderV1(Struct):
	ID_MPQ = b'MPQ\x1A'
	ID_BN3 = b'BN3\x1A'

	_fields = (
		('type_id', Type.str(4)),
		('header_size', Type.u32()),
		('archive_size', Type.u32()),
		('format_version', Type.u16()),
		('sector_size_shift', Type.u16()),
		('hash_table_offset', Type.u32()),
		('block_table_offset', Type.u32()),
		('hash_table_entries', Type.u32()),
		('block_table_entries', Type.u32()),
	)

	type_id: str
	header_size: int
	archive_size: int
	format_version: int
	sector_size_shift: int
	hash_table_offset: int
	block_table_offset: int
	hash_table_entries: int
	block_table_entries: int

class MPQLocale:
	neutral    = 0 # Neutral (English US)
	chinese    = 1028 # 0x404
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

class MPQHashEntry(Struct):
	BLOCK_INDEX_EMPTY   = 0xFFFFFFFF
	BLOCK_INDEX_DELETED = 0xFFFFFFFE

	_fields = (
		('hash_name_a', Type.u32()),
		('hash_name_b', Type.u32()),
		('locale', Type.u16()),
		('platform', Type.u16()),
		('block_index', Type.u32())
	)

	hash_name_a: int
	hash_name_b: int
	locale: int
	platform: int
	block_index: int

class MPQBlockFlag:
	imploded      = 0x00000100
	compressed    = 0x00000200
	encrypted     = 0x00010000
	adjust_key    = 0x00020000
	patch_file    = 0x00100000
	single_unit   = 0x01000000
	delete_marker = 0x02000000
	sector_crc    = 0x04000000
	exists        = 0x80000000

class MPQBlockEntry(Struct):
	_fields = (
		('file_offset', Type.u32()),
		('compressed_size', Type.u32()),
		('file_size', Type.u32()),
		('flags', Type.u32())
	)

	file_offset: int
	compressed_size: int
	file_size: int
	flags: int

class MPQFileEntry(object):
	UNKNOWN_PREFIX = '~unknowns\\unknown_'

	def __init__(self, filename, hash_entry, block_entry):
		self.filename = filename
		self.locale = hash_entry.locale
		self.compressed_size = block_entry.compressed_size
		self.file_size = block_entry.file_size
		self.flags = block_entry.flags

	def __repr__(self):
		return """<%s.%s
	filename = '%s'
	locale = %d
	compressed_size = %d
	file_size = %d
	flags = %s
>""" % (
	self.__class__.__module__, self.__class__.__name__,
	self.filename,
	self.locale,
	self.compressed_size,
	self.file_size,
	flags_code(self.flags, {
		MPQBlockFlag.imploded: "imploded",
		MPQBlockFlag.compressed: "compressed",
		MPQBlockFlag.encrypted: "encrypted",
		MPQBlockFlag.adjust_key: "adjust_key",
		MPQBlockFlag.patch_file: "patch_file",
		MPQBlockFlag.single_unit: "single_unit",
		MPQBlockFlag.delete_marker: "delete_marker",
		MPQBlockFlag.sector_crc: "sector_crc",
		MPQBlockFlag.exists: "exists",
	})
)

class MPQTableKey:
	hash_table = MPQCrypt.hash_string('(hash table)', MPQCrypt.HashType.key)
	block_table = MPQCrypt.hash_string('(block table)', MPQCrypt.HashType.key)

class MPQInternalFile:
	attributes = "(attributes)"
	listfile = "(listfile)"
	signature = "(signature)"

RE_NEWLINE = re.compile(r'[\n\r]+')
class Listfiles(object):
	def __init__(self):
		self.filenames = {}

	def add_listfile_list(self, filenames): # type: (list[str]) -> None
		for filename in filenames:
			hash_name_a = MPQCrypt.hash_string(filename, MPQCrypt.HashType.name_a)
			hash_name_b = MPQCrypt.hash_string(filename, MPQCrypt.HashType.name_b)
			self.filenames[(hash_name_a, hash_name_b)] = filename

	def add_listfile_str(self, filenames): # type: (str) -> None
		self.add_listfile_list(RE_NEWLINE.split(filenames))

	def add_listfile_file(self, file): # type: (TextIO) -> None
		self.add_listfile_str(file.read())

	def add_listfile_path(self, path): # type: (str) -> None
		with open(path, 'r') as file:
			self.add_listfile_file(file)

	def get_filenames(self): # type: () -> list[str]
		return list(self.filenames.values())

BYTE = struct.Struct('<B')

class MPQ(object):
	def __init__(self): # type: () -> None
		self.mpq_offset = None # type: int | None
		self.file_size = None # type: int | None
		self.headerv1 = None # type: MPQHeaderV1 | None
		self.path = None # type: str | None
		self.file_handle = None # type: BinaryIO | None
		self.hash_table = None # type: list[MPQHashEntry] | None
		self.block_table = None # type: list[MPQBlockEntry] | None
		self.internal_listfiles = None # type: Listfiles | None

		self.external_listfiles = None # type: Listfiles | None

	def load_file(self, path): # type: (str) -> None
		try:
			file_handle = open(path, 'rb')
		except:
			raise PyMSError('Load', "Could not load '%s'" % path)
		try:
			file_handle.seek(0, 2)
			file_size = file_handle.tell()
			file_handle.seek(0)

			# Find MPQ offset
			mpq_offset = 0
			max_offset = file_size - MPQHeaderV1.size()
			while mpq_offset < max_offset:
				file_handle.seek(mpq_offset)
				type_id = file_handle.read(4)
				if type_id == MPQHeaderV1.ID_MPQ:
					break
				if type_id == MPQHeaderV1.ID_BN3:
					raise PyMSError('Load', "BN3 type MPQ's are not currently supported")
				mpq_offset += 512
			else:
				raise PyMSError('Load', "Couldn't find MPQ in '%s'" % path)

			# Load v1 header
			file_handle.seek(mpq_offset)
			headerv1 = MPQHeaderV1.unpack_file(file_handle)
			# print(headerv1)
			if headerv1.format_version != 0:
				raise PyMSError('Load', "Unsupported MPQ version (expected 0, got %d)" % headerv1.format_version)

			# Load hash table
			try:
				file_handle.seek(mpq_offset + headerv1.hash_table_offset)
				hash_table_data = file_handle.read(MPQHashEntry.size() * headerv1.hash_table_entries)
			except:
				raise PyMSError('Load', "Couldn't read hash table")
			hash_table_data = MPQCrypt.decrypt(hash_table_data, MPQTableKey.hash_table)
			hash_table = MPQHashEntry.unpack_array(hash_table_data, headerv1.hash_table_entries)
			# for entry in hash_table:
			# 	if not entry.block_index in (MPQHashEntry.BLOCK_INDEX_EMPTY, MPQHashEntry.BLOCK_INDEX_DELETED):
			# 		print(entry)
			
			# Load block table
			try:
				file_handle.seek(mpq_offset + headerv1.block_table_offset)
				block_table_data = file_handle.read(MPQBlockEntry.size() * headerv1.block_table_entries)
			except:
				raise PyMSError('Load', "Couldn't read block table")
			block_table_data = MPQCrypt.decrypt(block_table_data, MPQTableKey.block_table)
			block_table = MPQBlockEntry.unpack_array(block_table_data, headerv1.block_table_entries)
			# for entry in block_table:
			# 	print(entry)
		except:
			file_handle.close()
			raise

		self.close()
		self.mpq_offset = mpq_offset
		self.file_size = file_size
		self.headerv1 = headerv1
		self.path = path
		self.file_handle = file_handle
		self.hash_table = hash_table
		self.block_table = block_table

	def close(self):
		self.mpq_offset = None
		self.file_size = None
		self.headerv1 = None
		self.path = None
		if self.file_handle:
			self.file_handle.close()
		self.file_handle = None
		self.hash_table = None
		self.block_table = None
		self.internal_listfiles = None

	# Set a Listfiles object on the MPQ so you don't need to continue passing it to `list_files`
	def set_listfiles(self, listfiles): # type: (Listfiles) -> None
		self.external_listfiles = listfiles

	def _find_hash_entries(self, filename): # type: (str) -> list[MPQHashEntry]
		assert self.hash_table is not None
		entries = [] # type: list[MPQHashEntry]
		hash_name_a = MPQCrypt.hash_string(filename, MPQCrypt.HashType.name_a)
		hash_name_b = MPQCrypt.hash_string(filename, MPQCrypt.HashType.name_b)
		for hash_entry in self.hash_table:
			if hash_entry.hash_name_a == hash_name_a and hash_entry.hash_name_b == hash_name_b and (hash_entry.block_index & MPQHashEntry.BLOCK_INDEX_DELETED) != MPQHashEntry.BLOCK_INDEX_DELETED:
				entries.append(hash_entry)
		return entries

	def _find_hash_entry(self, start_index, hash_name_a, hash_name_b, locale=MPQLocale.neutral): # type: (int, int, int, int) -> (MPQHashEntry | None)
		assert self.headerv1 is not None
		assert self.hash_table is not None
		neutral_hash_entry = None # type: MPQHashEntry | None
		for offset in range(self.headerv1.hash_table_entries):
			index = (start_index + offset) % self.headerv1.hash_table_entries
			hash_entry = self.hash_table[index]
			if hash_entry.block_index == MPQHashEntry.BLOCK_INDEX_EMPTY:
				return None
			if hash_entry.hash_name_a == hash_name_a and hash_entry.hash_name_b == hash_name_b and hash_entry.block_index != MPQHashEntry.BLOCK_INDEX_DELETED:
				# If the locale is correct return it
				if hash_entry.locale == locale:
					return hash_entry
				# If the entry has the neutral locale, store it to return in the case there is no entry with the requested locale
				elif hash_entry.locale == MPQLocale.neutral and neutral_hash_entry is None:
					neutral_hash_entry = hash_entry
		return neutral_hash_entry

	def _find_hash_entry_by_filename(self, filename, locale=MPQLocale.neutral): # type: (str, int) -> (MPQHashEntry | None)
		assert self.headerv1 is not None
		assert self.hash_table is not None
		if filename.startswith(MPQFileEntry.UNKNOWN_PREFIX):
			try:
				index = int(filename.split('_')[-1], 16)
				return self.hash_table[index]
			except:
				raise PyMSError('MPQ', 'Invalid unknown filename')
		start_index = MPQCrypt.hash_string(filename, MPQCrypt.HashType.position) % self.headerv1.hash_table_entries
		hash_name_a = MPQCrypt.hash_string(filename, MPQCrypt.HashType.name_a)
		hash_name_b = MPQCrypt.hash_string(filename, MPQCrypt.HashType.name_b)
		return self._find_hash_entry(start_index, hash_name_a, hash_name_b, locale)

	def get_internal_listfiles(self): # type: () -> Listfiles
		# BN3 files have different internal listfile setup
		if self.internal_listfiles is None:
			self.internal_listfiles = Listfiles()
			self.internal_listfiles.add_listfile_list([MPQInternalFile.attributes, MPQInternalFile.listfile, MPQInternalFile.signature])
			crypt_key = MPQCrypt.hash_string(MPQInternalFile.listfile, MPQCrypt.HashType.key)
			hash_entries = self._find_hash_entries(MPQInternalFile.listfile)
			for hash_entry in hash_entries:
				filenames = self._read_file_by_hash_entry(hash_entry, crypt_key)
				if filenames:
					self.internal_listfiles.add_listfile_str(filenames)
		return self.internal_listfiles

	# `listfiles` will be combined with the internal listfile (if available) and listfiles set through `set_listfiles` (if available)
	def list_files(self, listfiles=None): # type: (Listfiles | None) -> list[MPQFileEntry]
		assert self.headerv1 is not None
		assert self.hash_table is not None
		assert self.block_table is not None
		listfile_hashes = {}
		listfile_hashes.update(self.get_internal_listfiles().filenames)
		if listfiles is not None:
			listfile_hashes.update(listfiles.filenames)
		if self.external_listfiles is not None:
			listfile_hashes.update(self.external_listfiles.filenames)

		file_entries = []
		for (index, hash_entry) in enumerate(self.hash_table):
			if (hash_entry.block_index & 0xFFFFFFFE) == 0xFFFFFFFE or hash_entry.block_index >= self.headerv1.block_table_entries:
				continue
			block_entry = self.block_table[hash_entry.block_index]
			if not block_entry.flags & MPQBlockFlag.exists:
				continue
			entry_filename = listfile_hashes.get((hash_entry.hash_name_a, hash_entry.hash_name_b))
			if entry_filename is None:
				entry_filename = '%s%08x' % (MPQFileEntry.UNKNOWN_PREFIX, index)
			file_entries.append(MPQFileEntry(entry_filename, hash_entry, block_entry))

		return file_entries

	def _read_file_by_block_entry(self, block_entry, crypt_key=None): # type: (MPQBlockEntry, int | None) -> bytes
		assert self.headerv1 is not None
		assert self.file_handle is not None
		assert self.mpq_offset is not None
		if not block_entry.flags & MPQBlockFlag.exists:
			raise PyMSError('Read', "File doesn't exist")
		if block_entry.file_size == 0:
			return b''

		if block_entry.flags & MPQBlockFlag.encrypted:
			if not crypt_key:
				raise PyMSError('Read', "Missing key for decrypting")
			if block_entry.flags & MPQBlockFlag.adjust_key:
				crypt_key = (crypt_key + block_entry.file_offset) ^ block_entry.file_size
		else:
			crypt_key = 0

		read_size = block_entry.file_size
		block_size = 512 << self.headerv1.sector_size_shift
		if block_entry.flags & MPQBlockFlag.single_unit:
			block_size = block_entry.file_size
		total_blocks = int(math.ceil(block_entry.file_size / float(block_size)))

		header_length = 0
		# If BN3 then adjust for header length value

		block_offsets = [] # type: list[int]
		if (block_entry.flags & MPQBlockFlag.imploded or block_entry.flags & MPQBlockFlag.compressed) and not block_entry.flags & MPQBlockFlag.single_unit:
			self.file_handle.seek(self.mpq_offset + block_entry.file_offset + header_length)
			block_offsets_data = self.file_handle.read((total_blocks + 1) * 4)
			if block_entry.flags & MPQBlockFlag.encrypted:
				assert crypt_key is not None
				block_offsets_data = MPQCrypt.decrypt(block_offsets_data, crypt_key - 1)
			block_offsets = list(int(o) for o in struct.unpack('<%dL' % (total_blocks + 1), block_offsets_data))
		else:
			for i in range(total_blocks):
				block_offsets.append(i * block_size)
			block_offsets.append(block_entry.compressed_size - header_length)

		print(block_offsets)
		file_data = b''
		for index in range(0, len(block_offsets)-1):
			raw_size = block_offsets[index+1] - block_offsets[index]
			sector_size = block_size
			# The last sector might be smaller than a full sector
			if sector_size > read_size:
				sector_size = read_size
			self.file_handle.seek(self.mpq_offset + block_entry.file_offset + block_offsets[index])
			block_data = self.file_handle.read(raw_size)
			if block_entry.flags & MPQBlockFlag.encrypted:
				assert crypt_key is not None
				block_data = MPQCrypt.decrypt(block_data, crypt_key + index)
			# Some sectors might not be compressed, only decompress if the raw size is smaller than the sector size
			if raw_size < sector_size:
				algorithm_ids = None
				if block_entry.flags & MPQBlockFlag.imploded:
					algorithm_ids = MPQComp.AlgorithmID.pkware
				elif block_entry.flags & MPQBlockFlag.compressed:
					algorithm_ids = block_data[0]
					block_data = block_data[1:]
				if algorithm_ids is not None:
					block_data = MPQComp.decompress(algorithm_ids, block_data)
			file_data += block_data
			read_size -= len(block_data)
		return file_data

	def _read_file_by_hash_entry(self, hash_entry, crypt_key=None):
		block_entry = self.block_table[hash_entry.block_index]
		return self._read_file_by_block_entry(block_entry, crypt_key)

	def find_file(self, filename, locale=MPQLocale.neutral):
		hash_entry = self._find_hash_entry_by_filename(filename, locale)
		if hash_entry is None:
			return None
		block_entry = self.block_table[hash_entry.block_index]
		return MPQFileEntry(filename, hash_entry, block_entry)

	def read_file(self, filename, locale=MPQLocale.neutral):
		crypt_key = MPQCrypt.hash_string(filename, MPQCrypt.HashType.key)
		hash_entry = self._find_hash_entry_by_filename(filename, locale)
		if hash_entry is None:
			raise PyMSError('Read', "No file with name '%s' exists" % filename)
		return self._read_file_by_hash_entry(hash_entry, crypt_key)
