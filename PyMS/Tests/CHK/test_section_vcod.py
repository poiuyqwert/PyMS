
from .utils import make_chk
from ...FileFormats.CHK.Sections.CHKSectionVCOD import CHKSectionVCOD

import struct
import unittest


class Test_CHKSectionVCOD(unittest.TestCase):
	def test_default_code_and_opcodes(self) -> None:
		section = CHKSectionVCOD(make_chk())
		self.assertEqual(section.code, CHKSectionVCOD.DEFAULT_CODE)
		self.assertEqual(section.opcodes, CHKSectionVCOD.DEFAULT_OPCODES)

	def test_round_trip(self) -> None:
		chk = make_chk()
		data = bytes((i * 3) % 256 for i in range(1024)) + struct.pack('<16B', *range(16))
		section = CHKSectionVCOD(chk)
		section.load_data(data)
		self.assertEqual(section.code, data[:1024])
		self.assertEqual(section.opcodes, tuple(range(16)))
		self.assertEqual(section.save_data(), data)

	def test_default_save_round_trips(self) -> None:
		chk = make_chk()
		data = CHKSectionVCOD(chk).save_data()
		self.assertEqual(len(data), 1040)
		reloaded = CHKSectionVCOD(chk)
		reloaded.load_data(data)
		self.assertEqual(reloaded.save_data(), data)

	def test_decompile(self) -> None:
		self.assertTrue(CHKSectionVCOD(make_chk()).decompile().startswith('VCOD:'))
