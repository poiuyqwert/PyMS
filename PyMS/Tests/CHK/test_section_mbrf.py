
from .utils import make_chk
from ...FileFormats.CHK.Sections.CHKSectionMBRF import CHKSectionMBRF
from ...FileFormats.TRG import TRG
from ...FileFormats import TBL
from ...FileFormats.AIBIN import AIBIN

import io
import unittest


def _empty_briefing_bytes() -> bytes:
	trg = TRG.TRG(TBL.TBL(), AIBIN.AIBIN())
	out = io.BytesIO()
	trg.save(out, TRG.Format.briefing)
	return out.getvalue()


class Test_CHKSectionMBRF(unittest.TestCase):
	def test_round_trip(self) -> None:
		data = _empty_briefing_bytes()
		section = CHKSectionMBRF(make_chk())
		section.load_data(data)
		self.assertEqual(section.save_data(), data)

	def test_load_uses_briefing_format(self) -> None:
		section = CHKSectionMBRF(make_chk())
		section.load_data(_empty_briefing_bytes())
		self.assertEqual(section.trg.format, TRG.Format.briefing)

	def test_decompile(self) -> None:
		section = CHKSectionMBRF(make_chk())
		section.load_data(_empty_briefing_bytes())
		self.assertTrue(section.decompile().startswith('MBRF:'))
