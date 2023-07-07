
from .Trigger import Trigger
from .UnitProperties import UnitProperties, UnitPropertiesDefinition
from .Constants import ActionFlag

from ...FileFormats import TBL
from ...FileFormats.AIBIN import AIBIN

from ...Utilities import IO
from ...Utilities.PyMSError import PyMSError
from ...Utilities.PyMSWarning import PyMSWarning
from ...Utilities.BytesScanner import BytesScanner
from ...Utilities import Serialize
from ...Utilities import Struct

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
				# trigger = Trigger()
				# trigger.load_data(scanner)
				trigger = scanner.scan(Trigger)
				triggers.append(trigger)
				if format != Format.got:
					for action in trigger.actions:
						if action.string_index:
							strings[action.string_index] = scanner.scan(TRG.STRING_STRUCT)
						if action.flags & ActionFlag.unit_property_used:
							props = scanner.scan(UnitProperties)
							# props = UnitProperties()
							# props.load_data(scanner)
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
						# properties.save_data(f)
		return warnings

	RE_NEWLINES = re.compile(r'(\r\n|\r|\n)')
	def decompile(self, output: IO.AnyOutputText, reference: bool = False) -> None:
		with IO.OutputText(output) as f:
			for string_index,raw_string in self.strings.items():
				string = TRG.RE_NEWLINES.sub('\\1  ', TBL.decompile_string(raw_string, '\r\n'))
				f.write(f'String({string_index}):\n  {string}\n\n')
			if self.unit_properties:
				unit_properties = tuple((props, id) for id,props in self.unit_properties.items())
				f.write(Serialize.encode_texts(unit_properties, lambda _: UnitPropertiesDefinition))
				f.write('\n\n')
			for trigger in self.triggers:
				trigger.decompile(self, f)
				f.write('\n\n')

	# TODO: Compile
	def compile(self, input: IO.AnyInputText) -> list[PyMSWarning]:
		return []
