
from ...Utilities.fileutils import load_file
from ...Utilities.PyMSError import PyMSError
from ...Utilities.AtomicWriter import AtomicWriter

from math import ceil

# Abstract class for DAT files
class AbstractDAT(object):
	# File format
	FORMAT = None
	# Struct object for entries
	ENTRY_STRUCT = None
	# Default filename for DAT file
	FILE_NAME = None

	def __init__(self):
		self.entries = []

	def load_file(self, file):
		data = load_file(file, self.FILE_NAME)
		try:
			self.load_data(data)
		except PyMSError:
			raise
		except:
			raise PyMSError("Load", "Invalid %s (error parsing file)" % self.FILE_NAME, capture_exception=True)

	def load_data(self, data):
		data_size = len(data)
		entry_info = self.FORMAT.check_file_size(data_size)
		if not entry_info:
			expected_data_size = self.FORMAT.file_size()
			raise PyMSError("Load", "Invalid %s (the file size must be %d, but got %d)" % (self.FILE_NAME, expected_data_size, data_size))
		entry_count,is_expanded = entry_info
		offset = 0
		properties = []
		for prop in self.FORMAT.properties:
			total_size,prop_data = prop.load_data(data, offset, entry_count, is_expanded)
			properties.append(prop_data)
			offset += total_size

		entries = []
		for values in zip(*properties):
			entry = self.ENTRY_STRUCT()
			entry.load_values(values)
			entries.append(entry)

		self.entries = entries

	def save_file(self, file_path):
		try:
			file = AtomicWriter(file_path, 'wb')
		except:
			raise PyMSError("Save", "Could not create file for writing")
		data = self.save_data()
		file.write(data)
		file.close()

	def save_data(self):
		entry_count = self.entry_count()
		is_expanded = entry_count > self.FORMAT.entries
		all_values = zip(*(entry.save_values() for entry in self.entries))
		data = ''.join(prop.save_data(values, is_expanded) for prop,values in zip(self.FORMAT.properties, all_values))
		data_size = len(data)
		expected_data_size = self.FORMAT.file_size(expanded_entry_count=entry_count if is_expanded else None)
		if data_size != expected_data_size:
			raise PyMSError("Save", "Save produced invalid size (expected %d, but got %d" % (expected_data_size, data_size))
		return data

	def entry_count(self):
		return len(self.entries)

	def get_entry(self, index):
		return self.entries[index]

	def set_entry(self, index, entry):
		self.entries[index] = entry

	def is_expanded(self):
		return self.entry_count() > self.FORMAT.entries

	def _expand_count(self, count=1):
		resulting_entry_count = self.entry_count()
		if not self.is_expanded() and self.FORMAT.expanded_min_entries:
			resulting_entry_count = self.FORMAT.expanded_min_entries
		resulting_entry_count += count
		if self.FORMAT.expanded_entries_multiple:
			resulting_entry_count = ceil(resulting_entry_count / float(self.FORMAT.expanded_entries_multiple)) * self.FORMAT.expanded_entries_multiple
		return resulting_entry_count

	def can_expand(self, count=1):
		resulting_entry_count = self._expand_count(count)
		if self.FORMAT.expanded_max_entries and resulting_entry_count > self.FORMAT.expanded_max_entries:
			return False
		return True

	def expand_entries(self, count=1):
		if not self.is_expanded():
			for entry in self.entries:
				entry.expand()
		resulting_entry_count = self._expand_count(count)
		while self.entry_count() < resulting_entry_count:
			self.entries.append(self.ENTRY_STRUCT())
		return True

class AbstractDATEntry(object):
	def load_values(self, values):
		pass

	def save_values(self):
		pass

	# Ensure entry has all properties enabled (not set to `None`)
	def expand(self):
		pass

	def export_text(self, id):
		pass

	def import_text(self, text):
		pass

	def export_json(self, id, dump=True, indent=4):
		pass

	def import_json(self, json):
		pass
