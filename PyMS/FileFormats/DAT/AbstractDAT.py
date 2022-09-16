
from .DATCoders import DATPropertyCoder

from ...Utilities.fileutils import load_file
from ...Utilities.PyMSError import PyMSError
from ...Utilities.AtomicWriter import AtomicWriter

from math import ceil
from collections import OrderedDict
from copy import deepcopy
import json, re

class ExportType:
	text = 'text'
	json = 'json'

# Abstract class for DAT files
class AbstractDAT(object):
	# File format
	FORMAT = None
	# Struct object for entries
	ENTRY_STRUCT = lambda: None
	# Default filename for DAT file
	FILE_NAME = None

	def __init__(self):
		self.entries = []

	def new_file(self, entry_count=None):
		entry_count = max(entry_count or 0, self.FORMAT.entries)
		if entry_count != self.FORMAT.entries:
			entry_count = self.expanded_count(entry_count)
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

	def get_entry(self, index): # type: (int) -> AbstractDATEntry
		return self.entries[index]

	def set_entry(self, index, entry):
		self.entries[index] = entry

	def is_expanded(self):
		return self.entry_count() > self.FORMAT.entries

	def expanded_count(self, count):
		resulting_entry_count = count
		if not self.is_expanded() and self.FORMAT.expanded_min_entries and resulting_entry_count < self.FORMAT.expanded_min_entries:
			resulting_entry_count = self.FORMAT.expanded_min_entries
		if self.FORMAT.expanded_entries_multiple:
			resulting_entry_count = int(ceil(resulting_entry_count / float(self.FORMAT.expanded_entries_multiple)) * self.FORMAT.expanded_entries_multiple)
		return resulting_entry_count

	def can_expand(self, add=1):
		resulting_entry_count = self.expanded_count(self.entry_count() + add)
		if self.FORMAT.expanded_max_entries and resulting_entry_count > self.FORMAT.expanded_max_entries:
			return False
		return True

	def expand_entries(self, add=1):
		if not self.is_expanded():
			for entry in self.entries:
				entry.expand()
		resulting_entry_count = self.expanded_count(self.entry_count() + add)
		while self.entry_count() < resulting_entry_count:
			self.entries.append(self.ENTRY_STRUCT())
		return True

	re_comment = re.compile(r'\s*#.+')
	re_entry_header = re.compile(r'^\s*(\w+)\((\d+)?\):\s*$')
	re_property = re.compile(r'^\s*(\w+)(?:\.(\w+))?\s+(\d+|True|False)\s*$')
	@classmethod
	def parse_text(self, text):
		entries = []
		entry_starts = {}
		entry = None
		def check_entry():
			if entry == None:
				return
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
				id = int(id)
				if id in entry_starts:
					raise PyMSError('Import', 'Entry %d already exists' % id, line=n, code=line)
				entry = {'_type': name, '_id': id}
				entry_starts[id] = n
				continue
			match = self.re_property.match(line)
			if match:
				if entry == None:
					raise PyMSError('Import', "Missing header before defining properties", line=n, code=line)
				name,subproperty,value = match.groups()
				if value == 'True':
					value = True
				elif value == 'False':
					value = False
				else:
					value = int(value)
				# TODO: Validate property, subproperty, value?
				if subproperty != None:
					subobject = entry.get(name, {})
					if not name in entry:
						entry[name] = subobject
					subobject[subproperty] = value
				else:
					entry[name] = value
				continue
			raise PyMSError('Import', "Unexpected line, expected a header or a property definition", line=n, code=line)
		check_entry()
		if not entries:
			raise PyMSError('Import', 'No entries found')
		return entries

	def export_file(self, file_path):
		try:
			file = AtomicWriter(file_path, 'wb')
		except:
			raise PyMSError("Decompile", "Could not create file for writing")
		data = self.export_entries()
		file.write(data)
		file.close()

	def export_entries(self, ids=None, export_properties=None, export_type=ExportType.text, json_dump=False, json_indent=4):
		if not ids:
			ids = range(self.entry_count())
		data = []
		for id in ids:
			if id < 0 or id >= self.entry_count():
				raise PyMSError('Export', "Invalid entry id (must be between 0 and %d, got %d)" % (self.entry_count(), id))
			data.append(self.get_entry(id).export_data(id, export_properties))
		return self._export(data, export_type, json_dump, json_indent)

	# Export some or all `export_properties` (`None` or emptry array for all properties, or an array of property names for a subset) to the specified format
	def export_entry(self, id, export_properties=None, export_type=ExportType.text, json_dump=False, json_indent=4):
		data = self.get_entry(id).export_data(id, export_properties)
		return self._export(data, export_type, json_dump, json_indent)

	def _export(self, data, export_type=ExportType.text, json_dump=True, json_indent=4):
		if export_type == ExportType.text:
			if not isinstance(data, list):
				data = [data]
			def flatten(fields, breadcrumbs, lines): # type: (OrderedDict[str, Any], tuple[str], list[str]) -> None
				for key, value in fields.items():
					if key.startswith('_'):
						continue
					if isinstance(value, OrderedDict):
						flatten(value, breadcrumbs + (key,), lines)
					else:
						name = '.'.join(breadcrumbs + (key,))
						lines.append('\t%s %s' % (name, value))
			lines = []
			for entry in data:
				lines.append('%s%s:' % (entry['_type'], '(%d)' % entry['_id'] if '_id' in entry else ''))
				flatten(entry, (), lines)
				lines.append('')
			return '\n'.join(lines)
		elif export_type == ExportType.json:
			if json_dump:
				return json.dumps(data, indent=json_indent)
			return data

	def import_file(self, file_path):
		data = load_file(file_path)
		self.import_entries(data)

	def import_entries(self, data, export_type=ExportType.text):
		if export_type == ExportType.text:
			data = AbstractDAT.parse_text(data)
		backup = deepcopy(self.entries)
		try:
			for entry in data:
				id = entry.get('_id')
				if id == None:
					raise PyMSError('Import', 'Entry missing id')
				if id >= self.entry_count():
					raise PyMSError('Export', "Invalid entry id (must be between 0 and %d, got %d)" % (self.entry_count(), id))
				self.get_entry(id).import_data(entry)
		except:
			self.entries = backup
			raise

	def import_entry(self, id, data, export_type=ExportType.text):
		if export_type == ExportType.text:
			data_entries = AbstractDAT.parse_text(data)
			if len(data_entries) != 1:
				raise PyMSError('Import', 'Too many entries to import (expected 1, got %d)' % len(data_entries))
			data = data_entries[0]
		return self.get_entry(id).import_data(data)

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
	def export_data(self, id=None, export_properties=None):
		data = OrderedDict()
		data["_type"] = self.EXPORT_NAME
		if id != None:
			data["_id"] = id
		self._export_data(export_properties, data)
		return data
	
	def _export_data(self, export_properties, data): # type: (list[str], OrderedDict[str, Any]) -> None
		pass

	def import_data(self, data): # type: (dict[str, Any]) -> None
		type_name = data.get('_type')
		if type_name != self.EXPORT_NAME:
			raise PyMSError('Import', "Invalid type (expected '%s', got '%s')" % (self.EXPORT_NAME, type_name))
		self._import_data(data)
		for key in data.keys():
			if key.startswith('_'):
				continue
			raise PyMSError('Import', "Unrecognized property '%s'" % key)

	def _import_data(self, data):
		pass

	def _export_property_value(self, export_properties, prop, value, data, property_encoder=None): # type: (list[str], str, Any, Any, DATPropertyCoder) -> None
		if value == None or (export_properties and not prop in export_properties):
			return
		if property_encoder:
			value = property_encoder.encode(value)
		data[prop] = value

	def _import_property_value(self, data, prop, property_coder=None, allowed=True): # type: (dict[str, Any], str, Any, DATPropertyCoder) -> Any
		if not prop in data:
			return None
		elif not allowed:
			return None
		value = data[prop]
		del data[prop]
		if property_coder:
			value = property_coder.decode(value)
		return value
