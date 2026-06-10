
from ...FileFormats.CHK.CHK import CHK
from ...FileFormats.CHK import Sections
from ...FileFormats import TBL
from ...FileFormats.AIBIN import AIBIN


def make_chk() -> CHK:
	# Build a CHK without loading the bundled stat_txt/aiscript assets.
	return CHK(stat_txt=TBL.TBL(), aiscript=AIBIN.AIBIN())


def make_chk_with_version(version: int) -> CHK:
	chk = make_chk()
	ver = Sections.CHKSectionVER(chk)
	ver.version = version
	chk.sections = {Sections.CHKSectionVER.NAME: ver}
	chk.section_order = [Sections.CHKSectionVER.NAME]
	return chk


def make_chk_with_dim(width: int = 2, height: int = 2) -> CHK:
	chk = make_chk_with_version(Sections.CHKSectionVER.BW)
	dim = Sections.CHKSectionDIM(chk)
	dim.width, dim.height = width, height
	chk.sections[Sections.CHKSectionDIM.NAME] = dim
	chk.section_order.append(Sections.CHKSectionDIM.NAME)
	return chk
