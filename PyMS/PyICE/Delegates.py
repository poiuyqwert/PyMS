
from __future__ import annotations

from ..FileFormats import TBL
from ..FileFormats import DAT
from ..FileFormats import IScriptBIN

from ..Utilities.Settings import Settings
from ..Utilities.MPQHandler import MPQHandler
from ..Utilities.UIKit import ScrolledListbox, Toplevel, Misc

from typing import Protocol

class MainDelegate(Protocol):
	settings: Settings

	tbl: TBL.TBL
	imagestbl: TBL.TBL
	sfxdatatbl: TBL.TBL
	unitsdat: DAT.UnitsDAT
	weaponsdat: DAT.WeaponsDAT
	flingydat: DAT.FlingyDAT
	spritesdat: DAT.SpritesDAT
	imagesdat: DAT.ImagesDAT
	soundsdat: DAT.SoundsDAT

	mpqhandler: MPQHandler

	iscriptlist: ScrolledListbox
	imageslist: ScrolledListbox
	spriteslist: ScrolledListbox
	flingylist: ScrolledListbox
	unitlist: ScrolledListbox

	def get_ibin(self) -> IScriptBIN.IScriptBIN:
		...

class CodeGeneratorDelegate(Protocol):
	def load_preset(self, preset: str, window: Toplevel | None) -> bool:
		...

class ImportListDelegate(Protocol):
	imports: list[str]

	def iimport(self, files: str | list[str] | None = None, parent: Misc | None = None) -> None:
		...
