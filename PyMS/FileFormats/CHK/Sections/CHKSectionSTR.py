
from ..CHKSection import CHKSection
from ..CHKRequirements import CHKRequirements

from ....Utilities.utils import pad

import struct

from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from ..CHK import CHK

class CHKString(object):
	def __init__(self, sect, string_id, text, refs=1): # type: (CHKSectionSTR, int, str, int) -> None
		self.sect = sect
		self.string_id = string_id
		self.text = text
		self.references = refs

	def retain(self):
		self.references += 1

	def release(self):
		self.references -= 1
		if self.references == 0:
			self.sect.delete_string(self.string_id)

class CHKSectionSTR(CHKSection):
	NAME = 'STR '
	REQUIREMENTS = CHKRequirements(CHKRequirements.VER_ALL, CHKRequirements.MODE_ALL)
	
	def __init__(self, chk): # type: (CHK) -> None
		CHKSection.__init__(self, chk)
		self.strings = {} # type: dict[int, CHKString]
		self.open_ids = [] # type: list[int]
	
	def load_data(self, data): # type: (bytes) -> None
		self.strings = {}
		self.open_ids = []
		string_id = 0
		count = int(struct.unpack('<H', data[:2])[0])
		for n in range(count):
			offset = int(struct.unpack('<H', data[2+n*2:4+n*2])[0])
			end = data.find(b'\0', offset, len(data))
			if end == -1:
				end = len(data)
			text = data[offset:end].decode('utf-8')
			# string = self.lookup_string(text)
			# if string:
			# 	string.retain()
			# else:
			string = CHKString(self, string_id, text)
			self.strings[string_id] = string
			string_id += 1
	
	def string_count(self): # type: () -> int
		return len(self.strings)

	def highest_index(self): # type: () -> int
		index = 0
		if self.strings:
			index = list(sorted(self.strings.keys()))[-1]
		return index

	def save_data(self): # type: () -> bytes
		count = self.highest_index() + 1
		header = struct.pack('<H', count)
		strings = b''
		offset = 2+count*2
		for string_id in range(count):
			string = self.get_string(string_id)
			if not string:
				continue
			header += struct.pack('<H', offset+len(strings))
			strings += string.text.encode('utf-8') or b'' + b'\0'
		return header + strings

	def string_exists(self, string_id): # type: (int) -> bool
		return string_id in self.strings

	def lookup_string(self, text): # type: (str) -> (CHKString | None)
		for string in list(self.strings.values()):
			if string.text == text:
				return string
		return None

	def add_string(self, text, reuse=True): # type: (str, bool) -> CHKString
		if reuse:
			string = self.lookup_string(text)
			if string:
				string.retain()
				return string
		index = self.string_count()
		if self.open_ids:
			index = self.open_ids[0]
			del self.open_ids[0]
		string = CHKString(self, index, text)
		self.strings[index] = string
		return string

	def remove_text(self, text): # type: (str) -> None
		string = self.lookup_string(text)
		if string:
			string.release()

	def remove_string(self, string_id): # type: (int) -> None
		string = self.strings.get(string_id)
		if string:
			string.release()

	def get_string(self, string_id): # type: (int) -> (CHKString | None)
		return self.strings.get(string_id)

	def get_text(self, string_id, default=None): # type: (int, str | None) -> (str | None)
		string = self.get_string(string_id)
		if string:
			return string.text
		return default

	def set_string(self, string_id, text): # type: (int, str) -> CHKString
		string = self.get_string(string_id)
		if string:
			if string.references == 1:
				string.text = text
			else:
				string = self.lookup_string(text)
		if not string:
			string = self.add_string(text)
		return string

	def delete_string(self, string_id): # type: (int) -> None
		if string_id in self.strings:
			del self.strings[string_id]
	
	def decompile(self): # type: () -> str
		result = '%s:\n' % (self.NAME)
		for n,string in self.strings.items():
			result += '\t%s"%s"\n' % (pad('String %d' % (n+1)), string.text.replace('\\','\\\\').replace('"','\\"'))
		return result
