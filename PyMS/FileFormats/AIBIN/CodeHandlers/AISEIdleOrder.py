
from __future__ import annotations

from ....Utilities.BytesScanner import BytesScanner
from ....Utilities import Struct

from dataclasses import dataclass

from typing import TypeAlias

@dataclass
class BasicFlags:
	TYPE_ID = 0

	flags: int

	@staticmethod
	def decompile(value: int) -> BasicFlags:
		return BasicFlags(value)

@dataclass
class SpellEffects:
	TYPE_ID_WITH = 1
	TYPE_ID_WITHOUT = 2

	without: bool
	flags: int

	@staticmethod
	def decompile(type: int, value: int) -> SpellEffects:
		return SpellEffects(type == SpellEffects.TYPE_ID_WITHOUT, value)

@dataclass
class UnitProps:
	TYPE_ID = 3

	field: int
	comparison: int
	amount: int

	@staticmethod
	def decompile(value: int, scanner: BytesScanner) -> UnitProps:
		return UnitProps((value >> 4) & 0xF, value & 0xF, scanner.scan(Struct.l_u32))

@dataclass
class Order:
	TYPE_ID = 5

	order_id: int

	@staticmethod
	def decompile(value: int) -> Order:
		return Order(value)

@dataclass
class UnitFlags:
	TYPE_ID = 6

	without: bool
	flags: int

	@staticmethod
	def decompile(value: int, scanner: BytesScanner) -> UnitFlags:
		return UnitFlags(value == 1, scanner.scan(Struct.l_u32))

@dataclass
class Targetting:
	TYPE_ID = 7

	flags: int

	@staticmethod
	def decompile(value: int) -> Targetting:
		return Targetting(value)

@dataclass
class RandomRate:
	TYPE_ID = 8

	low: int
	high: int

	@staticmethod
	def decompile(scanner: BytesScanner) -> RandomRate:
		return RandomRate(scanner.scan(Struct.l_u16), scanner.scan(Struct.l_u16))

@dataclass
class UnitCount:
	TYPE_ID = 9

	comparison: int
	amount: int
	radius: int
	players: int

	@staticmethod
	def decompile(scanner: BytesScanner) -> UnitCount:
		return UnitCount(scanner.scan(Struct.l_u8), scanner.scan(Struct.l_u16), scanner.scan(Struct.l_u16), scanner.scan(Struct.l_u8))

@dataclass
class TileFlags:
	TYPE_ID = 10

	without: bool
	flags: int

	@staticmethod
	def decompile(value: int, scanner: BytesScanner) -> TileFlags:
		return TileFlags(value == 1, scanner.scan(Struct.l_u8))

Option: TypeAlias = 'OptionSet | BasicFlags | SpellEffects | UnitProps | Order | UnitFlags | Targetting | RandomRate | UnitCount | TileFlags'
OptionSet = tuple[Option, ...]
