
from .utils import make_chk
from ...FileFormats.CHK.Sections.CHKSectionUNIT import CHKSectionUNIT, CHKUnit

import unittest


def _unit(chk, ref_id: int, instance_id: int) -> CHKUnit:
	unit = CHKUnit(chk, ref_id)
	unit.instanceID = instance_id
	unit.position = [10, 20]
	unit.unit_id = 7
	unit.owner = 3
	unit.health = 100
	unit.resources = 1500
	return unit


class Test_CHKUnit(unittest.TestCase):
	def test_round_trip(self) -> None:
		chk = make_chk()
		unit = _unit(chk, 0, 42)
		data = unit.save_data()
		self.assertEqual(len(data), 36)
		reloaded = CHKUnit(chk, 0)
		reloaded.load_data(data)
		self.assertEqual(reloaded.instanceID, 42)
		self.assertEqual(reloaded.position, [10, 20])
		self.assertEqual(reloaded.unit_id, 7)
		self.assertEqual(reloaded.owner, 3)
		self.assertEqual(reloaded.resources, 1500)
		self.assertEqual(reloaded.save_data(), data)

	def test_decompile(self) -> None:
		text = _unit(make_chk(), 0, 1).decompile()
		self.assertIn('InstanceID', text)
		self.assertIn('Position', text)


class Test_CHKSectionUNIT(unittest.TestCase):
	def _section(self) -> CHKSectionUNIT:
		chk = make_chk()
		section = CHKSectionUNIT(chk)
		section.units = {0: _unit(chk, 0, 1), 1: _unit(chk, 1, 2)}
		return section

	def test_round_trip(self) -> None:
		section = self._section()
		data = section.save_data()
		self.assertEqual(len(data), 72)
		reloaded = CHKSectionUNIT(make_chk())
		reloaded.load_data(data)
		self.assertEqual(reloaded.unit_count(), 2)
		self.assertEqual(reloaded.save_data(), data)

	def test_accessors(self) -> None:
		section = self._section()
		self.assertEqual(section.unit_count(), 2)
		self.assertEqual(section.nth_unit(0).instanceID, 1)
		self.assertEqual(section.nth_unit(1).instanceID, 2)
		self.assertIsNotNone(section.get_unit(0))
		self.assertIsNone(section.get_unit(99))

	def test_empty_save(self) -> None:
		self.assertEqual(CHKSectionUNIT(make_chk()).save_data(), b'')

	def test_decompile(self) -> None:
		self.assertTrue(self._section().decompile().startswith('UNIT:'))
