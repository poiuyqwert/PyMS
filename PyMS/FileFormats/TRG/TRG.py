
from .Trigger import Trigger
from .UnitProperties import UnitProperties, properties_definitions, PropertyFieldDefinition, PropertyStateDefinition
from .Constants import ConditionFlag, ActionFlag
from .CodeHandler import TRGLexer
from .Parameters import PlayerParameter, PlayerGroup
from . import Conditions
from . import Actions

from ...FileFormats import TBL
from ...FileFormats.AIBIN import AIBIN

from ...Utilities import IO
from ...Utilities.PyMSError import PyMSError
from ...Utilities.PyMSWarning import PyMSWarning
from ...Utilities.BytesScanner import BytesScanner
from ...Utilities import Struct
from ...Utilities.CodeHandlers import Tokens
from ...Utilities.CodeHandlers.Lexer import Stop

import enum, re

class Format(enum.Enum):
	normal = 0
	briefing = 1
	got = 2

class TRG:
	HEADER = b'qw\x986\x18\x00\x00\x00'

	def __init__(self, stat_txt: TBL.TBL | None = None, aiscript: AIBIN.AIBIN | None = None) -> None:
		self.triggers: list[Trigger] = []
		self.strings: dict[int, str] = {}
		self.unit_properties: dict[int, UnitProperties] = {}
		self.format = Format.normal

		self.stat_txt: TBL.TBL | None = stat_txt
		self.aiscript: AIBIN.AIBIN | None = aiscript

	STRING_STRUCT = Struct.l_str(2048)
	def load(self, input: IO.AnyInputBytes, format: Format = Format.normal) -> None:
		with IO.InputBytes(input) as f:
			data = f.read()
		scanner = BytesScanner(data)
		if format != Format.got and not scanner.matches(TRG.HEADER):
			raise PyMSError('Load', 'Not a valid .trg file (missing header), could possibly be a GOT .trg file')
		triggers: list[Trigger] = []
		strings: dict[int, str] = {}
		unit_properties: dict[int, UnitProperties] = {}
		try:
			while not scanner.at_end():
				trigger = scanner.scan(Trigger)
				triggers.append(trigger)
				if format != Format.got:
					for action in trigger.actions:
						if action.string_index:
							strings[action.string_index] = scanner.scan(TRG.STRING_STRUCT)
						if action.flags & ActionFlag.unit_property_used:
							props = scanner.scan(UnitProperties)
							unit_properties[action.unit_properties_index] = props
		except Exception as e:
			raise PyMSError('Load', 'Unsupported TRG file, could possibly be corrupt')
		self.triggers = triggers
		self.strings = strings
		self.unit_properties = unit_properties
		self.format = format

	def save(self, output: IO.AnyOutputBytes, format: Format | None = None) -> list[PyMSWarning]:
		save_format = self.format if format is None else format
		warnings: list[PyMSWarning] = []
		is_missiong_briefing: bool | None = None
		with IO.OutputBytes(output) as f:
			if save_format != Format.got:
				f.write(TRG.HEADER)
			for trigger in self.triggers:
				f.write(trigger.pack())
				if is_missiong_briefing is None:
					is_missiong_briefing = trigger.is_missing_briefing
				elif trigger.is_missing_briefing != is_missiong_briefing:
					warnings.append(PyMSWarning('Save', 'There is a mix of missing briefing and normal triggers'))
				for action in trigger.actions:
					if action.string_index:
						string: str
						if action.string_index in self.strings:
							string = self.strings[action.string_index]
						else:
							string = ''
							warnings.append(PyMSWarning('Save', f'String {action.string_index} is missing, saving an empty string'))
						f.write(TRG.STRING_STRUCT.pack(string))
					if action.flags & ActionFlag.unit_property_used:
						properties: UnitProperties
						if action.flags & ActionFlag.unit_property_used:
							properties = self.unit_properties[action.unit_properties_index]
						else:
							properties = UnitProperties()
							warnings.append(PyMSWarning('Save', f'Unit properties {action.unit_properties_index} is missing, saving empty properties'))
						f.write(properties.pack())
		return warnings

	RE_NEWLINES = re.compile(r'(\r\n|\r|\n)')
	def decompile(self, output: IO.AnyOutputText, reference: bool = False) -> None:
		with IO.OutputText(output) as f:
			for string_index,raw_string in self.strings.items():
				string = TRG.RE_NEWLINES.sub('\\1  ', TBL.decompile_string(raw_string, '\r\n'))
				f.write(f'String({string_index}):\n  {string}\n\n')
			for properties_index,properties in self.unit_properties.items():
				properties.decompile(properties_index, f)
				f.write('\n\n')
			for trigger in self.triggers:
				trigger.decompile(self, f)
				f.write('\n\n')

	# TODO: Compile
	def compile(self, input: IO.AnyInputText) -> list[PyMSWarning]:
		with IO.InputText(input) as f:
			code = f.read()
		format: Format | None = None
		triggers: list[Trigger] = []
		strings: dict[int, str] = {}
		unit_properties: dict[int, UnitProperties] = {}
		warnings: list[PyMSWarning] = []

		lexer = TRGLexer(code)

		def process_conditions(trigger: Trigger) -> Tokens.Token:
			nonlocal warnings
			token = lexer.skip(Tokens.NewlineToken)
			while trigger.conditions_free:
				enabled = True
				if isinstance(token, TRGLexer.SymbolToken) and token.raw_value == '-':
					enabled = False
					token = lexer.next_token()
				if not isinstance(token, TRGLexer.IdentifierToken):
					raise PyMSError('Compile', 'Expected a condition')
				definition = Conditions.get_definition_named(token.raw_value)
				if not definition:
					raise PyMSError('Compile', 'Unknown condition name')
				token = lexer.next_token()
				if not isinstance(token, TRGLexer.SymbolToken) or token.raw_value != '(':
					raise PyMSError('Compile', 'Expected start of parameters')
				condition = definition.new_condition()
				if not enabled:
					condition.flags |= ConditionFlag.disabled
				trigger.add_condition(condition)
				token = lexer.next_token()
				for parameter in definition.parameters:
					if not isinstance(token, TRGLexer.IdentifierToken):
						raise PyMSError('Compile', 'Expected a parameter')
					try:
						if warning := parameter.condition_compile(token.raw_value, condition, self):
							warnings.append(warning)
					except PyMSError:
						raise
					except:
						raise PyMSError('Compile', 'Invalid parameter')
					token = lexer.next_token()
					if isinstance(token, TRGLexer.SymbolToken) and token.raw_value == ',':
						token = lexer.next_token()
				if not isinstance(token, TRGLexer.SymbolToken) or token.raw_value != ')':
					raise PyMSError('Compile', 'Expected end of parameters')
				token = lexer.next_token()
				if not isinstance(token, Tokens.NewlineToken):
					raise PyMSError('Compile', 'Expected end of line')
				token = lexer.skip(Tokens.NewlineToken)
				if isinstance(token, TRGLexer.KeywordsToken):
					break
			return token

		def process_actions(trigger: Trigger) -> Tokens.Token:
			nonlocal warnings
			token = lexer.skip(Tokens.NewlineToken)
			while trigger.actions_free:
				enabled = True
				if isinstance(token, TRGLexer.SymbolToken) and token.raw_value == '-':
					enabled = False
					token = lexer.next_token()
				if not isinstance(token, TRGLexer.IdentifierToken):
					raise PyMSError('Compile', 'Expected an action')
				definition = Actions.get_action_named(token.raw_value)
				if not definition:
					raise PyMSError('Compile', 'Unknown condition name')
				token = lexer.next_token()
				if not isinstance(token, TRGLexer.SymbolToken) or token.raw_value != '(':
					raise PyMSError('Compile', 'Expected start of parameters')
				action = definition.new_action()
				if not enabled:
					action.flags |= ActionFlag.disabled
				trigger.add_action(action)
				token = lexer.next_token()
				for parameter in definition.parameters:
					if not isinstance(token, TRGLexer.IdentifierToken):
						raise PyMSError('Compile', 'Expected a parameter')
					try:
						if warning := parameter.action_compile(token.raw_value, action, self):
							warnings.append(warning)
					except PyMSError:
						raise
					except:
						raise PyMSError('Compile', 'Invalid parameter')
					token = lexer.next_token()
					if isinstance(token, TRGLexer.SymbolToken) and token.raw_value == ',':
						token = lexer.next_token()
				if not isinstance(token, TRGLexer.SymbolToken) or token.raw_value != ')':
					raise PyMSError('Compile', 'Expected end of parameters')
				token = lexer.next_token()
				if not isinstance(token, Tokens.NewlineToken):
					raise PyMSError('Compile', 'Expected end of line')
				token = lexer.skip(Tokens.NewlineToken)
				if isinstance(token, (TRGLexer.KeywordsToken, Tokens.EOFToken)):
					break
			return token

		def process_trigger() -> Tokens.Token:
			nonlocal triggers
			token = lexer.next_token()
			if not isinstance(token, TRGLexer.SymbolToken) or token.raw_value != '(':
				raise PyMSError('Compile', "Expected a '(' to start the list of players for Trigger")
			trigger = Trigger()
			triggers.append(trigger)
			player_param = PlayerParameter()
			token = lexer.next_token()
			while isinstance(token, TRGLexer.IdentifierToken):
				try:
					player = player_param._compile(token.raw_value)
				except PyMSError:
					raise
				except:
					raise PyMSError('Compile', 'Invalid player')
				if player > PlayerGroup.non_allied_victory_players:
					raise PyMSError('Compile', 'Invalid player')
				if trigger.execution.player_groups[player]:
					raise PyMSError('Compile', 'Player already specified')
				trigger.execution.player_groups[player] = 1
				token = lexer.next_token()
				if isinstance(token, TRGLexer.SymbolToken) and token.raw_value == ',':
					token = lexer.next_token()
			if not isinstance(token, TRGLexer.SymbolToken) or token.raw_value != ')':
				raise PyMSError('Compile', 'Expected end of players for Trigger')
			token = lexer.next_token()
			if not isinstance(token, TRGLexer.SymbolToken) or token.raw_value != ':':
				raise PyMSError('Compile', 'Expected start of trigger body')
			token = lexer.next_token()
			if not isinstance(token, Tokens.NewlineToken):
				raise PyMSError('Compile', 'Expected end of line')
			token = lexer.skip(Tokens.NewlineToken)
			if format == Format.normal:
				if not isinstance(token, TRGLexer.KeywordsToken) or token.raw_value != 'Conditions:':
					raise PyMSError('Compile', 'Expected conditions')
				token = lexer.next_token()
				if not isinstance(token, Tokens.NewlineToken):
					raise PyMSError('Compile', 'Expected end of line')
				token = process_conditions(trigger)
			if not isinstance(token, TRGLexer.KeywordsToken) or token.raw_value != 'Actions:':
				raise PyMSError('Compile', 'Expected actions')
			token = process_actions(trigger)
			return token

		def process_string():
			nonlocal strings
			try:
				id_token = lexer.get_token(Tokens.IntegerToken)
			except:
				raise PyMSError('Compile', 'Expected a string id')
			token = lexer.next_token()
			if not isinstance(token, TRGLexer.SymbolToken) or token.raw_value != ')':
				raise PyMSError('Compile', 'Expected closing parenthesis')
			token = lexer.next_token()
			if not isinstance(token, TRGLexer.SymbolToken) or token.raw_value != ':':
				raise PyMSError('Compile', 'Expected start of string')
			token = lexer.next_token()
			if not isinstance(token, Tokens.NewlineToken):
				raise PyMSError('Compile', 'Expected end of line')
			string_id = int(id_token.raw_value)
			if string_id in strings:
				raise PyMSError('Compile', 'String with id already defined')
			string = ''
			try:
				indent_token = lexer.get_token(Tokens.WhitespaceToken)
			except:
				raise PyMSError('Compile', 'Expected indentation for string')
			while True:
				string_token = lexer.read_open_string(lambda token: Stop.include if isinstance(token, Tokens.NewlineToken) else Stop.proceed)
				try:
					token = lexer.get_token(Tokens.WhitespaceToken)
					if not token.raw_value.startswith(indent_token.raw_value):
						string += string_token.raw_value.rstrip('\r\n')
						break
				except:
					string += string_token.raw_value.rstrip('\r\n')
					break
				string += string_token.raw_value
			strings[string_id] = string

		def process_properties() -> Tokens.Token:
			nonlocal unit_properties
			try:
				id_token = lexer.get_token(Tokens.IntegerToken)
			except:
				raise PyMSError('Compile', 'Expected a properties id')
			token = lexer.next_token()
			if not isinstance(token, TRGLexer.SymbolToken) or token.raw_value != ')':
				raise PyMSError('Compile', 'Expected closing parenthesis')
			token = lexer.next_token()
			if not isinstance(token, TRGLexer.SymbolToken) or token.raw_value != ':':
				raise PyMSError('Compile', 'Expected start of properties')
			token = lexer.next_token()
			if not isinstance(token, Tokens.NewlineToken):
				raise PyMSError('Compile', 'Expected end of line')
			properties_id = int(id_token.raw_value)
			if properties_id in strings:
				raise PyMSError('Compile', 'Properties with id already defined')
			properties = UnitProperties()
			token = lexer.next_token()
			property_found = False
			while isinstance(token, TRGLexer.IdentifierToken):
				for definition in properties_definitions:
					if token.raw_value == definition.name:
						if isinstance(definition, PropertyFieldDefinition):
							if properties.fields_available_flags & definition.flag:
								raise PyMSError('Compile', 'Property already defined')
							token = lexer.next_token()
							if not isinstance(token, TRGLexer.SymbolToken) or token.raw_value != '(':
								raise PyMSError('Compile', 'Expected open parenthesis')
							try:
								token = lexer.get_token(Tokens.IntegerToken)
								value = int(token.raw_value)
							except:
								raise PyMSError('Compile', 'Expected an integer parameter')
							if value < 0 or definition.parameter.max < value:
								raise PyMSError('Compile', 'Integer parameter too large')
							token = lexer.next_token()
							if not isinstance(token, TRGLexer.SymbolToken) or token.raw_value != ')':
								raise PyMSError('Compile', 'Expected closing parenthesis')
							token = lexer.next_token()
							if not isinstance(token, Tokens.NewlineToken):
								raise PyMSError('Compile', 'Expected end of line')
							setattr(properties, definition.attr, value)
							properties.fields_available_flags |= definition.flag
							property_found = True
						elif isinstance(definition, PropertyStateDefinition):
							if properties.state_flags & definition.flag:
								raise PyMSError('Compile', 'Property already defined')
							token = lexer.next_token()
							if not isinstance(token, TRGLexer.SymbolToken) or token.raw_value != '(':
								raise PyMSError('Compile', 'Expected open parenthesis')
							token = lexer.next_token()
							if not isinstance(token, TRGLexer.SymbolToken) or token.raw_value != ')':
								raise PyMSError('Compile', 'Expected closing parenthesis')
							token = lexer.next_token()
							if not isinstance(token, Tokens.NewlineToken):
								raise PyMSError('Compile', 'Expected end of line')
							properties.state_flags |= definition.flag
							property_found = True
						break
				else:
					raise PyMSError('Compile', 'Expected a property')
				token = lexer.next_token()
			if not property_found:
				raise PyMSError('Compile', 'No properties defined for Properties')
			unit_properties[properties_id] = properties
			return token

		token = lexer.skip(Tokens.NewlineToken)
		while True:
			if isinstance(token, Tokens.EOFToken):
				break
			if not isinstance(token, TRGLexer.KeywordsToken):
				raise PyMSError('Compile', 'Expected start of Trigger, String, or Properties')
			if token.raw_value == 'Trigger' or token.raw_value == 'BriefingTrigger':
				trigger_format = Format.briefing if token.raw_value == 'BriefingTrigger' else Format.normal
				if format == None:
					format = trigger_format
				elif format != trigger_format:
					raise PyMSError('Compile', 'Invalid mix of Triggers and BriefingTriggers')
				token = process_trigger()
			elif token.raw_value == 'String(':
				process_string()
				token = lexer.skip(Tokens.NewlineToken)
			elif token.raw_value == 'Properties(':
				token = process_properties()
			else:
				raise PyMSError('Compile', 'Expected start of Trigger, String, or unit Properties')
		if not triggers:
			raise PyMSError('Compile', 'No triggers')
		
		self.triggers = triggers
		self.strings = strings
		self.unit_properties = unit_properties
		assert format is not None
		self.format = format
		return warnings

	def __eq__(self, other) -> bool:
		if not isinstance(other, TRG):
			return False
		if other.format != self.format:
			return False
		if other.triggers != self.triggers:
			return False
		if other.strings != self.strings:
			return False
		if other.unit_properties != self.unit_properties:
			return False
		return True
