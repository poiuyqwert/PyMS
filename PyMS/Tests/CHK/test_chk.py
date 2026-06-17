
from .utils import make_chk, make_chk_with_version
from ...FileFormats.CHK import Sections
from ...FileFormats.CHK.CHKSectionUnknown import CHKSectionUnknown
from ...Utilities import IO

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
		data = IO.output_to_bytes(self._populated().save)
		loaded = make_chk()
		loaded.load(data)
		self.assertEqual(loaded.section_order, [CHKSectionVER.NAME, CHKSectionDIM.NAME])
		dim = loaded.sections[CHKSectionDIM.NAME]
		assert isinstance(dim, CHKSectionDIM)
		self.assertEqual((dim.width, dim.height), (128, 96))

	def test_round_trip_is_byte_identical(self) -> None:
		data = IO.output_to_bytes(self._populated().save)
		loaded = make_chk()
		loaded.load(data)
		self.assertEqual(IO.output_to_bytes(loaded.save), data)

	def test_unknown_section_preserved(self) -> None:
		data = IO.output_to_bytes(self._populated().save) + struct.pack('<4sL', b'XXXX', 3) + b'abc'
		loaded = make_chk()
		loaded.load(data)
		self.assertIsInstance(loaded.sections[b'XXXX'], CHKSectionUnknown)
		self.assertEqual(IO.output_to_bytes(loaded.save), data)

	def test_save_appends_sections_not_in_order(self) -> None:
		chk = self._populated()
		# A section present but absent from section_order is still written.
		era = Sections.CHKSectionERA(chk)
		chk.sections[Sections.CHKSectionERA.NAME] = era
		data = IO.output_to_bytes(chk.save)
		loaded = make_chk()
		loaded.load(data)
		self.assertIn(Sections.CHKSectionERA.NAME, loaded.sections)

	def test_zero_length_section_at_eof_is_read(self) -> None:
		# A section header that begins exactly at EOF (8-byte header, empty body)
		# must still be read rather than dropped by the scan boundary.
		data = IO.output_to_bytes(self._populated().save) + struct.pack('<4sL', b'XXXX', 0)
		loaded = make_chk()
		loaded.load(data)
		self.assertIn(b'XXXX', loaded.sections)
		self.assertIn(b'XXXX', loaded.section_order)

	def test_duplicate_section_name_recorded_and_written_once(self) -> None:
		# Repeated section names collapse to the last occurrence; the name must
		# appear exactly once in the order and be written exactly once on save.
		ver = CHKSectionVER(make_chk())
		ver.version = CHKSectionVER.BW
		ver_body = ver.save_data()
		dim_a = CHKSectionDIM(make_chk())
		dim_a.width, dim_a.height = 128, 96
		dim_b = CHKSectionDIM(make_chk())
		dim_b.width, dim_b.height = 64, 64
		def section_bytes(name: bytes, body: bytes) -> bytes:
			return struct.pack('<4sL', name, len(body)) + body
		data = (
			section_bytes(CHKSectionVER.NAME, ver_body)
			+ section_bytes(CHKSectionDIM.NAME, dim_a.save_data())
			+ section_bytes(CHKSectionDIM.NAME, dim_b.save_data())
		)
		loaded = make_chk()
		loaded.load(data)
		self.assertEqual(loaded.section_order.count(CHKSectionDIM.NAME), 1)
		# Last occurrence wins.
		dim = loaded.sections[CHKSectionDIM.NAME]
		assert isinstance(dim, CHKSectionDIM)
		self.assertEqual((dim.width, dim.height), (64, 64))
		# Saving emits the section only once, not once per original occurrence.
		saved = IO.output_to_bytes(loaded.save)
		self.assertEqual(saved.count(CHKSectionDIM.NAME), 1)
