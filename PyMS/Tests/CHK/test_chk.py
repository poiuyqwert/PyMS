
from .utils import make_chk, make_chk_with_version
from ...FileFormats.CHK import Sections
from ...FileFormats.CHK.CHKSectionUnknown import CHKSectionUnknown

import struct
import unittest

CHKSectionVER = Sections.CHKSectionVER
CHKSectionDIM = Sections.CHKSectionDIM
CHKSectionCOLR = Sections.CHKSectionCOLR


class Test_get_section(unittest.TestCase):
	def test_returns_existing_version_section(self) -> None:
		chk = make_chk_with_version(CHKSectionVER.BW)
		self.assertIs(chk.get_section(CHKSectionVER), chk.sections[CHKSectionVER.NAME])

	def test_creates_required_section(self) -> None:
		chk = make_chk_with_version(CHKSectionVER.BW)
		section = chk.get_section(CHKSectionDIM)
		self.assertIsInstance(section, CHKSectionDIM)
		self.assertIs(chk.sections[CHKSectionDIM.NAME], section)

	def test_returns_none_when_not_required(self) -> None:
		# COLR requires BroodWar; a 1.04 map does not require it.
		chk = make_chk_with_version(CHKSectionVER.SC104)
		self.assertIsNone(chk.get_section(CHKSectionCOLR))

	def test_get_section_named(self) -> None:
		chk = make_chk_with_version(CHKSectionVER.BW)
		self.assertIs(chk.get_section_named(CHKSectionVER.NAME), chk.sections[CHKSectionVER.NAME])

	def test_get_section_named_creates_required(self) -> None:
		chk = make_chk_with_version(CHKSectionVER.BW)
		section = chk.get_section_named(CHKSectionDIM.NAME)
		self.assertIsInstance(section, CHKSectionDIM)


class Test_player_color(unittest.TestCase):
	def test_default_colors(self) -> None:
		chk = make_chk_with_version(CHKSectionVER.BW)
		self.assertEqual(chk.player_color(0), CHKSectionCOLR.RED)
		self.assertEqual(chk.player_color(7), CHKSectionCOLR.YELLOW)

	def test_appended_trailing_colors(self) -> None:
		chk = make_chk_with_version(CHKSectionVER.BW)
		self.assertEqual(chk.player_color(8), CHKSectionCOLR.GREEN)
		self.assertEqual(chk.player_color(11), CHKSectionCOLR.NEUTRAL)

	def test_uses_colr_section_when_present(self) -> None:
		chk = make_chk_with_version(CHKSectionVER.BW)
		colr = CHKSectionCOLR(chk)
		colr.colors = [CHKSectionCOLR.WHITE] * 8
		chk.sections[CHKSectionCOLR.NAME] = colr
		self.assertEqual(chk.player_color(0), CHKSectionCOLR.WHITE)

	def test_does_not_mutate_default_colors(self) -> None:
		chk = make_chk_with_version(CHKSectionVER.BW)
		before = list(CHKSectionCOLR.DEFAULT_COLORS)
		chk.player_color(8)
		chk.player_color(8)
		self.assertEqual(CHKSectionCOLR.DEFAULT_COLORS, before)


class Test_load_save(unittest.TestCase):
	def _populated(self):
		chk = make_chk()
		ver = CHKSectionVER(chk)
		ver.version = CHKSectionVER.BW
		dim = CHKSectionDIM(chk)
		dim.width, dim.height = 128, 96
		chk.sections = {CHKSectionVER.NAME: ver, CHKSectionDIM.NAME: dim}
		chk.section_order = [CHKSectionVER.NAME, CHKSectionDIM.NAME]
		return chk

	def test_round_trip_preserves_order_and_values(self) -> None:
		data = self._populated().save_data()
		loaded = make_chk()
		loaded.load_data(data)
		self.assertEqual(loaded.section_order, [CHKSectionVER.NAME, CHKSectionDIM.NAME])
		dim = loaded.sections[CHKSectionDIM.NAME]
		assert isinstance(dim, CHKSectionDIM)
		self.assertEqual((dim.width, dim.height), (128, 96))

	def test_round_trip_is_byte_identical(self) -> None:
		data = self._populated().save_data()
		loaded = make_chk()
		loaded.load_data(data)
		self.assertEqual(loaded.save_data(), data)

	def test_unknown_section_preserved(self) -> None:
		data = self._populated().save_data() + struct.pack('<4sL', b'XXXX', 3) + b'abc'
		loaded = make_chk()
		loaded.load_data(data)
		self.assertIsInstance(loaded.sections[b'XXXX'], CHKSectionUnknown)
		self.assertEqual(loaded.save_data(), data)

	def test_save_appends_sections_not_in_order(self) -> None:
		chk = self._populated()
		# A section present but absent from section_order is still written.
		era = Sections.CHKSectionERA(chk)
		chk.sections[Sections.CHKSectionERA.NAME] = era
		data = chk.save_data()
		loaded = make_chk()
		loaded.load_data(data)
		self.assertIn(Sections.CHKSectionERA.NAME, loaded.sections)
