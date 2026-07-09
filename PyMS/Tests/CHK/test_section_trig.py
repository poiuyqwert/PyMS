
from .utils import make_chk
from ...FileFormats.CHK.Sections.CHKSectionTRIG import CHKSectionTRIG
from ...FileFormats.TRG import TRG
from ...FileFormats import TBL
from ...FileFormats.AIBIN import AIBIN

import io
import unittest


def _empty_trg_bytes() -> bytes:
	trg = TRG.TRG(TBL.TBL(), AIBIN.AIBIN())
	out = io.BytesIO()
	trg.save(out, TRG.Format.normal)
	return out.getvalue()


class Test_CHKSectionTRIG(unittest.TestCase):
	def test_round_trip(self) -> None:
		data = _empty_trg_bytes()
		section = CHKSectionTRIG(make_chk())
		section.load_data(data)
		self.assertEqual(section.save_data(), data)

	def test_load_wraps_a_trg(self) -> None:
		section = CHKSectionTRIG(make_chk())
		section.load_data(_empty_trg_bytes())
		self.assertIsInstance(section.trg, TRG.TRG)
		self.assertEqual(section.trg.format, TRG.Format.normal)

	def test_decompile(self) -> None:
		section = CHKSectionTRIG(make_chk())
		section.load_data(_empty_trg_bytes())
		self.assertTrue(section.decompile().startswith('TRIG:'))
