
from ...PyDAT.DATRef import DATRef, DATRefMatch, DATRefs
from ...PyDAT.DataID import DATID
from ...PyDAT.DataContext import DataContext
from ...FileFormats.DAT.UnitsDAT import DATUnit

import unittest
from typing import cast


class Test_DATRef_matches(unittest.TestCase):
	def test_none_entry_id_never_matches(self) -> None:
		self.assertFalse(DATRef('field', None).matches(0))
		self.assertFalse(DATRef('field', None).matches(5))

	def test_exact_match(self) -> None:
		ref = DATRef('field', 3)
		self.assertTrue(ref.matches(3))
		self.assertFalse(ref.matches(2))
		self.assertFalse(ref.matches(4))

	def test_range_is_inclusive(self) -> None:
		ref = DATRef('field', 2, 5)
		self.assertEqual([ref.matches(i) for i in range(7)], [False, False, True, True, True, True, False])

	def test_range_end_zero_falls_back_to_exact(self) -> None:
		# A range end of 0 is falsy, so it is treated as an exact match on entry_id.
		ref = DATRef('field', 0, 0)
		self.assertTrue(ref.matches(0))
		self.assertFalse(ref.matches(1))


class Test_DATRefMatch_str(unittest.TestCase):
	def test_without_sub_tab(self) -> None:
		match = DATRefMatch(DATID.units, dat_sub_tab_id=None, field_name='subunit1', entry_id=7, entry_name='Marine')
		self.assertEqual(str(match), 'units.dat, subunit1 field, entry 7: Marine')

	def test_with_sub_tab(self) -> None:
		class _SubTab:
			tab_name = 'Graphics'
		match = DATRefMatch(DATID.weapons, dat_sub_tab_id=_SubTab(), field_name='graphics', entry_id=2, entry_name='Gun')
		self.assertEqual(str(match), 'weapons.dat, graphics field (Graphics sub-tab), entry 2: Gun')


class Test_DATRefs_matching(unittest.TestCase):
	def setUp(self) -> None:
		self.dc = DataContext()

	def _unit(self, entry_id: int) -> DATUnit:
		assert self.dc.units.dat is not None
		entry = self.dc.units.dat.get_entry(entry_id)
		assert isinstance(entry, DATUnit)
		return entry

	def test_returns_empty_when_dat_not_loaded(self) -> None:
		# A fresh DataContext has not loaded any DAT files.
		self.assertIsNone(self.dc.units.dat)
		refs = DATRefs(DATID.units, lambda entry: (DATRef('subunit1', 0),))
		self.assertEqual(refs.matching(self.dc, 0), [])

	def test_finds_entries_referencing_lookup_id(self) -> None:
		self.dc.units.new_file()
		# Default subunit1 is 228, so 42 is a value no default entry holds.
		self._unit(5).subunit1 = 42
		self._unit(9).subunit1 = 42
		refs = DATRefs(DATID.units, lambda entry: (DATRef('subunit1', cast(DATUnit, entry).subunit1),))
		matches = refs.matching(self.dc, 42)
		self.assertEqual(sorted(match.entry_id for match in matches), [5, 9])

	def test_no_matching_entries_returns_empty(self) -> None:
		self.dc.units.new_file()
		refs = DATRefs(DATID.units, lambda entry: (DATRef('subunit1', cast(DATUnit, entry).subunit1),))
		# Nothing references entry 42 (all default to 228).
		self.assertEqual(refs.matching(self.dc, 42), [])

	def test_multiple_refs_per_entry(self) -> None:
		self.dc.units.new_file()
		self._unit(3).subunit1 = 42
		self._unit(3).subunit2 = 42
		self._unit(5).subunit1 = 42
		refs = DATRefs(DATID.units, lambda entry: (
			DATRef('subunit1', cast(DATUnit, entry).subunit1),
			DATRef('subunit2', cast(DATUnit, entry).subunit2),
		))
		matches = refs.matching(self.dc, 42)
		self.assertEqual(
			sorted((match.entry_id, match.field_name) for match in matches),
			[(3, 'subunit1'), (3, 'subunit2'), (5, 'subunit1')],
		)

	def test_match_carries_metadata(self) -> None:
		self.dc.units.new_file()
		self._unit(7).subunit1 = 42
		refs = DATRefs(DATID.units, lambda entry: (DATRef('subunit1', cast(DATUnit, entry).subunit1, dat_sub_tab=None),))
		matches = refs.matching(self.dc, 42)
		self.assertEqual(len(matches), 1)
		match = matches[0]
		self.assertEqual(match.dat_id, DATID.units)
		self.assertEqual(match.field_name, 'subunit1')
		self.assertEqual(match.entry_id, 7)
		self.assertEqual(match.entry_name, self.dc.units.entry_name(7))

	def test_range_ref_in_lookup(self) -> None:
		self.dc.units.new_file()
		entry_count = self.dc.units.entry_count()
		# Every entry contributes a ref covering ids 10..20.
		refs = DATRefs(DATID.units, lambda entry: (DATRef('field', 10, 20),))
		self.assertEqual(len(refs.matching(self.dc, 15)), entry_count)
		self.assertEqual(refs.matching(self.dc, 25), [])
