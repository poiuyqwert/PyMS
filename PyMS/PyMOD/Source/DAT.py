
from __future__ import annotations

from .File import File

import os

from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from ...FileFormats.DAT.AbstractDAT import AbstractDAT

def _dat_types() -> dict[str, type[AbstractDAT]]:
	from ...FileFormats import DAT as FileFormatsDAT
	dat_types: tuple[type[AbstractDAT], ...] = (
		FileFormatsDAT.UnitsDAT,
		FileFormatsDAT.WeaponsDAT,
		FileFormatsDAT.FlingyDAT,
		FileFormatsDAT.SpritesDAT,
		FileFormatsDAT.ImagesDAT,
		FileFormatsDAT.UpgradesDAT,
		FileFormatsDAT.TechDAT,
		FileFormatsDAT.SoundsDAT,
		FileFormatsDAT.PortraitsDAT,
		FileFormatsDAT.CampaignDAT,
		FileFormatsDAT.OrdersDAT,
	)
	return {dat_type.FILE_NAME: dat_type for dat_type in dat_types}

class DAT(File):
	@classmethod
	def matches(cls, folder_name: str) -> float:
		if folder_name in _dat_types():
			return 1
		return 0

	def dat_type(self) -> type[AbstractDAT]:
		return _dat_types()[self.name]

	def text_paths(self) -> list[str]:
		text_paths: list[str] = []
		for filename in os.listdir(self.path):
			if filename.endswith('.txt'):
				text_paths.append(os.path.join(self.path, filename))
		return sorted(text_paths)

	# A file in the folder named the same as the folder (e.g. `units.dat/units.dat`) is a
	# user-supplied base file for the import to be applied on top of
	def base_dat_path(self) -> str | None:
		base_dat_path = os.path.join(self.path, self.name)
		if os.path.isfile(base_dat_path):
			return base_dat_path
		return None
