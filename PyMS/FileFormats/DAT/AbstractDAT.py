
from ...Utilities.fileutils import load_file
from ...Utilities.PyMSError import PyMSError
from ...Utilities.AtomicWriter import AtomicWriter

from math import ceil
from collections import OrderedDict
import json, re

class ExportType:
	text = 'text'
	json = 'json'

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

	def new_file(self, entry_count=None):
		entry_count = max(entry_count or 0, self.FORMAT.entries)
		if entry_count != self.FORMAT.entries:
			entry_count = self._expanded_count(entry_count)
		self.entries = list(self.ENTRY_STRUCT() for _ in range(entry_count))
		if not self.is_expanded():
			for id,entry in enumerate(self.entries):
				entry.limit(id)

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

	def _expanded_count(self, count):
		resulting_entry_count = count
		if not self.is_expanded() and self.FORMAT.expanded_min_entries:
			resulting_entry_count = self.FORMAT.expanded_min_entries
		if self.FORMAT.expanded_entries_multiple:
			resulting_entry_count = int(ceil(resulting_entry_count / float(self.FORMAT.expanded_entries_multiple)) * self.FORMAT.expanded_entries_multiple)
		return resulting_entry_count

	def can_expand(self, add=1):
		resulting_entry_count = self._expanded_count(self.entry_count() + add)
		if self.FORMAT.expanded_max_entries and resulting_entry_count > self.FORMAT.expanded_max_entries:
			return False
		return True

	def expand_entries(self, add=1):
		if not self.is_expanded():
			for entry in self.entries:
				entry.expand()
		resulting_entry_count = self._expanded_count(self.entry_count() + add)
		while self.entry_count() < resulting_entry_count:
			self.entries.append(self.ENTRY_STRUCT())
		return True

	re_comment = re.compile(r'\s*#.+')
	re_entry_header = re.compile(r'^\s*(\w+)\((\d+)?\):\s*$')
	re_property = re.compile(r'^\s*(\w+)(?:\.(\w+))?\s+(\d+)$')
	@classmethod
	def parse_text(self, entry_type, text):
		entry_name = entry_type.EXPORT_NAME
		entries = []
		entry_starts = {}
		entry = None
		def check_entry():
			if entry != None:
				if len(entry) < 3:
					raise PyMSError('Import', 'Entry %d is empty' % entry['_id'], line=entry_starts[entry['_id']])
				entries.append(entry)
		for n,line in enumerate(text.splitlines()):
			line = self.re_comment.sub('', line)
			if not line:
				continue
			match = self.re_entry_header.match(line)
			if match:
				check_entry()
				name,id = match.groups()
				if name != entry_name:
					raise PyMSError('Import', "Entry type is incorrect (expected '%s' but got '%s')" % (entry_name, name), line=n, code=line)
				if id in entry_starts:
					raise PyMSError('Import', 'Entry %d already exists' % id, line=n, code=line)
				entry = {'_type': name, '_id': id}
				entry_starts[id] = n
				continue
			match = self.re_property.match(line)
			if match:
				if entry == None:
					raise PyMSError('Import', "Missing '%s' header before defining properties" % entry_name, line=n, code=line)
				name,subproperty,value = match.groups()
				# TODO: Validate property, subproperty, value?
				if subproperty != None:
					subobject = entry.get(name, {})
					if not name in entry:
						entry[name] = subobject
					subobject[subproperty] = value
				else:
					entry[name] = value
				continue
			raise PyMSError('Import', "Unexpected line, expected a '%s' header or a property" % entry_name, line=n, code=line)
		check_entry()
		if not entries:
			raise PyMSError('Import', 'No entries found')
		print entries

	def export_entry(self, id, export_properties=None, export_type=ExportType.text, json_dump=True, json_indent=4):
		return self.get_entry(id).export(id, export_properties, export_type, json_dump, json_indent)

class AbstractDATEntry(object):
	EXPORT_NAME = None

	def load_values(self, values):
		pass

	def save_values(self):
		pass

	# Ensure entry has limited properties unavailable (set to `None`)
	def limit(self, id):
		pass

	# Ensure entry has limited properties available (not set to `None`)
	def expand(self):
		pass

	# Export some or all `export_properties` (`None` or emptry array for all properties, or an array of property names for a subset) to the specified format
	def export(self, id, export_properties=None, export_type=ExportType.text, json_dump=True, json_indent=4):
		if export_type == ExportType.text:
			data = []
			data.append("%s(%d):" % (self.EXPORT_NAME, id))
		elif export_type == ExportType.json:
			data = OrderedDict()
			data["_type"] = self.EXPORT_NAME
			data["_id"] = id
		else:
			raise PyMSError('Export', "Invalid export type '%s'" % export_type)
		self._export(export_properties, export_type, data)
		if export_type == ExportType.text:
			return '\n\t'.join(data)
		elif export_type == ExportType.json:
			if json_dump:
				return json.dumps(data, indent=json_indent)
			return data
	
	def _export(self, export_properties, export_type, data):
		pass

	def import_text(self, text):
		json = AbstractDAT.parse_text(type(self), text)

	def import_json(self, json):
		pass

	def _export_property_value(self, export_properties, prop, value, export_type, data):
		if (not export_properties or prop in export_properties) and value != None:
			if export_type == ExportType.text:
				data.append("%s %s" % (prop, value))
			elif export_type == ExportType.json:
				data[prop] = value

	# `values_lambda` is called with `obj` (if not None), and returns an iterable of tuples in the format `(field, value)`
	def _export_property_values(self, export_properties, prop, obj, values_lambda, export_type, data):
		if (not export_properties or prop in export_properties) and obj != None:
			if export_type == ExportType.text:
				for field,value in values_lambda(obj):
					if value != None:
						data.append("%s.%s %s" % (prop, field, value))
			elif export_type == ExportType.json:
				sub_data = OrderedDict()
				for field,value in values_lambda(obj):
					if value != None:
						sub_data[field] = value
				if sub_data:
					data[prop] = sub_data
