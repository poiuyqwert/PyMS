from .Item import Item
from .Folder import Folder
from .File import File

from .MPQ import MPQ
from .GRP import GRP
from .AIScript import AIScript
from .TBL import TBL

from typing import Type as _Type

ITEM_TYPES: list[_Type[Item]] = [
	MPQ,
	GRP,
	AIScript,
	TBL,
]
