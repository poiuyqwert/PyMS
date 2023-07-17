
from __future__ import annotations

from PyMS.Utilities.PyMSWarning import PyMSWarning

from .Constants import *

from ...FileFormats import TBL

from ...Utilities.PyMSError import PyMSError
from ...Utilities.PyMSWarning import PyMSWarning
from ...Utilities.Bidict import Bidict
from ...Utilities import Struct

import struct

from typing import TYPE_CHECKING, Protocol, runtime_checkable
if TYPE_CHECKING:
	from .TRG import TRG
	from .Condition import Condition
	from .Action import Action

class _Parameter(Protocol):
	def name(self) -> str:
		...

	def help(self) -> str:
		...

class ConditionParameter(_Parameter, Protocol):
	def condition_decompile(self, condition: Condition, trg: TRG) -> str:
		...

	def condition_compile(self, value: str, condition: Condition, trg: TRG) -> (PyMSWarning | None):
		...

class ActionParameter(_Parameter, Protocol):
	def action_decompile(self, action: Action, trg: TRG) -> str:
		...

	def action_compile(self, value: str, action: Action, trg: TRG) -> (PyMSWarning | None):
		...

@runtime_checkable
class HasKeywords(Protocol):
	def keywords(self) -> tuple[str, ...]:
		...

class NumberParameter(ConditionParameter, ActionParameter):
	def name(self) -> str:
		return 'Number'

	def help(self) -> str:
		return 'Any number in the range 0 to 4294967295'

	def _decompile(self, number: int) -> str:
		return str(number)

	def _compile(self, value: str) -> int:
		try:
			number = int(value)
			if -1 < number < 4294967296:
				return number
		except:
			pass
		raise PyMSError('Paramater', f"'{value}' is not a valid Number (value must be a number in the range 0 to 4294967295)")

	def condition_decompile(self, condition: Condition, trg: TRG) -> str:
		return self._decompile(condition.number)

	def condition_compile(self, value: str, condition: Condition, trg: TRG) -> (PyMSWarning | None):
		condition.number = self._compile(value)
		return None

	def action_decompile(self, action: Action, trg: TRG) -> str:
		return self._decompile(action.number)

	def action_compile(self, value: str, action: Action, trg: TRG) -> PyMSWarning | None:
		action.number = self._compile(value)
		return None

class PlayerParameter(ConditionParameter, HasKeywords):
	OPTIONS = Bidict({
		PlayerGroup.p1: 'Player 1',
		PlayerGroup.p2: 'Player 2',
		PlayerGroup.p3: 'Player 3',
		PlayerGroup.p4: 'Player 4',
		PlayerGroup.p5: 'Player 5',
		PlayerGroup.p6: 'Player 6',
		PlayerGroup.p7: 'Player 7',
		PlayerGroup.p8: 'Player 8',
		PlayerGroup.p9: 'Player 9',
		PlayerGroup.p10: 'Player 10',
		PlayerGroup.p11: 'Player 11',
		PlayerGroup.p12: 'Player 12',
		PlayerGroup.current_player: 'Current Player',
		PlayerGroup.foes: 'Foes',
		PlayerGroup.allies: 'Allies',
		PlayerGroup.neutral_players: 'Neutral Players',
		PlayerGroup.all_players: 'All Players',
		PlayerGroup.force_1: 'Force 1',
		PlayerGroup.force_2: 'Force 2',
		PlayerGroup.force_3: 'Force 3',
		PlayerGroup.force_4: 'Force 4',
		PlayerGroup.unused_1: 'Unused 1',
		PlayerGroup.unused_2: 'Unused 2',
		PlayerGroup.unused_3: 'Unused 3',
		PlayerGroup.unused_4: 'Unused 4',
		PlayerGroup.non_allied_victory_players: 'Non Allied Victory Players'
	})
	
	def name(self) -> str:
		return 'Player'
	
	def help(self) -> str:
		return 'A number in the range 0 to 255 (with or without the keyword Player before it), or any keyword from this list: Current Player, Foes, Allies, Neutral Players, All Players, Force 1, Force 2, Force 3, Force 4, Unused 1, Unused 2, Unused 3, Unused 4, Non Allied Victory Players'

	def keywords(self) -> tuple[str, ...]:
		return ('Current Player', 'Neutral Players', 'All Players', 'Non Allied Victory Players', 'Player', 'Foes', 'Allies', 'Force', 'Unused')

	def __init__(self, *, target: bool = False):
		self.target = target

	def decompile(self, player_group: int) -> str:
		if player_group in PlayerParameter.OPTIONS:
			return PlayerParameter.OPTIONS[player_group]
		return str(player_group)

	def _compile(self, value: str) -> int:
		if PlayerParameter.OPTIONS.has_value(value):
			return PlayerParameter.OPTIONS.key_of(value)
		if value.startswith('Player '):
			value = value[7:]
		try:
			player_group = int(value)
			if -1 < player_group < 256:
				return player_group
		except:
			pass
		raise PyMSError('Parameter',f"'{value}' is an invalid Player (value must be in the range 0 to 255, or on of the keywords: Current Player, Foes, Allies, Neutral Players, All Players, Force 1, Force 2, Force 3, Force 4, Unused 1, Unused 2, Unused 3, Unused 4, Non Allied Victory Players)")

	def condition_decompile(self, condition: Condition, trg: TRG) -> str:
		return self.decompile(condition.player_group)

	def condition_compile(self, value: str, condition: Condition, trg: TRG) -> (PyMSWarning | None):
		condition.player_group = self._compile(value)
		return None

	def action_decompile(self, action: Action, trg: TRG) -> str:
		if self.target:
			return self.decompile(action.target_player_group)
		else:
			return self.decompile(action.player_group)

	def action_compile(self, value: str, action: Action, trg: TRG) -> (PyMSWarning | None):
		if self.target:
			action.target_player_group = self._compile(value)
		else:
			action.player_group = self._compile(value)
		return None

class ComparisonParameter(ConditionParameter, HasKeywords):
	OPTIONS = Bidict({
		Comparison.at_least: 'At Least',
		Comparison.at_most: 'At Most',
		Comparison.exactly: 'Exactly'
	})
	def name(self) -> str:
		return 'Comparison'

	def help(self) -> str:
		return 'One of the keywords: At Least, Exactly, At Most'

	def keywords(self) -> tuple[str, ...]:
		return tuple(ComparisonParameter.OPTIONS.values())

	def condition_decompile(self, condition: Condition, trg: TRG) -> str:
		if condition.comparison in ComparisonParameter.OPTIONS:
			return ComparisonParameter.OPTIONS[condition.comparison]
		return str(condition.comparison)

	def condition_compile(self, value: str, condition: Condition, trg: TRG) -> (PyMSWarning | None):
		if ComparisonParameter.OPTIONS.has_value(value):
			condition.comparison = ComparisonParameter.OPTIONS.key_of(value)
			return None
		try:
			num = int(value)
			if -1 < num < 256:
				condition.comparison = num
				return PyMSWarning('Parameter', f"'{value}' is not an expected Comparison (value should be one of the keywords: At Least, Exactly, At Most)")
		except:
			pass
		raise PyMSError('Parameter',f"'{value}' is an invalid Comparison (value must be one of the keywords: At Least, Exactly, At Most)")

class UnitTypeParameter(ConditionParameter, ActionParameter, HasKeywords):
	OPTIONS = Bidict({
		UnitType.none: 'None',
		UnitType.any: 'Any Unit',
		UnitType.men: 'Men',
		UnitType.buildings: 'Buildings',
		UnitType.factories: 'Factories'
	})

	def name(self) -> str:
		return 'TUnit'

	def help(self) -> str:
		return 'A unit ID from 0 to 227 (and extended unit ID 233 to 65535), a full unit name (in the TBL, its the part before the first <0>), or a type from the list: None, Any Unit, Men, Buildings, Factories'

	def keywords(self) -> tuple[str, ...]:
		return tuple(UnitTypeParameter.OPTIONS.values())

	@staticmethod
	def unit_name(tbl_string: str) -> str:
		components = tbl_string.split('\x00')
		name = components[0]
		if len(components) > 1 and components[1] != '*':
			name = '\x00'.join(components[:2])
		return TBL.decompile_string(name, include='(,)')

	def _decompile(self, unit_type: int, trg: TRG) -> str:
		if unit_type in UnitTypeParameter.OPTIONS:
			return UnitTypeParameter.OPTIONS[unit_type]
		if -1 < unit_type < 228 and trg.stat_txt:
			return UnitTypeParameter.unit_name(trg.stat_txt.strings[unit_type])
		return str(unit_type)

	def _compile(self, value: str, trg: TRG) -> int:
		if UnitTypeParameter.OPTIONS.has_value(value):
			return UnitTypeParameter.OPTIONS.key_of(value)
		try:
			unit_type = int(value)
			if -1 < unit_type < 65536:
				return unit_type
		except:
			pass
		if trg.stat_txt:
			for unit_id,string in enumerate(trg.stat_txt.strings[:228]):
				if value == UnitTypeParameter.unit_name(string):
					return unit_id
		raise PyMSError('Parameter',f"'{value}' is an invalid TUnit (value must be in the range 0 to 227, a full unit name, or a type from the list: None, Any Unit, Men, Buildings, Factories)")

	def condition_decompile(self, condition: Condition, trg: TRG) -> str:
		return self._decompile(condition.unit_type, trg)

	def condition_compile(self, value: str, condition: Condition, trg: TRG) -> PyMSWarning | None:
		condition.unit_type = self._compile(value, trg)
		condition.flags |= ConditionFlag.unit_used
		return None

	def action_decompile(self, action: Action, trg: TRG) -> str:
		return self._decompile(action.unit_type, trg)

	def action_compile(self, value: str, action: Action, trg: TRG) -> PyMSWarning | None:
		action.unit_type = self._compile(value, trg)
		action.flags |= ActionFlag.unit_used
		return None

class LocationParameter(ConditionParameter, ActionParameter, HasKeywords):
	def name(self) -> str:
		return 'Location'

	def help(self) -> str:
		return 'A number in the range 0 to 254 (with or without the keyword Location before it), or the keyword Anywhere (Anywhere is Location 63)'

	def keywords(self) -> tuple[str, ...]:
		return ('Location', 'Anywhere')

	def __init__(self, *, destination: bool = False) -> None:
		self.destination = destination

	def _decompile(self, location_index: int) -> str:
		if location_index == 64:
			return 'Anywhere'
		return f'Location {location_index - 1}'

	def _compile(self, value: str) -> int:
		if value == 'Anywhere':
			return 64
		if value.startswith('Location '):
			value = value[9:]
		try:
			location_index = int(value)
			if 0 <= location_index < 255:
				return location_index + 1
		except:
			pass
		raise PyMSError('Parameter', f"'{value}' is an invalid Location (value must be in the range 0 to 254, or the keyword Anywhere, which is Location 63)")

	def condition_decompile(self, condition: Condition, trg: TRG) -> str:
		return self._decompile(condition.location_index)

	def condition_compile(self, value: str, condition: Condition, trg: TRG) -> PyMSWarning | None:
		condition.location_index = self._compile(value)
		return None

	def action_decompile(self, action: Action, trg: TRG) -> str:
		if self.destination:
			return self._decompile(action.destination_location_index)
		else:
			return self._decompile(action.location_index)

	def action_compile(self, value: str, action: Action, trg: TRG) -> (PyMSWarning | None):
		if self.destination:
			action.destination_location_index = self._compile(value)
		else:
			action.location_index = self._compile(value)
		return None

class ResourceTypeParameter(ConditionParameter, ActionParameter, HasKeywords):
	OPTIONS = Bidict({
		ResourceType.ore: 'Ore',
		ResourceType.gas: 'Gas',
		ResourceType.ore_and_gas: 'Ore and Gas'
	})

	def name(self) -> str:
		return 'ResType'

	def help(self) -> str:
		return 'One of the keywords: Ore, Gas, Ore and Gas'

	def keywords(self) -> tuple[str, ...]:
		return tuple(sorted(ResourceTypeParameter.OPTIONS.values(), key=len, reverse=True))

	def _decompile(self, resource_type: int) -> str:
		if resource_type in ResourceTypeParameter.OPTIONS:
			return ResourceTypeParameter.OPTIONS[resource_type]
		return str(resource_type)

	def _compile(self, value: str) -> tuple[int, PyMSWarning | None]:
		if ResourceTypeParameter.OPTIONS.has_value(value):
			return (ResourceTypeParameter.OPTIONS.key_of(value), None)
		try:
			num = int(value)
			if -1 < num < 256:
				return (num, PyMSWarning('Parameter', f"'{value}' is not an expected Comparison (value should be one of the keywords: At Least, Exactly, At Most)"))
		except:
			pass
		raise PyMSError('Parameter',f"'{value}' is an invalid Comparison (value must be one of the keywords: At Least, Exactly, At Most)")

	def condition_decompile(self, condition: Condition, trg: TRG) -> str:
		return self._decompile(condition.resource_type)

	def condition_compile(self, value: str, condition: Condition, trg: TRG) -> PyMSWarning | None:
		condition.resource_type, warning = self._compile(value)
		return warning

	def action_decompile(self, action: Action, trg: TRG) -> str:
		return self._decompile(action.resource_type)

	def action_compile(self, value: str, action: Action, trg: TRG) -> PyMSWarning | None:
		action.resource_type, warning = self._compile(value)
		return warning

class ScoreTypeParameter(ConditionParameter, ActionParameter, HasKeywords):
	OPTIONS = Bidict({
		ScoreType.total: 'Total',
		ScoreType.units: 'Units',
		ScoreType.buildings: 'Buildings',
		ScoreType.units_and_buildings: 'Units and Buildings',
		ScoreType.kills: 'Kills',
		ScoreType.razings: 'Razings',
		ScoreType.kills_and_razings: 'Kills and Razings',
		ScoreType.custom: 'Custom'
	})

	def name(self) -> str:
		return 'ScoreType'

	def help(self) -> str:
		return 'One of the keywords: Total, Units, Buildings, Units and Buildings, Kills, Razings, Kills and Razings, Custom'

	def keywords(self) -> tuple[str, ...]:
		return tuple(sorted(ScoreTypeParameter.OPTIONS.values(), key=len, reverse=True))

	def _decompile(self, score_type: int) -> str:
		if score_type in ScoreTypeParameter.OPTIONS:
			return ScoreTypeParameter.OPTIONS[score_type]
		return str(score_type)
	
	def _compile(self, value: str) -> tuple[int, PyMSWarning | None]:
		if ScoreTypeParameter.OPTIONS.has_value(value):
			return (ScoreTypeParameter.OPTIONS.key_of(value), None)
		try:
			num = int(value)
			if -1 < num < 256:
				return (num, PyMSWarning('Parameter', f"'{value}' is not an expected ScoreType (value should be one of the keywords: Total, Units, Buildings, Units and Buildings, Razings, Kills and Razings, Custom)"))
		except:
			pass
		raise PyMSError('Parameter',f"'{value}' is an invalid ScoreType (value must be one of the keywords: Total, Units, Buildings, Units and Buildings, Razings, Kills and Razings, Custom)")

	def condition_decompile(self, condition: Condition, trg: TRG) -> str:
		return self._decompile(condition.score_type)
	
	def condition_compile(self, value: str, condition: Condition, trg: TRG) -> PyMSWarning | None:
		condition.score_type, warning = self._compile(value)
		return warning

	def action_decompile(self, action: Action, trg: TRG) -> str:
		return self._decompile(action.score_type)

	def action_compile(self, value: str, action: Action, trg: TRG) -> PyMSWarning | None:
		action.score_type, warning = self._compile(value)
		return warning

class SwitchParameter(ConditionParameter, ActionParameter, HasKeywords):
	def name(self) -> str:
		return 'Switch'

	def help(self) -> str:
		return 'A number in the range 0 to 255 (with or without the keyword Switch before it)'

	def keywords(self) -> tuple[str, ...]:
		return ('Switch',)

	def _decompile(self, switch_index: int) -> str:
		return f'Switch {switch_index}'

	def _compile(self, value: str) -> int:
		if value.startswith('Switch '):
			value = value[7:]
		try:
			switch_index = int(value)
			if -1 < switch_index < 256:
				return switch_index
		except:
			pass
		raise PyMSError('Parameter', f"'{value}' is an invalid Switch (value must be in the range 0 to 255)")

	def condition_decompile(self, condition: Condition, trg: TRG) -> str:
		return self._decompile(condition.switch_index)

	def condition_compile(self, value: str, condition: Condition, trg: TRG) -> PyMSWarning | None:
		condition.switch_index = self._compile(value)
		return None

	def action_decompile(self, action: Action, trg: TRG) -> str:
		return self._decompile(action.switch_index)

	def action_compile(self, value: str, action: Action, trg: TRG) -> PyMSWarning | None:
		action.switch_index = self._compile(value)
		return None

class SwitchStateParameter(ConditionParameter, HasKeywords):
	OPTIONS = Bidict({
		SwitchState.set: 'Set',
		SwitchState.cleared: 'Cleared'
	})

	def name(self) -> str:
		return 'SwitchState'

	def help(self) -> str:
		return 'Either the keyword Set, or Cleared'

	def keywords(self) -> tuple[str, ...]:
		return tuple(SwitchStateParameter.OPTIONS.values())

	def condition_decompile(self, condition: Condition, trg: TRG) -> str:
		if condition.switch_state in SwitchStateParameter.OPTIONS:
			return SwitchStateParameter.OPTIONS[condition.switch_state]
		return str(condition.switch_state)
	
	def condition_compile(self, value: str, condition: Condition, trg: TRG) -> PyMSWarning | None:
		if SwitchStateParameter.OPTIONS.has_value(value):
			condition.switch_state = SwitchStateParameter.OPTIONS.key_of(value)
			return None
		try:
			num = int(value)
			if -1 < num < 256:
				condition.switch_state = num
				return PyMSWarning('Parameter', f"'{value}' is not an expected SwitchState (value must be one of the keywords: Set, Cleared)")
		except:
			pass
		raise PyMSError('Parameter',f"'{value}' is an invalid SwitchState (value must be one of the keywords: Set, Cleared)")

# TODO: Support time formats?
class TimeParameter(ActionParameter):
	def name(self) -> str:
		return 'Time'

	def help(self) -> str:
		return 'Can be any number in the range 0 to 4294967295'
	
	def __init__(self, transmission: bool = False) -> None:
		self.transmission = transmission

	def action_decompile(self, action: Action, trg: TRG) -> str:
		if self.transmission:
			return str(action.transmission_duration)
		return str(action.duration)

	def action_compile(self, value: str, action: Action, trg: TRG) -> PyMSWarning | None:
		try:
			duration = int(value)
			if -1 < duration < 4294967296:
				if self.transmission:
					action.transmission_duration = duration
				else:
					action.duration = duration
				return None
		except:
			pass
		raise PyMSError('Parameter', f"'{value}' is not a valid Time (value must be a number in the range 0 to 4294967295)")

class StringParameter(ActionParameter, HasKeywords):
	def name(self) -> str:
		return 'String'

	def help(self) -> str:
		return 'A number corresponding to a string index (with or without the keyword String before it), or the keyword No String'

	def keywords(self) -> tuple[str, ...]:
		return ('String',)

	def action_decompile(self, action: Action, trg: TRG) -> str:
		if action.string_index == 0:
			return 'No String'
		return f'String {action.string_index}'

	def action_compile(self, value: str, action: Action, trg: TRG) -> PyMSWarning | None:
		if value == 'No String':
			action.string_index = 0
			return None
		if value.startswith('String '):
			value = value[7:]
		try:
			string_index = int(value)
			if -1 < string_index < 4294967296:
				action.string_index = string_index
				if string_index == 0:
					return PyMSWarning('Parameter', 'String 0 means "no string"')
				return None
		except:
			pass
		raise PyMSError('Parameter', f"'{value}' is an invalid String (value must be in the range 0 to 4294967296), or the keyword No String")

class UnitParameter(ActionParameter):
	def name(self) -> str:
		return 'Unit'
	
	def help(self) -> str:
		return 'A unit ID from 0 to 227 (and extended unit ID 233 to 65535), or a full unit name (in the TBL, its the part before the first <0>)'

	@staticmethod
	def unit_name(tbl_string: str) -> str:
		components = tbl_string.split('\x00')
		name = components[0]
		if len(components) > 1 and components[1] != '*':
			name = '\x00'.join(components[:2])
		return TBL.decompile_string(name, include='(,)')

	def action_decompile(self, action: Action, trg: TRG) -> str:
		if -1 < action.unit_type < 228 and trg.stat_txt:
			return UnitParameter.unit_name(trg.stat_txt.strings[action.unit_type])
		return str(action.unit_type)

	def action_compile(self, value: str, action: Action, trg: TRG) -> PyMSWarning | None:
		unit_type: int | None = None
		try:
			unit_type = int(value)
			if unit_type < 0 or unit_type > 65535:
				unit_type = None
		except:
			pass
		if trg.stat_txt:
			if unit_type is None:
				for unit_id,string in enumerate(trg.stat_txt.strings[:228]):
					if value == UnitParameter.unit_name(string):
						unit_type = unit_id
						break
		if unit_type is None:
			raise PyMSError('Parameter',f"'{value}' is an invalid Unit (value must be in the range 0 to 227, or a full unit name)")
		action.unit_type = unit_type
		action.flags |= ActionFlag.unit_used
		return None

class ModifierParameter(ActionParameter, HasKeywords):
	OPTIONS = Bidict({
		NumberModifier.set: 'Set To',
		NumberModifier.add: 'Add',
		NumberModifier.subtract: 'Subtract'
	})

	def name(self) -> str:
		return 'Modifier'

	def help(self) -> str:
		return 'One of the keywords: Set To, Add, Subtract'

	def keywords(self) -> tuple[str, ...]:
		return tuple(ModifierParameter.OPTIONS.values())

	def action_decompile(self, action: Action, trg: TRG) -> str:
		if action.number_modifier in ModifierParameter.OPTIONS:
			return ModifierParameter.OPTIONS[action.number_modifier]
		return str(action.number_modifier)

	def action_compile(self, value: str, action: Action, trg: TRG) -> PyMSWarning | None:
		if ModifierParameter.OPTIONS.has_value(value):
			action.number_modifier = ModifierParameter.OPTIONS.key_of(value)
			return None
		try:
			num = int(value)
			if -1 < num < 256:
				action.number_modifier = num
				return PyMSWarning('Parameter', f"'{value}' is not an expected Modifier (value should be one of the keywords: Set To, Add, Subtract)")
		except:
			pass
		raise PyMSError('Parameter',f"'{value}' is an invalid Modifier (value must be one of the keywords: Set To, Add, Subtract)")

class WAVParameter(ActionParameter, HasKeywords):
	def name(self) -> str:
		return 'WAV'

	def help(self) -> str:
		return 'A number corresponding to a WAV string index (with or without the keyword WAV before it), or the keyword No WAV'

	def keywords(self) -> tuple[str, ...]:
		return ('No WAV', 'WAV')

	def action_decompile(self, action: Action, trg: TRG) -> str:
		if action.wav_string_index == 0:
			return 'No WAV'
		return f'WAV {action.wav_string_index}'

	def action_compile(self, value: str, action: Action, trg: TRG) -> PyMSWarning | None:
		if value == 'No WAV':
			action.wav_string_index = 0
			return None
		if value.startswith('WAV '):
			value = value[4:]
		try:
			wav_string_index = int(value)
			if -1 < wav_string_index < 4294967296:
				action.wav_string_index = wav_string_index
				if wav_string_index == 0:
					return PyMSWarning('Parameter', 'WAV 0 means "No WAV"')
				return None
		except:
			pass
		raise PyMSError('Parameter', f"'{value}' is an invalid WAV (value must be in the range 1 to 4294967296, or the keyword No WAV)")

class DisplayParameter(ActionParameter, HasKeywords):
	def name(self) -> str:
		return 'Display'

	def help(self) -> str:
		return 'Either the keyword Always Display, or Only With Subtitles'

	def keywords(self) -> tuple[str, ...]:
		return ('Always Display', 'Only With Subtitles')

	def action_decompile(self, action: Action, trg: TRG) -> str:
		if action.flags & ActionFlag.always_display:
			return 'Always Display'
		return 'Only With Subtitles'

	def action_compile(self, value: str, action: Action, trg: TRG) -> PyMSWarning | None:
		if value == 'Always Display':
			action.flags |= ActionFlag.always_display
		elif value == 'Only With Subtitles':
			action.flags &= ~ActionFlag.always_display
		else:
			raise PyMSError('Parameter', f"'{value}' is an invalid Display type (value must be one of the keywords: Always Display, Only With Subtitles)")
		return None

class QuantityParameter(ActionParameter, HasKeywords):
	def name(self) -> str:
		return 'Quantity'

	def help(self) -> str:
		return 'Can be any number in the range 1 to 4294967295, or the keyword All'
	
	def keywords(self) -> tuple[str, ...]:
		return ('All',)

	def action_decompile(self, action: Action, trg: TRG) -> str:
		if action.quantity == 0:
			return 'All'
		return str(action.quantity)

	def action_compile(self, value: str, action: Action, trg: TRG) -> PyMSWarning | None:
		if value == 'All':
			action.quantity = 0
			return None
		try:
			number = int(value)
			if -1 < number < 4294967296:
				action.quantity = number
				if number == 0:
					return PyMSWarning('Parameter', 'Quantity 0 means "all"')
				return None
		except:
			pass
		raise PyMSError('Parameter', f"'{value}' is not a valid Quantity (value must be a number in the range 1 to 4294967295, or the keyword All)")

class PropertiesParameter(ActionParameter, HasKeywords):
	def name(self) -> str:
		return 'Properties'

	def help(self) -> str:
		return 'A number corresponding to a unit Properties index (1-64, with or without the keyword Properties before it)'

	def keywords(self) -> tuple[str, ...]:
		return ('Properties',)

	def action_decompile(self, action: Action, trg: TRG) -> str:
		return f'Properties {action.unit_properties_index+1}'

	def action_compile(self, value: str, action: Action, trg: TRG) -> PyMSWarning | None:
		if value.startswith('Properties '):
			value = value[11:]
		try:
			index = int(value)
			if 0 < index < 65:
				action.unit_properties_index = index - 1
				action.flags |= ActionFlag.unit_property_used
				return None
		except:
			pass
		raise PyMSError('Parameter', f"'{value}' is an invalid unit Properties index (value must be in the range 1 to 64, with or without the keyword Properties before it)")

class SwitchActionParameter(ActionParameter, HasKeywords):
	OPTIONS = Bidict({
		SwitchAction.set: 'Set',
		SwitchAction.clear: 'Clear',
		SwitchAction.toggle: 'Toggle',
		SwitchAction.randomize: 'Randomize'
	})

	def name(self) -> str:
		return 'SwitchAction'

	def help(self) -> str:
		return 'One of the keywords: Set, Clear, Toggle, Randomize'

	def keywords(self) -> tuple[str, ...]:
		return tuple(SwitchActionParameter.OPTIONS.values())

	def action_decompile(self, action: Action, trg: TRG) -> str:
		if action.switch_action in SwitchActionParameter.OPTIONS:
			return SwitchActionParameter.OPTIONS[action.switch_action]
		return str(action.switch_action)
	
	def action_compile(self, value: str, action: Action, trg: TRG) -> PyMSWarning | None:
		if SwitchActionParameter.OPTIONS.has_value(value):
			action.switch_action = SwitchActionParameter.OPTIONS.key_of(value)
			return None
		try:
			num = int(value)
			if -1 < num < 256:
				action.switch_action = num
				return PyMSWarning('Parameter', f"'{value}' is not an expected SwitchAction (value must be one of the keywords: Set, Clear, Toggle, Randomize)")
		except:
			pass
		raise PyMSError('Parameter',f"'{value}' is an invalid SwitchAction (value must be one of the keywords: Set, Clear, Toggle, Randomize)")

class StateActionParameter(ActionParameter, HasKeywords):
	OPTIONS = Bidict({
		StateAction.set: 'Set',
		StateAction.clear: 'Clear',
		StateAction.toggle: 'Toggle'
	})

	def name(self) -> str:
		return 'StateAction'

	def help(self) -> str:
		return 'One of the keywords: Set, Clear, Toggle'

	def keywords(self) -> tuple[str, ...]:
		return tuple(StateActionParameter.OPTIONS.values())

	def action_decompile(self, action: Action, trg: TRG) -> str:
		if action.state_action in StateActionParameter.OPTIONS:
			return StateActionParameter.OPTIONS[action.state_action]
		return str(action.state_action)
	
	def action_compile(self, value: str, action: Action, trg: TRG) -> PyMSWarning | None:
		if StateActionParameter.OPTIONS.has_value(value):
			action.state_action = StateActionParameter.OPTIONS.key_of(value)
			return None
		try:
			num = int(value)
			if -1 < num < 256:
				action.state_action = num
				return PyMSWarning('Parameter', f"'{value}' is not an expected StateAction (value must be one of the keywords: Set, Clear, Toggle)")
		except:
			pass
		raise PyMSError('Parameter',f"'{value}' is an invalid StateAction (value must be one of the keywords: Set, Clear, Toggle)")

# TODO: AIScript
class AIScriptParameter(ActionParameter):
	def name(self) -> str:
		return 'AIScript'

	def help(self) -> str:
		return 'The name of an AIScript, or the four character AIScript ID'

	def __init__(self, *, location_based: bool) -> None:
		self.location_based = location_based

	def action_decompile(self, action: Action, trg: TRG) -> str:
		ai_id = struct.pack('<L', action.ai_script_id).decode('utf-8')
		# if ai_id in trg.ais[0][0]:
		# 	return trg.ais[0][0][ai_id]
		# if ai_id in trg.ais[1][0]:
		# 	return trg.ais[1][0][ai_id]
		return ai_id

	def action_compile(self, value: str, action: Action, trg: TRG) -> PyMSWarning | None:
		ai_script_id: str | None = None
		# if value in trg.ais_rev[0][0]:
		# 	ai_script_id = trg.ais_rev[0][0][value]
		# elif value in trg.ais_rev[1][0]:
		# 	ai_script_id = trg.ais_rev[1][0][value]
		if len(value) == 4:
			ai_script_id = value
		if ai_script_id is None:
			raise PyMSError('Parameter', f"'{value}' is an invalid AIScript (value must be the name of an AIScript, or the four character AIScript ID)")
		action.ai_script_id = int(struct.unpack('<L', ai_script_id.encode('utf-8'))[0])
		# if not ai_script_id in trg.ais[0][0] and not ai_script_id in trg.ais[1][0]:
		# 	return PyMSWarning('Parameter', f"'{value}' is an recongnized AIScript")
		# TODO: Fix AIScript checks
		# if self.location_based and AISCRIPT DOESN'T USE LOCATION:
		# 	return PyMSWarning('Parameter', f"AIScript '{value}' doesn't use a location")
		# elif not self.location_based and AISCRIPT USES LOCATION:
		# 	return PyMSWarning('Parameter', f"AIScript '{value}' uses a location")
		return None

class OrderParameter(ActionParameter, HasKeywords):
	OPTIONS = Bidict({
		Order.move: 'Move',
		Order.patrol: 'Patrol',
		Order.attack: 'Attack',
	})

	def name(self) -> str:
		return 'Order'

	def help(self) -> str:
		return 'One of the keywords: Move, Patrol, Attack'

	def keywords(self) -> tuple[str, ...]:
		return tuple(OrderParameter.OPTIONS.values())

	def action_decompile(self, action: Action, trg: TRG) -> str:
		if action.order in OrderParameter.OPTIONS:
			return OrderParameter.OPTIONS[action.order]
		return str(action.order)

	def action_compile(self, value: str, action: Action, trg: TRG) -> PyMSWarning | None:
		if OrderParameter.OPTIONS.has_value(value):
			action.order = OrderParameter.OPTIONS.key_of(value)
			return None
		try:
			num = int(value)
			if -1 < num < 256:
				action.order = num
				return PyMSWarning('Parameter', f"'{value}' is not an expected Order (value must be one of the keywords: Move, Patrol, Attack)")
		except:
			pass
		raise PyMSError('Parameter',f"'{value}' is an invalid Order (value must be one of the keywords: Move, Patrol, Attack)")

class PercentageParameter(ActionParameter):
	def name(self) -> str:
		return 'Percentage'

	def help(self) -> str:
		return 'A number from 0 to 100 (with or without a trailing %)'

	def action_decompile(self, action: Action, trg: TRG) -> str:
		return f'{action.number}%'

	def action_compile(self, value: str, action: Action, trg: TRG) -> PyMSWarning | None:
		if value.endswith('%'):
			value = value[:-1]
		try:
			number = int(value)
			if -1 < number < 4294967296:
				action.number = number
				if number > 100:
					return PyMSWarning('Parameter', f"'{value}' is larger than 100%")
				return None
		except:
			pass
		raise PyMSError('Paramater', f"'{value}' is not a valid Number (value must be a number in the range 0 to 4294967295)")

class AllianceStatusParameter(ActionParameter, HasKeywords):
	OPTIONS = Bidict({
		AllianceStatus.enemy: 'Enemy',
		AllianceStatus.ally: 'Ally',
		AllianceStatus.allied_victory: 'Allied Victory'
	})

	def name(self) -> str:
		return 'AllyStatus'

	def help(self) -> str:
		return 'One of the keywords: Enemy, Ally, Allied Victory'

	def keywords(self) -> tuple[str, ...]:
		return tuple(AllianceStatusParameter.OPTIONS.values())

	def action_decompile(self, action: Action, trg: TRG) -> str:
		if action.alliance_status in AllianceStatusParameter.OPTIONS:
			return AllianceStatusParameter.OPTIONS[action.alliance_status]
		return str(action.alliance_status)

	def action_compile(self, value: str, action: Action, trg: TRG) -> PyMSWarning | None:
		if AllianceStatusParameter.OPTIONS.has_value(value):
			action.alliance_status = AllianceStatusParameter.OPTIONS.key_of(value)
			return None
		try:
			num = int(value)
			if -1 < num < 256:
				action.alliance_status = num
				return PyMSWarning('Parameter', f"'{value}' is not an expected AllyStatus (value must be one of the keywords: Enemy, Ally, Allied Victory)")
		except:
			pass
		raise PyMSError('Parameter',f"'{value}' is an invalid AllyStatus (value must be one of the keywords: Enemy, Ally, Allied Victory)")

class SlotParameter(ActionParameter, HasKeywords):
	def name(self) -> str:
		return 'Slot'

	def help(self) -> str:
		return 'A number from 1 to 4 (with or without they keyword Slot before it)'

	def keywords(self) -> tuple[str, ...]:
		return ('Slot',)

	def action_decompile(self, action: Action, trg: TRG) -> str:
		return f'Slot {action.slot + 1}'

	def action_compile(self, value: str, action: Action, trg: TRG) -> PyMSWarning | None:
		if value.startswith('Slot '):
			value = value[5:]
		try:
			slot = int(value) - 1
			if -1 < slot < 4294967296:
				action.slot = slot
				if slot > 4:
					return PyMSWarning('Parameter', f"'{value}' is not an expected Slot (value must be a number from 1 to 4, with or without they keyword Slot before it)")
				return None
		except:
			pass
		raise PyMSError('Parameter', f"'{value}' is an invalid Slot (value must be a number from 1 to 4, with or without they keyword Slot before it)")

class RawFieldParameter(ConditionParameter, ActionParameter):
	limit: int 

	def name(self) -> str:
		return 'Raw'

	def help(self) -> str:
		return f'Any number in the range 0 to {self.limit}'

	def __init__(self, field_index: int) -> None:
		self.field_index = field_index

	def _compile(self, value: str) -> int:
		try:
			number = int(value)
			if -1 < number <= self.limit:
				return number
		except:
			pass
		raise PyMSError('Paramater', f"'{value}' is not a valid Raw number for this field (value must be a number in the range 0 to {self.limit})")

	def condition_decompile(self, condition: Condition, trg: TRG) -> str:
		return str(condition._fields[self.field_index])

	def condition_compile(self, value: str, condition: Condition, trg: TRG) -> PyMSWarning | None:
		condition.fields[self.field_index] = self._compile(value)
		return None

	def action_decompile(self, action: Action, trg: TRG) -> str:
		return str(action.fields[self.field_index])

	def action_compile(self, value: str, action: Action, trg: TRG) -> PyMSWarning | None:
		action.fields[self.field_index] = self._compile(value)
		return None

class LongParameter(RawFieldParameter):
	limit = 4294967295

	def name(self) -> str:
		return 'Long'

class ShortParamater(RawFieldParameter):
	limit = 65535

	def name(self) -> str:
		return 'Short'

class ByteParameter(RawFieldParameter):
	limit = 255

	def name(self) -> str:
		return 'Byte'

class MemoryParameter(ConditionParameter, ActionParameter):
	def name(self) -> str:
		return 'Memory'

	def help(self) -> str:
		return 'A memory address in hex (prefixed with 0x), or decimal'

	def _decompile(self, unit: int, player: int) -> str:
		address = 0x0058A364 + (unit * 48) + (player * 4)
		address %= Struct.l_u32.max + 1
		return f"{address:#010X}"

	def _compile(self, value: str) -> int:
		try:
			if value.startswith('0x'):
				address = int(value, 16)
			else:
				address = int(value)
		except:
			raise PyMSError('Paramater', f"'{value}' is not a valid Memory (value must be in hex prefixed with 0x, or decimal")
		if address % 4:
			raise PyMSError('Parameter', 'Memory must be a multiple of 4')
		address -= 0x0058A364
		while address < 0:
			address += Struct.l_u32.max + 1
		player = address // 4
		if player > Struct.l_u32.max:
			raise PyMSError('Parameter', 'Memory address is too high')
		return player

	def condition_decompile(self, condition: Condition, trg: TRG) -> str:
		return self._decompile(condition.unit_type, condition.player_group)

	def condition_compile(self, value: str, condition: Condition, trg: TRG) -> PyMSWarning | None:
		player = self._compile(value)
		condition.unit_type = 0
		condition.flags |= ConditionFlag.unit_used
		condition.player_group = player
		return None

	def action_decompile(self, action: Action, trg: TRG) -> str:
		return self._decompile(action.unit_type, action.player_group)

	def action_compile(self, value: str, action: Action, trg: TRG) -> PyMSWarning | None:
		player = self._compile(value)
		action.unit_type = 0
		action.flags |= ActionFlag.unit_used
		action.player_group = player
		return None
