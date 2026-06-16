
from ...FileFormats import DAT
from ...FileFormats.DAT.AbstractDAT import AbstractDAT, ExportType
from ...Utilities.PyMSError import PyMSError
from ...Utilities import IO

from ..utils import resource_path

import json
import unittest

from typing import Any, cast

# Every concrete DAT file format paired (by `FILE_NAME`) with its committed binary fixture.
ALL_DAT_CLASSES: list[type[AbstractDAT]] = [
	DAT.UnitsDAT,
	DAT.WeaponsDAT,
	DAT.FlingyDAT,
	DAT.SpritesDAT,
	DAT.ImagesDAT,
	DAT.UpgradesDAT,
	DAT.TechDAT,
	DAT.SoundsDAT,
	DAT.PortraitsDAT,
	DAT.CampaignDAT,
	DAT.OrdersDAT,
]


def _fixture(cls: type[AbstractDAT]) -> bytes:
	with open(resource_path(cls.FILE_NAME, __file__), 'rb') as f:
		return f.read()


def _loaded(cls: type[AbstractDAT]) -> AbstractDAT:
	dat = cls()
	dat.load(_fixture(cls))
	return dat


# A small, self-contained text document for the simplest format (all integer properties).
def _flingy_text(entry_id: int = 0, sprite: int = 7) -> str:
	return (
		f'Flingy({entry_id}):\n'
		f'\tsprite {sprite}\n'
		'\tspeed 0\n'
		'\tacceleration 0\n'
		'\thalt_distance 0\n'
		'\tturn_radius 0\n'
		'\tiscript_mask 0\n'
		'\tmovement_control 0\n'
	)


class Test_RoundTrip(unittest.TestCase):
	# The core invariant: a real game file survives export -> import unchanged, byte for byte,
	# for every format and every serialization path.

	def test_text_round_trip_is_byte_identical(self) -> None:
		for cls in ALL_DAT_CLASSES:
			with self.subTest(format=cls.FILE_NAME):
				original = _fixture(cls)
				text = _loaded(cls).export_entries(export_type=ExportType.text)
				self.assertIsInstance(text, str)
				dest = cls()
				dest.new_file()
				dest.import_entries(cast(str, text))
				self.assertEqual(IO.output_to_bytes(dest.save), original)

	def test_json_object_round_trip_is_byte_identical(self) -> None:
		# Import the exported in-memory objects directly (json_dump=False).
		for cls in ALL_DAT_CLASSES:
			with self.subTest(format=cls.FILE_NAME):
				original = _fixture(cls)
				data = _loaded(cls).export_entries(export_type=ExportType.json)
				self.assertIsInstance(data, list)
				dest = cls()
				dest.new_file()
				dest.import_entries(cast(list, data), ExportType.json)
				self.assertEqual(IO.output_to_bytes(dest.save), original)

	def test_json_string_round_trip_is_byte_identical(self) -> None:
		# json_dump=True serializes to a string; reparse via json.loads as an external consumer would.
		for cls in ALL_DAT_CLASSES:
			with self.subTest(format=cls.FILE_NAME):
				original = _fixture(cls)
				dumped = _loaded(cls).export_entries(export_type=ExportType.json, json_dump=True)
				self.assertIsInstance(dumped, str)
				data = json.loads(cast(str, dumped))
				dest = cls()
				dest.new_file()
				dest.import_entries(data, ExportType.json)
				self.assertEqual(IO.output_to_bytes(dest.save), original)

	def test_export_file_import_file_round_trip_is_byte_identical(self) -> None:
		# export_file/import_file are the file-level entry points the PyDAT GUI/CLI use.
		for cls in ALL_DAT_CLASSES:
			with self.subTest(format=cls.FILE_NAME):
				original = _fixture(cls)
				text = IO.output_to_text(_loaded(cls).export_file)
				dest = cls()
				dest.new_file()
				dest.import_file(text)
				self.assertEqual(IO.output_to_bytes(dest.save), original)

	def test_export_entry_import_entry_text_round_trip(self) -> None:
		# Single-entry text export/import (the path PyDAT's per-entry GUI buttons use).
		for cls in ALL_DAT_CLASSES:
			with self.subTest(format=cls.FILE_NAME):
				source = _loaded(cls)
				dest = cls()
				dest.new_file()
				for entry_id in (0, source.entry_count() // 2, source.entry_count() - 1):
					text = source.export_entry(entry_id)
					self.assertIsInstance(text, str)
					dest.import_entry(entry_id, cast(str, text))
					# Compare via the text export: save_values() holds rich DATType objects without __eq__.
					self.assertEqual(dest.export_entry(entry_id), source.export_entry(entry_id))

	def test_export_file_text_matches_export_entries_text(self) -> None:
		for cls in ALL_DAT_CLASSES:
			with self.subTest(format=cls.FILE_NAME):
				dat = _loaded(cls)
				self.assertEqual(IO.output_to_text(dat.export_file), dat.export_entries(export_type=ExportType.text))


class Test_ExportEntries(unittest.TestCase):
	def setUp(self) -> None:
		self.dat = cast(DAT.FlingyDAT, _loaded(DAT.FlingyDAT))

	def test_export_all_entries_text_has_a_header_per_entry(self) -> None:
		text = self.dat.export_entries(export_type=ExportType.text)
		self.assertIsInstance(text, str)
		assert isinstance(text, str)
		self.assertEqual(text.count('Flingy('), self.dat.entry_count())
		self.assertIn('Flingy(0):', text)

	def test_export_specific_entries_text_only_includes_requested_ids(self) -> None:
		text = self.dat.export_entries([2, 5], export_type=ExportType.text)
		assert isinstance(text, str)
		self.assertIn('Flingy(2):', text)
		self.assertIn('Flingy(5):', text)
		self.assertEqual(text.count('Flingy('), 2)

	def test_export_entries_json_returns_list_of_dicts(self) -> None:
		data = self.dat.export_entries([0, 1], export_type=ExportType.json)
		assert isinstance(data, list)
		self.assertEqual(len(data), 2)
		self.assertEqual(data[0]['_type'], 'Flingy')
		self.assertEqual(data[0]['_id'], 0)
		self.assertEqual(data[1]['_id'], 1)

	def test_export_entries_json_dump_returns_parseable_string(self) -> None:
		dumped = self.dat.export_entries([0], export_type=ExportType.json, json_dump=True)
		assert isinstance(dumped, str)
		parsed = json.loads(dumped)
		self.assertEqual(parsed[0]['_type'], 'Flingy')

	def test_export_properties_subset_limits_exported_fields(self) -> None:
		text = self.dat.export_entries([0], export_properties=['sprite', 'speed'], export_type=ExportType.text)
		assert isinstance(text, str)
		self.assertIn('\tsprite ', text)
		self.assertIn('\tspeed ', text)
		self.assertNotIn('acceleration', text)
		self.assertNotIn('movement_control', text)

	def test_export_entries_negative_id_raises(self) -> None:
		with self.assertRaises(PyMSError):
			self.dat.export_entries([-1])

	def test_export_entries_id_past_end_raises(self) -> None:
		with self.assertRaises(PyMSError):
			self.dat.export_entries([self.dat.entry_count()])

	def test_export_invalid_export_type_raises(self) -> None:
		with self.assertRaises(PyMSError):
			self.dat.export_entries([0], export_type=cast(Any, 'not-a-type'))


class Test_ExportEntry(unittest.TestCase):
	def setUp(self) -> None:
		self.dat = cast(DAT.FlingyDAT, _loaded(DAT.FlingyDAT))

	def test_export_entry_text_is_string_with_header(self) -> None:
		text = self.dat.export_entry(3)
		self.assertIsInstance(text, str)
		self.assertIn('Flingy(3):', cast(str, text))

	def test_export_entry_json_is_single_dict(self) -> None:
		data = self.dat.export_entry(3, export_type=ExportType.json)
		self.assertNotIsInstance(data, list)
		assert isinstance(data, dict)
		self.assertEqual(data['_type'], 'Flingy')
		self.assertEqual(data['_id'], 3)

	def test_export_entry_json_dump_returns_string(self) -> None:
		dumped = self.dat.export_entry(3, export_type=ExportType.json, json_dump=True)
		self.assertIsInstance(dumped, str)
		self.assertEqual(json.loads(cast(str, dumped))['_id'], 3)


class Test_TextFormatting(unittest.TestCase):
	# Units exercises the richest text output: integer fields, flag sub-objects, and
	# position/size/extents sub-objects rendered as `name.subproperty` lines.
	def setUp(self) -> None:
		self.dat = cast(DAT.UnitsDAT, _loaded(DAT.UnitsDAT))

	def test_subproperties_render_as_dotted_names(self) -> None:
		text = self.dat.export_entry(0)
		assert isinstance(text, str)
		self.assertIn('\tstaredit_placement_size.width ', text)
		self.assertIn('\tstaredit_placement_size.height ', text)
		self.assertIn('\tunit_extents.left ', text)

	def test_flag_subproperties_render_as_booleans(self) -> None:
		text = self.dat.export_entry(0)
		assert isinstance(text, str)
		self.assertRegex(text, r'\tspecial_ability_flags\.\w+ (True|False)')

	def test_partial_property_absent_when_out_of_range(self) -> None:
		# `addon_position` only exists for a sub-range of unit ids; it must not be exported for unit 0.
		text = self.dat.export_entry(0)
		assert isinstance(text, str)
		self.assertNotIn('addon_position', text)


class Test_ParseText(unittest.TestCase):
	def test_parses_header_and_properties(self) -> None:
		entries = AbstractDAT.parse_text(_flingy_text(0, sprite=12))
		self.assertEqual(len(entries), 1)
		self.assertEqual(entries[0]['_type'], 'Flingy')
		self.assertEqual(entries[0]['_id'], 0)
		self.assertEqual(entries[0]['sprite'], 12)

	def test_strips_full_line_and_trailing_comments(self) -> None:
		text = (
			'# leading comment\n'
			'Flingy(0):\n'
			'\tsprite 5 # trailing comment\n'
			'\tspeed 0\n'
		)
		entries = AbstractDAT.parse_text(text)
		self.assertEqual(entries[0]['sprite'], 5)
		self.assertEqual(entries[0]['speed'], 0)

	def test_parses_subproperties_into_nested_dict(self) -> None:
		text = (
			'Unit(0):\n'
			'\taddon_position.x 3\n'
			'\taddon_position.y 4\n'
		)
		entries = AbstractDAT.parse_text(text)
		self.assertEqual(entries[0]['addon_position'], {'x': 3, 'y': 4})

	def test_parses_boolean_and_integer_values(self) -> None:
		text = (
			'Unit(0):\n'
			'\tflag_a True\n'
			'\tflag_b False\n'
			'\tcount 42\n'
		)
		entries = AbstractDAT.parse_text(text)
		self.assertIs(entries[0]['flag_a'], True)
		self.assertIs(entries[0]['flag_b'], False)
		self.assertEqual(entries[0]['count'], 42)

	def test_duplicate_entry_id_raises(self) -> None:
		text = 'Flingy(0):\n\tsprite 1\nFlingy(0):\n\tsprite 2\n'
		with self.assertRaises(PyMSError):
			AbstractDAT.parse_text(text)

	def test_property_before_header_raises(self) -> None:
		with self.assertRaises(PyMSError):
			AbstractDAT.parse_text('\tsprite 5\n')

	def test_empty_entry_raises(self) -> None:
		# A header immediately followed by another header has no properties.
		text = 'Flingy(0):\nFlingy(1):\n\tsprite 1\n'
		with self.assertRaises(PyMSError):
			AbstractDAT.parse_text(text)

	def test_unexpected_line_raises(self) -> None:
		text = 'Flingy(0):\n\tsprite 1\nthis is not valid\n'
		with self.assertRaises(PyMSError):
			AbstractDAT.parse_text(text)

	def test_no_entries_raises(self) -> None:
		with self.assertRaises(PyMSError):
			AbstractDAT.parse_text('# only a comment\n\n')

	def test_header_without_id_raises_cleanly(self) -> None:
		# A header must carry an id (imports key off `_id`); a missing id is a reportable
		# input error, not an internal crash.
		with self.assertRaises(PyMSError):
			AbstractDAT.parse_text('Flingy():\n\tsprite 1\n')


class Test_ImportEntries(unittest.TestCase):
	def setUp(self) -> None:
		self.dat = DAT.FlingyDAT()
		self.dat.new_file()

	def test_import_text_applies_values(self) -> None:
		self.dat.import_entries(_flingy_text(1, sprite=99))
		self.assertEqual(self.dat.get_entry(1).sprite, 99)

	def test_import_json_list_applies_values(self) -> None:
		self.dat.import_entries([{'_type': 'Flingy', '_id': 1, 'sprite': 77}], ExportType.json)
		self.assertEqual(self.dat.get_entry(1).sprite, 77)

	def test_import_text_with_non_string_raises(self) -> None:
		with self.assertRaises(PyMSError):
			self.dat.import_entries(cast(Any, [{'_type': 'Flingy', '_id': 0}]), ExportType.text)

	def test_import_json_with_non_list_raises(self) -> None:
		with self.assertRaises(PyMSError):
			self.dat.import_entries(cast(Any, 'not a list'), ExportType.json)

	def test_import_invalid_type_raises(self) -> None:
		with self.assertRaises(PyMSError):
			self.dat.import_entries('whatever', cast(Any, 'bogus'))

	def test_import_entry_missing_id_raises(self) -> None:
		with self.assertRaises(PyMSError):
			self.dat.import_entries([{'_type': 'Flingy', 'sprite': 1}], ExportType.json)

	def test_import_entry_id_out_of_range_raises(self) -> None:
		with self.assertRaises(PyMSError):
			self.dat.import_entries([{'_type': 'Flingy', '_id': self.dat.entry_count(), 'sprite': 1}], ExportType.json)

	def test_failed_import_rolls_back_all_changes(self) -> None:
		original_sprite = self.dat.get_entry(0).sprite
		entries = [
			{'_type': 'Flingy', '_id': 0, 'sprite': original_sprite + 123},
			{'_type': 'Flingy', '_id': 1, 'unrecognized_property': 1},
		]
		with self.assertRaises(PyMSError):
			self.dat.import_entries(entries, ExportType.json)
		# The first entry's change must be undone even though it was applied before the second failed.
		self.assertEqual(self.dat.get_entry(0).sprite, original_sprite)


class Test_ImportEntry(unittest.TestCase):
	def setUp(self) -> None:
		self.dat = DAT.FlingyDAT()
		self.dat.new_file()

	def test_import_entry_text_applies_values(self) -> None:
		self.dat.import_entry(2, _flingy_text(2, sprite=55))
		self.assertEqual(self.dat.get_entry(2).sprite, 55)

	def test_import_entry_text_with_multiple_entries_raises(self) -> None:
		text = _flingy_text(0) + _flingy_text(1)
		with self.assertRaises(PyMSError):
			self.dat.import_entry(0, text)

	def test_import_entry_text_with_non_string_raises(self) -> None:
		with self.assertRaises(PyMSError):
			self.dat.import_entry(0, cast(Any, {'_type': 'Flingy', '_id': 0}))

	def test_import_entry_json_object_applies_values(self) -> None:
		self.dat.import_entry(2, {'_type': 'Flingy', '_id': 2, 'sprite': 88}, ExportType.json)
		self.assertEqual(self.dat.get_entry(2).sprite, 88)

	def test_import_entry_json_with_non_object_raises(self) -> None:
		with self.assertRaises(PyMSError):
			self.dat.import_entry(0, cast(Any, [{'_type': 'Flingy', '_id': 0}]), ExportType.json)

	def test_export_entry_import_entry_json_round_trip(self) -> None:
		# Single-entry JSON export must be re-importable, mirroring the text path.
		for cls in ALL_DAT_CLASSES:
			with self.subTest(format=cls.FILE_NAME):
				source = _loaded(cls)
				data = source.export_entry(0, export_type=ExportType.json)
				dest = cls()
				dest.new_file()
				dest.import_entry(0, cast(Any, data), ExportType.json)
				self.assertEqual(dest.export_entry(0), source.export_entry(0))


class Test_ImportData(unittest.TestCase):
	# Entry-level import validation (AbstractDATEntry.import_data).
	def setUp(self) -> None:
		self.dat = DAT.FlingyDAT()
		self.dat.new_file()

	def test_wrong_type_raises(self) -> None:
		with self.assertRaises(PyMSError):
			self.dat.get_entry(0).import_data({'_type': 'NotFlingy', 'sprite': 1})

	def test_unrecognized_property_raises(self) -> None:
		with self.assertRaises(PyMSError):
			self.dat.get_entry(0).import_data({'_type': 'Flingy', 'nonexistent_property': 1})


if __name__ == '__main__':
	unittest.main()
