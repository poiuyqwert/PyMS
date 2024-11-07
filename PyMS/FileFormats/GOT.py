
from __future__ import annotations

from ..Utilities.fileutils import load_file
from ..Utilities.PyMSError import PyMSError
from ..Utilities import IO
from ..Utilities import Serialize

import struct
from enum import Enum

from typing import Protocol, Type

class VictoryCondition(Enum):
	map_default = 0
	melee = 1
	highest_score = 2
	resources = 3
	capture_the_flag = 4
	sudden_death = 5
	slaughter = 6
	one_on_one = 7

	@staticmethod
	def ALL() -> tuple[VictoryCondition, ...]:
		return (VictoryCondition.map_default, VictoryCondition.melee, VictoryCondition.highest_score, VictoryCondition.resources, VictoryCondition.capture_the_flag, VictoryCondition.sudden_death, VictoryCondition.slaughter, VictoryCondition.one_on_one)

	@property
	def requires_value(self) -> bool:
		if self == VictoryCondition.resources:
			return True
		if self == VictoryCondition.slaughter:
			return True
		return False

	@property
	def display_name(self) -> str:
		match self:
			case VictoryCondition.map_default:
				return 'Map Default'
			case VictoryCondition.melee:
				return 'Melee'
			case VictoryCondition.highest_score:
				return 'Highest Score'
			case VictoryCondition.resources:
				return 'Resources'
			case VictoryCondition.capture_the_flag:
				return 'Capture the Flag'
			case VictoryCondition.sudden_death:
				return 'Sudden Death'
			case VictoryCondition.slaughter:
				return 'Slaughter'
			case VictoryCondition.one_on_one:
				return 'One on One'

class Resources(Enum):
	map_default = 0
	fixed_value = 1
	low = 2
	medium = 3
	high = 4
	income = 5

	@staticmethod
	def ALL() -> tuple[Resources, ...]:
		return (Resources.map_default, Resources.fixed_value, Resources.low, Resources.medium, Resources.high, Resources.income)

	@property
	def requires_value(self) -> bool:
		if self == Resources.fixed_value:
			return True
		if self == Resources.income:
			return True
		return False

	@property
	def display_name(self) -> str:
		match self:
			case Resources.map_default:
				return 'Map Default'
			case Resources.fixed_value:
				return 'Fixed Value'
			case Resources.low:
				return 'Low'
			case Resources.medium:
				return 'Medium'
			case Resources.high:
				return 'High'
			case Resources.income:
				return 'Income'

class UnitStats(Enum):
	map_default = 0
	standard = 1

	@staticmethod
	def ALL() -> tuple[UnitStats, ...]:
		return (UnitStats.map_default, UnitStats.standard)

	@property
	def display_name(self) -> str:
		match self:
			case UnitStats.map_default:
				return 'Map Default'
			case UnitStats.standard:
				return 'Standard'

class FogOfWar(Enum):
	off = 0
	war1 = 1
	on = 2

	@staticmethod
	def ALL() -> tuple[FogOfWar, ...]:
		return (FogOfWar.off, FogOfWar.war1, FogOfWar.on)

	@property
	def display_name(self) -> str:
		match self:
			case FogOfWar.off:
				return 'Off'
			case FogOfWar.war1:
				return 'Warcraft 1 Style'
			case FogOfWar.on:
				return 'On'

class StartingUnits(Enum):
	map_default = 0
	workers_only = 1
	workers_and_center = 2

	@staticmethod
	def ALL() -> tuple[StartingUnits, ...]:
		return (StartingUnits.map_default, StartingUnits.workers_only, StartingUnits.workers_and_center)

	@property
	def display_name(self) -> str:
		match self:
			case StartingUnits.map_default:
				return 'Map Default'
			case StartingUnits.workers_only:
				return 'Workers Only'
			case StartingUnits.workers_and_center:
				return 'Workers and Center'

class StartingPositions(Enum):
	random = 0
	fixed = 1

	@staticmethod
	def ALL() -> tuple[StartingPositions, ...]:
		return (StartingPositions.random, StartingPositions.fixed)

	@property
	def display_name(self) -> str:
		match self:
			case StartingPositions.random:
				return 'Random'
			case StartingPositions.fixed:
				return 'Fixed'

class PlayerTypes(Enum):
	no_single_no_ai = 0
	no_single_ai = 1
	single_no_ai = 2
	single_ai = 3

	@staticmethod
	def ALL() -> tuple[PlayerTypes, ...]:
		return (PlayerTypes.no_single_no_ai, PlayerTypes.no_single_ai, PlayerTypes.single_no_ai, PlayerTypes.single_ai)

	@property
	def display_name(self) -> str:
		match self:
			case PlayerTypes.no_single_no_ai:
				return 'No Single, No AI'
			case PlayerTypes.no_single_ai:
				return 'No Single, AI'
			case PlayerTypes.single_no_ai:
				return 'Single, No AI'
			case PlayerTypes.single_ai:
				return 'Single, AI'

class Allies(Enum):
	not_allowed = 0
	allowed = 1

	@staticmethod
	def ALL() -> tuple[Allies, ...]:
		return (Allies.not_allowed, Allies.allowed)

	@property
	def display_name(self) -> str:
		match self:
			case Allies.not_allowed:
				return 'Not Allowed'
			case Allies.allowed:
				return 'Allowed'

class TeamMode(Enum):
	off = 0
	# dont_choose_me = 1
	teams_2 = 2
	teams_3 = 3
	teams_4 = 4
	# blank = 5

	@staticmethod
	def ALL() -> tuple[TeamMode, ...]:
		return (TeamMode.off, TeamMode.teams_2, TeamMode.teams_3, TeamMode.teams_4)

	@property
	def display_name(self) -> str:
		match self:
			case TeamMode.off:
				return 'Off'
			case TeamMode.teams_2:
				return '2 Teams'
			case TeamMode.teams_3:
				return '3 Teams'
			case TeamMode.teams_4:
				return '4 Teams'

class CheatCodes(Enum):
	off = 0
	on = 1

	@staticmethod
	def ALL() -> tuple[CheatCodes, ...]:
		return (CheatCodes.off, CheatCodes.on)

	@property
	def display_name(self) -> str:
		match self:
			case CheatCodes.off:
				return 'Off'
			case CheatCodes.on:
				return 'On'

class TournametMode(Enum):
	off = 0
	on = 1

	@staticmethod
	def ALL() -> tuple[TournametMode, ...]:
		return (TournametMode.off, TournametMode.on)

	@property
	def display_name(self) -> str:
		match self:
			case TournametMode.off:
				return 'Off'
			case TournametMode.on:
				return 'On'

class HasALL(Protocol):
	@staticmethod
	def ALL() -> tuple[Enum, ...]:
		...

_GOTDefinition = Serialize.Definition('Template', Serialize.IDMode.none, {
	'name': Serialize.StrEncoder(),
	'subtype_name': Serialize.StrEncoder(),
	'gametype_id': Serialize.IntEncoder(0, 31),
	'league_id': Serialize.IntEncoder(),
	'subtype_id': Serialize.IntEncoder(0, 7),
	'subtype_display': Serialize.IntEncoder(),
	'subtype_label': Serialize.IntEncoder(),
	'victory_condition': Serialize.EnumNameEncoder(VictoryCondition),
	'resources': Serialize.EnumNameEncoder(Resources),
	'unit_stats': Serialize.EnumNameEncoder(UnitStats),
	'fog_of_war': Serialize.EnumNameEncoder(FogOfWar),
	'starting_units': Serialize.EnumNameEncoder(StartingUnits),
	'starting_positions': Serialize.EnumNameEncoder(StartingPositions),
	'player_types': Serialize.EnumNameEncoder(PlayerTypes),
	'allies': Serialize.EnumNameEncoder(Allies),
	'team_mode': Serialize.EnumNameEncoder(TeamMode),
	'cheat_codes': Serialize.EnumNameEncoder(CheatCodes),
	'tournament_mode': Serialize.EnumNameEncoder(TournametMode),
	'victory_condition_value': Serialize.IntEncoder(),
	'resources_value': Serialize.IntEncoder(),
	'subtype_value': Serialize.IntEncoder(0, 56534),
})

class GOT:
	def __init__(self) -> None:
		self.name = ''
		self.subtype_name = ''
		self.gametype_id = 0 # < 32
		self.league_id = 0
		self.subtype_id = 0 # < 8
		self.subtype_display = 0 # < 56534
		self.subtype_label = 0
		self.victory_condition = VictoryCondition.map_default
		self.resources = Resources.map_default
		self.unit_stats = UnitStats.map_default
		self.fog_of_war = FogOfWar.off
		self.starting_units = StartingUnits.map_default
		self.starting_positions = StartingPositions.random
		self.player_types = PlayerTypes.no_single_no_ai
		self.allies = Allies.not_allowed
		self.team_mode = TeamMode.off
		self.cheat_codes = CheatCodes.off
		self.tournament_mode = TournametMode.off
		self.victory_condition_value = 0
		self.resources_value = 0
		self.subtype_value = 0

	def load_file(self, input: IO.AnyInputBytes) -> None:
		with IO.InputBytes(input) as f:
			data = f.read()
		try:
			if len(data) != 97 or data[0] != 3:
				raise Exception()
			raw_name: bytes
			raw_subtype_name: bytes
			gametype_id: int
			league_id: int
			subtype_id: int
			subtype_display: int
			subtype_label: int
			raw_victory_condition: int
			raw_resources: int
			raw_unit_stats: int
			raw_fog_of_war: int
			raw_starting_units: int
			raw_starting_positions: int
			raw_player_types: int
			raw_allies: int
			raw_team_mode: int
			raw_cheat_codes: int
			raw_tournament_mode: int
			victory_condition_value: int
			resources_value: int
			subtype_value: int
			fields = struct.unpack('<x32s32s2B3H11B3Lx', data)
			raw_name,raw_subtype_name,gametype_id,league_id,subtype_id,subtype_display,subtype_label,raw_victory_condition,raw_resources,raw_unit_stats,raw_fog_of_war,raw_starting_units,raw_starting_positions,raw_player_types,raw_allies,raw_team_mode,raw_cheat_codes,raw_tournament_mode,victory_condition_value,resources_value,subtype_value = fields
			name = raw_name.rstrip(b'\x00').decode('utf-8')
			subtype_name = raw_subtype_name.rstrip(b'\x00').decode('utf-8')
			victory_condition = VictoryCondition(raw_victory_condition)
			resources = Resources(raw_resources)
			unit_stats = UnitStats(raw_unit_stats)
			fog_of_war = FogOfWar(raw_fog_of_war)
			starting_units = StartingUnits(raw_starting_units)
			starting_positions = StartingPositions(raw_starting_positions)
			player_types = PlayerTypes(raw_player_types)
			allies = Allies(raw_allies)
			team_mode = TeamMode(raw_team_mode)
			cheat_codes = CheatCodes(raw_cheat_codes)
			tournament_mode = TournametMode(raw_tournament_mode)
		except PyMSError as e:
			raise PyMSError('Load',"Unsupported GOT file, could possibly be corrupt")
		self.name = name
		self.subtype_name = subtype_name
		self.gametype_id = gametype_id
		self.league_id = league_id
		self.subtype_id = subtype_id
		self.subtype_display = subtype_display
		self.subtype_label = subtype_label
		self.victory_condition = victory_condition
		self.resources = resources
		self.unit_stats = unit_stats
		self.fog_of_war = fog_of_war
		self.starting_units = starting_units
		self.starting_positions = starting_positions
		self.player_types = player_types
		self.allies = allies
		self.team_mode = team_mode
		self.cheat_codes = cheat_codes
		self.tournament_mode = tournament_mode
		self.victory_condition_value = victory_condition_value
		self.resources_value = resources_value
		self.subtype_value = subtype_value

	def decompile(self, output: IO.AnyOutputText, include_reference: bool = True):
		text = Serialize.encode_text(self, None, _GOTDefinition)
		with IO.OutputText(output) as f:
			if include_reference:
				f.write('#----------------------------------------------------\n')
				for field_name,encoder in _GOTDefinition.structure.items():
					if not isinstance(encoder, Serialize.EnumNameEncoder):
						continue
					f.write(f"# '{field_name}' options:\n")
					enum_type: Type[HasALL] = encoder.enum_type
					for option in enum_type.ALL():
						f.write(f'#    {option.name}\n')
				f.write('#----------------------------------------------------\n')
			f.write(text)

	def interpret(self, input: IO.AnyInputText):
		with IO.InputText(input) as f:
			text = f.read()
		Serialize.decode_text(text, [_GOTDefinition], lambda i,d: self, 1)

	def save_data(self) -> bytes:
		return struct.pack('<B32s32s2B3H11B3Lx', 3, self.name.encode('utf-8'),self.subtype_name.encode('utf-8'),self.gametype_id,self.subtype_id,self.subtype_display,self.subtype_label,self.victory_condition,self.resources,self.unit_stats,self.fog_of_war,self.starting_units,self.starting_positions,self.player_types,self.allies,self.team_mode,self.cheat_codes,self.tournament_mode,self.victory_condition_value,self.resources_value,self.subtype_value)

	def save_file(self, output: IO.AnyOutputBytes):
		data = self.save_data()
		with IO.OutputBytes(output) as f:
			f.write(data)
