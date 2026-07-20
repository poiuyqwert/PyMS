from .Item import Item
from .Folder import Folder
from .File import File

from .MPQ import MPQ
from .GRP import GRP
from .AIScript import AIScript
from .IScript import IScript
from .TBL import TBL
from .DAT import DAT
from .LO import LO
from .PCX import PCX
from .SPK import SPK

from typing import Type as _Type

ITEM_TYPES: list[_Type[Item]] = [
	MPQ,
	GRP,
	AIScript,
	IScript,
	TBL,
	DAT,
	LO,
	PCX,
	SPK,
]
