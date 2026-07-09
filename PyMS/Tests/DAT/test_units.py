
from ...FileFormats.DAT import UnitsDAT
from ...FileFormats.DAT.UnitsDAT import DATUnit
from ...Utilities import IO

from ..utils import resource_path

import unittest


def _real_units() -> bytes:
	with open(resource_path('units.dat', __file__), 'rb') as f:
		return f.read()


def _entry(dat: UnitsDAT, entry_id: int) -> DATUnit:
	entry = dat.entries[entry_id]
	assert isinstance(entry, DATUnit)
	return entry


class Test_Units(unittest.TestCase):
	def test_load_and_save(self) -> None:
		expected = _real_units()

		dat = UnitsDAT()
		dat.load(expected)

		result = IO.output_to_bytes(dat.save)

		self.assertEqual(result, expected)


class Test_Units_new_file(unittest.TestCase):
	# UnitsDAT has partial properties (sounds, infestation, addon_position) that only exist
	# for a sub-range of unit ids. `new_file` must produce a saveable file where in-range
	# partial properties are available and out-of-range ones are `None`.
	def test_new_file_saves_and_round_trips(self) -> None:
		dat = UnitsDAT()
		dat.new_file()
		data = IO.output_to_bytes(dat.save)

		reloaded = UnitsDAT()
		reloaded.load(data)
		self.assertEqual(IO.output_to_bytes(reloaded.save), data)

	def test_new_file_partial_property_pattern_matches_loaded_file(self) -> None:
		loaded = UnitsDAT()
		loaded.load(_real_units())
		fresh = UnitsDAT()
		fresh.new_file()

		for prop in ('infestation', 'ready_sound', 'pissed_sound_start', 'yes_sound_end', 'addon_position'):
			with self.subTest(prop=prop):
				loaded_pattern = [getattr(e, prop) is None for e in loaded.entries]
				fresh_pattern = [getattr(e, prop) is None for e in fresh.entries]
				self.assertEqual(fresh_pattern, loaded_pattern)

	def test_new_file_in_range_partial_properties_are_available(self) -> None:
		dat = UnitsDAT()
		dat.new_file()
		# infestation / addon_position apply to units 106..201.
		self.assertIsNone(_entry(dat, 0).infestation)
		self.assertIsNotNone(_entry(dat, 150).infestation)
		self.assertIsNone(_entry(dat, 227).addon_position)
		self.assertIsNotNone(_entry(dat, 150).addon_position)
		# sounds apply to units 0..105.
		self.assertIsNotNone(_entry(dat, 50).ready_sound)
		self.assertIsNone(_entry(dat, 200).ready_sound)

	def test_expanded_new_file_round_trips(self) -> None:
		dat = UnitsDAT()
		dat.new_file(300)
		self.assertTrue(dat.is_expanded())
		data = IO.output_to_bytes(dat.save)
		reloaded = UnitsDAT()
		reloaded.load(data)
		self.assertEqual(IO.output_to_bytes(reloaded.save), data)


class Test_is_on_entry(unittest.TestCase):
	# Regression for a property with `entry_offset` of 0: the range check must not treat
	# offset 0 as "no offset" (which would report the property present on every entry).
	def test_zero_offset_property_respects_range(self) -> None:
		ready_sound = UnitsDAT.FORMAT.get_property('ready_sound')
		assert ready_sound is not None
		self.assertTrue(ready_sound.is_on_entry(0))
		self.assertTrue(ready_sound.is_on_entry(105))
		self.assertFalse(ready_sound.is_on_entry(106))
		self.assertFalse(ready_sound.is_on_entry(200))

	def test_nonzero_offset_property_respects_range(self) -> None:
		infestation = UnitsDAT.FORMAT.get_property('infestation')
		assert infestation is not None
		self.assertFalse(infestation.is_on_entry(105))
		self.assertTrue(infestation.is_on_entry(106))
		self.assertTrue(infestation.is_on_entry(201))
		self.assertFalse(infestation.is_on_entry(202))

	def test_unbounded_property_is_on_every_entry(self) -> None:
		# A property without offset/count (e.g. what_sound) exists on all entries.
		what_sound = UnitsDAT.FORMAT.get_property('what_sound_start')
		assert what_sound is not None
		self.assertTrue(what_sound.is_on_entry(0))
		self.assertTrue(what_sound.is_on_entry(227))
