
from .CodeGeneratorVariable import CodeGeneratorVariable
from .CodeGeneratorRange import CodeGeneratorTypeRange
from .CodeGeneratorMath import CodeGeneratorTypeMath
from .CodeGeneratorList import CodeGeneratorTypeList, CodeGeneratorTypeListRepeaterRepeatInvertedOnce

from ...Utilities import JSON

from dataclasses import dataclass

from typing import Self

@dataclass
class GeneratorPreset(JSON.Codable):
	name: str
	code: str
	variables: list[CodeGeneratorVariable]

	@classmethod
	def from_json(cls, json: JSON.Object) -> Self:
		return cls(
			JSON.get(json, 'name', str),
			JSON.get(json, 'code', str),
			JSON.get_array(json, 'variables', CodeGeneratorVariable)
		)

	def to_json(self) -> JSON.Object:
		return {
			'name': self.name,
			'code': self.code,
			'variables': list(variable.to_json() for variable in self.variables)
		}

DEFAULT_PRESETS = [
	GeneratorPreset(
		name='Play Frames',
		code="""\
	playfram            $frame
	wait                2""",
		variables=[
			CodeGeneratorVariable(
				name='frame',
				generator=CodeGeneratorTypeRange(
					start=0,
					stop=20,
					step=1
				)
			)
		]
	),
	GeneratorPreset(
		name='Play Frames', 
		code="""\
	playfram            $frame
	wait                2""", 
		variables=[
			CodeGeneratorVariable(
				name='frame',
				generator=CodeGeneratorTypeRange(
					start=0,
					stop=20,
					step=1
				)
			)
		]
	), 
	GeneratorPreset(
		name='Play Framesets', 
		code="""\
	playfram            %frameset
	wait                2""", 
		variables=[
			CodeGeneratorVariable(
				name='frameset',
				generator=CodeGeneratorTypeRange(
					start=0, 
					stop=51, 
					step=17
				)
			)
		]
	),
	GeneratorPreset(
		name='Play Framesets (Advanced)', 
		code="""\
	playfram            %frame
	wait                2""", 
		variables=[
			CodeGeneratorVariable(
				name='frameset',
				generator=CodeGeneratorTypeRange(
					start=0, 
					stop=20, 
					step=1
				)
			), 
			CodeGeneratorVariable(
				name='frame',
				generator=CodeGeneratorTypeMath('$frameset * 17')
			)
		]
	),
	GeneratorPreset(
		name='Hover Bobbing', 
		code="""\
	setvertpos          $offset
	waitrand            8 10""", 
		variables=[
			CodeGeneratorVariable(
				name='offset',
				generator=CodeGeneratorTypeList(
					values=[
						'0', 
						'1', 
						'2'
					], 
					repeater=CodeGeneratorTypeListRepeaterRepeatInvertedOnce()
				)
			)
		]
	)
]
