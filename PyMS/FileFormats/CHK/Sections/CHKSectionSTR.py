
from ..CHKSection import CHKSection
from ..CHKRequirements import CHKRequirements

from ....Utilities.utils import pad

import struct

class CHKString:
	def __init__(self, sect, string_id, text, refs=1):
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
	
	def __init__(self, chk):
		CHKSection.__init__(self, chk)
		self.strings = {}
		self.open_ids = []
	
	def load_data(self, data):
		self.strings = {}
		self.open_ids = []
		string_id = 0
		count = struct.unpack('<H', data[:2])[0]
		for n in range(count):
			offset = struct.unpack('<H', data[2+n*2:4+n*2])[0]
			end = data.find('\0', offset, len(data))
			if end == -1:
				end = len(data)
			text = data[offset:end]
			string = self.lookup_string(text)
			if string:
				string.retain()
			else:
				string = CHKString(self, string_id, text)
			self.strings[string_id] = string
			string_id += 1
	
	def string_count(self):
		return len(self.strings)

	def highest_index(self):
		index = 0
		if self.strings:
			index = list(sorted(self.strings.keys()))[-1]
		return index

	def save_data(self):
		count = self.highest_index() + 1
		result = struct.pack('<H', count)
		strings = ''
		offset = 2+count*2
		for string_id in enumerate(count):
			result += struct.pack('<H', offset+len(strings))
			strings += self.get_string(string_id) or '' + '\0'
		return result + strings

	def string_exists(self, string_id):
		return string_id in self.strings

	def lookup_string(self, text):
		for string in self.strings.values():
			if string.text == text:
				return string
		return None

	def add_string(self, text):
		string = self.lookup_string(text)
		if string:
			string.retain()
		else:
			index = self.string_count()
			if self.open_ids:
				index = self.open_ids[0]
				del self.open_ids[0]
			string = CHKString(self, index, text)
			self.strings[index] = string
		return string

	def remove_text(self, text):
		string = self.lookup_string(text)
		if string:
			string.release()

	def remove_string(self, string_id):
		string = self.strings.get(string_id)
		if string:
			string.release()

	def get_string(self, string_id):
		return self.strings.get(string_id)

	def get_text(self, string_id, default=None):
		string = self.get_string(string_id)
		if string:
			return string.text
		return default

	def set_string(self, string_id, text):
		string = self.get_string(string_id)
		if string:
			if string.references == 1:
				string.text = text
			else:
				string = self.lookup_string(text)
		if not string:
			string = self.add_string(text)
		return string

	def delete_string(self, string_id):
		if string_id in self.strings:
			del self.strings[string_id]
	
	def decompile(self):
		result = '%s:\n' % (self.NAME)
		for n,string in self.strings.iteritems():
			result += '\t%s"%s"\n' % (pad('String %d' % (n+1)), string.text.replace('\\','\\\\').replace('"','\\"'))
		return result
