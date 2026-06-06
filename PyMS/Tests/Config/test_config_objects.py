
from __future__ import annotations

from ...Utilities import Config

import enum
from dataclasses import dataclass

import unittest
from unittest import mock


class Mode(enum.Enum):
	alpha = 1
	beta = 2


@dataclass
class Point:
	x: int
	y: int

	@classmethod
	def from_json(cls, data: dict) -> Point:
		return cls(x=data['x'], y=data['y'])

	def to_json(self) -> dict:
		return {'x': self.x, 'y': self.y}


class Test_String_decode(unittest.TestCase):
	def test_accepts_string(self) -> None:
		obj = Config.String(default='d')
		obj.decode('hello')
		self.assertEqual(obj.value, 'hello')

	def test_ignores_non_string(self) -> None:
		obj = Config.String(default='d')
		obj.decode(42)
		self.assertEqual(obj.value, 'd')

	def test_default_and_reset(self) -> None:
		obj = Config.String(default='d')
		obj.decode('hello')
		obj.reset()
		self.assertEqual(obj.value, 'd')


class Test_Int_decode(unittest.TestCase):
	def test_accepts_number(self) -> None:
		obj = Config.Int(default=0)
		obj.decode(5)
		self.assertEqual(obj.value, 5)

	def test_coerces_float_to_int(self) -> None:
		obj = Config.Int(default=0)
		obj.decode(3.9)
		self.assertEqual(obj.value, 3)

	def test_ignores_non_number(self) -> None:
		obj = Config.Int(default=7)
		obj.decode('nope')
		self.assertEqual(obj.value, 7)

	def test_clamps_to_upper_limit(self) -> None:
		obj = Config.Int(default=0, limits=(0, 10))
		obj.decode(99)
		self.assertEqual(obj.value, 10)

	def test_clamps_to_lower_limit(self) -> None:
		obj = Config.Int(default=0, limits=(5, 10))
		obj.decode(-1)
		self.assertEqual(obj.value, 5)

	def test_within_limits_unchanged(self) -> None:
		obj = Config.Int(default=0, limits=(0, 10))
		obj.decode(7)
		self.assertEqual(obj.value, 7)


class Test_Float_decode(unittest.TestCase):
	def test_accepts_number(self) -> None:
		obj = Config.Float(default=0.0)
		obj.decode(1.5)
		self.assertEqual(obj.value, 1.5)

	def test_coerces_int_to_float(self) -> None:
		obj = Config.Float(default=0.0)
		obj.decode(4)
		self.assertEqual(obj.value, 4.0)
		self.assertIsInstance(obj.value, float)

	def test_ignores_non_number(self) -> None:
		obj = Config.Float(default=2.0)
		obj.decode('nope')
		self.assertEqual(obj.value, 2.0)

	def test_clamps_to_limits(self) -> None:
		obj = Config.Float(default=0.0, limits=(0.0, 1.0))
		obj.decode(5.0)
		self.assertEqual(obj.value, 1.0)
		obj.decode(-5.0)
		self.assertEqual(obj.value, 0.0)


class Test_Boolean_decode(unittest.TestCase):
	def test_zero_is_false(self) -> None:
		obj = Config.Boolean(default=True)
		obj.decode(0)
		self.assertIs(obj.value, False)

	def test_nonzero_is_true(self) -> None:
		obj = Config.Boolean(default=False)
		obj.decode(1)
		self.assertIs(obj.value, True)

	def test_accepts_bool(self) -> None:
		obj = Config.Boolean(default=False)
		obj.decode(True)
		self.assertIs(obj.value, True)

	def test_ignores_non_number(self) -> None:
		obj = Config.Boolean(default=True)
		obj.decode('nope')
		self.assertIs(obj.value, True)


class Test_Color(unittest.TestCase):
	def test_accepts_six_chars_with_hash(self) -> None:
		obj = Config.Color(default='#000000')
		obj.decode('#00FF00')
		self.assertEqual(obj.value, '#00FF00')

	def test_accepts_lowercase(self) -> None:
		obj = Config.Color(default='#000000')
		obj.decode('#abcdef')
		self.assertEqual(obj.value, '#abcdef')

	def test_accepts_optional_hash(self) -> None:
		obj = Config.Color(default='#000000')
		obj.decode('00FF00')
		self.assertEqual(obj.value, '00FF00')

	def test_rejects_too_short(self) -> None:
		obj = Config.Color(default='#000000')
		obj.decode('#12345')
		self.assertEqual(obj.value, '#000000')

	def test_rejects_too_long(self) -> None:
		obj = Config.Color(default='#000000')
		obj.decode('#1234567')
		self.assertEqual(obj.value, '#000000')

	def test_rejects_trailing_characters(self) -> None:
		obj = Config.Color(default='#000000')
		obj.decode('#00FF00extra')
		self.assertEqual(obj.value, '#000000')

	def test_rejects_non_string(self) -> None:
		obj = Config.Color(default='#000000')
		obj.decode(123456)
		self.assertEqual(obj.value, '#000000')

	def test_match_requires_full_six_characters(self) -> None:
		# fullmatch anchors length and rejects trailing characters.
		self.assertIsNotNone(Config.Color.RE_MATCH.fullmatch('#00FF00'))
		self.assertIsNone(Config.Color.RE_MATCH.fullmatch('#00FF00extra'))
		self.assertIsNone(Config.Color.RE_MATCH.fullmatch('#1234'))


class Test_Dictionary(unittest.TestCase):
	def test_decode_merges_matching_entries(self) -> None:
		obj: Config.Dictionary[int] = Config.Dictionary(value_type=int, defaults={'a': 1})
		obj.decode({'b': 2})
		self.assertEqual(obj.data, {'a': 1, 'b': 2})

	def test_decode_skips_wrong_value_type(self) -> None:
		obj: Config.Dictionary[int] = Config.Dictionary(value_type=int, defaults={})
		obj.decode({'b': 2, 'c': 'not an int'})
		self.assertEqual(obj.data, {'b': 2})

	def test_decode_ignores_non_dict(self) -> None:
		obj: Config.Dictionary[int] = Config.Dictionary(value_type=int, defaults={'a': 1})
		obj.decode([1, 2])
		self.assertEqual(obj.data, {'a': 1})

	def test_reset_restores_defaults_copy(self) -> None:
		obj: Config.Dictionary[int] = Config.Dictionary(value_type=int, defaults={'a': 1})
		obj.data['b'] = 2
		obj.reset()
		self.assertEqual(obj.data, {'a': 1})

	def test_reset_does_not_alias_defaults(self) -> None:
		obj: Config.Dictionary[int] = Config.Dictionary(value_type=int, defaults={'a': 1})
		obj.reset()
		obj.data['b'] = 2
		obj.reset()
		self.assertEqual(obj.data, {'a': 1})


class Test_List(unittest.TestCase):
	def test_decode_replaces_with_matching_values(self) -> None:
		obj: Config.List[int] = Config.List(value_type=int, defaults=[0])
		obj.decode([1, 2, 3])
		self.assertEqual(obj.data, [1, 2, 3])

	def test_decode_skips_wrong_value_type(self) -> None:
		obj: Config.List[int] = Config.List(value_type=int, defaults=[])
		obj.decode([1, 'x', 2])
		self.assertEqual(obj.data, [1, 2])

	def test_decode_ignores_non_list(self) -> None:
		obj: Config.List[int] = Config.List(value_type=int, defaults=[9])
		obj.decode({'a': 1})
		self.assertEqual(obj.data, [9])

	def test_reset_restores_defaults(self) -> None:
		obj: Config.List[int] = Config.List(value_type=int, defaults=[1, 2])
		obj.data.append(3)
		obj.reset()
		self.assertEqual(obj.data, [1, 2])


class Test_JSONList(unittest.TestCase):
	def test_decode_builds_objects(self) -> None:
		obj: Config.JSONList[Point] = Config.JSONList(value_type=Point)
		obj.decode([{'x': 1, 'y': 2}, {'x': 3, 'y': 4}])
		self.assertEqual(obj.data, [Point(1, 2), Point(3, 4)])

	def test_decode_skips_non_dict_and_bad_entries(self) -> None:
		obj: Config.JSONList[Point] = Config.JSONList(value_type=Point)
		obj.decode([{'x': 1, 'y': 2}, 'not a dict', {'missing': True}])
		self.assertEqual(obj.data, [Point(1, 2)])

	def test_decode_ignores_non_list(self) -> None:
		obj: Config.JSONList[Point] = Config.JSONList(value_type=Point, defaults=[Point(0, 0)])
		obj.decode('nope')
		self.assertEqual(obj.data, [Point(0, 0)])

	def test_encode_round_trips(self) -> None:
		obj: Config.JSONList[Point] = Config.JSONList(value_type=Point)
		obj.data = [Point(1, 2), Point(3, 4)]
		self.assertEqual(obj.encode(), [{'x': 1, 'y': 2}, {'x': 3, 'y': 4}])

	def test_reset_deep_copies_defaults(self) -> None:
		default = Point(1, 2)
		obj: Config.JSONList[Point] = Config.JSONList(value_type=Point, defaults=[default])
		obj.reset()
		obj.data[0].x = 99
		obj.reset()
		self.assertEqual(obj.data[0].x, 1)


class Test_Enum(unittest.TestCase):
	def test_encode_returns_underlying_value(self) -> None:
		obj: Config.Enum[Mode] = Config.Enum(enum_type=Mode, default=Mode.alpha)
		self.assertEqual(obj.encode(), 1)

	def test_decode_by_value(self) -> None:
		obj: Config.Enum[Mode] = Config.Enum(enum_type=Mode, default=Mode.alpha)
		obj.decode(2)
		self.assertEqual(obj.value, Mode.beta)

	def test_decode_invalid_value_unchanged(self) -> None:
		obj: Config.Enum[Mode] = Config.Enum(enum_type=Mode, default=Mode.alpha)
		obj.decode(99)
		self.assertEqual(obj.value, Mode.alpha)

	def test_reset(self) -> None:
		obj: Config.Enum[Mode] = Config.Enum(enum_type=Mode, default=Mode.alpha)
		obj.decode(2)
		obj.reset()
		self.assertEqual(obj.value, Mode.alpha)


class Test_Style(unittest.TestCase):
	def test_configuration_empty_when_unset(self) -> None:
		self.assertEqual(Config.Style().configuration, {})

	def test_configuration_includes_foreground(self) -> None:
		self.assertEqual(Config.Style(foreground='#ffffff').configuration, {'foreground': '#ffffff'})

	def test_configuration_includes_background(self) -> None:
		self.assertEqual(Config.Style(background='#000000').configuration, {'background': '#000000'})

	def test_configuration_includes_both_colors(self) -> None:
		self.assertEqual(
			Config.Style(foreground='#ffffff', background='#000000').configuration,
			{'foreground': '#ffffff', 'background': '#000000'}
		)

	def test_copy_preserves_fields(self) -> None:
		original = Config.Style(foreground='#ffffff', background='#000000', bold=True)
		copy = original.copy()
		self.assertEqual(copy, original)

	def test_copy_is_independent(self) -> None:
		original = Config.Style(foreground='#ffffff')
		copy = original.copy()
		copy.foreground = '#000000'
		self.assertEqual(original.foreground, '#ffffff')


class Test_HighlightStyle(unittest.TestCase):
	def test_encode_serializes_style(self) -> None:
		obj = Config.HighlightStyle(Config.Style(foreground='#ffffff', background='#000000', bold=True))
		self.assertEqual(obj.encode(), {'foreground': '#ffffff', 'background': '#000000', 'bold': True})

	def test_decode_round_trips(self) -> None:
		obj = Config.HighlightStyle(Config.Style())
		obj.decode({'foreground': '#112233', 'background': '#445566', 'bold': True})
		self.assertEqual(obj.style, Config.Style(foreground='#112233', background='#445566', bold=True))

	def test_decode_rejects_invalid_colors(self) -> None:
		obj = Config.HighlightStyle(Config.Style())
		obj.decode({'foreground': 'xyz', 'background': 123, 'bold': True})
		self.assertIsNone(obj.style.foreground)
		self.assertIsNone(obj.style.background)
		self.assertTrue(obj.style.bold)

	def test_decode_non_bool_bold_defaults_false(self) -> None:
		obj = Config.HighlightStyle(Config.Style())
		obj.decode({'foreground': '#112233', 'bold': 'yes'})
		self.assertFalse(obj.style.bold)

	def test_decode_ignores_non_dict(self) -> None:
		obj = Config.HighlightStyle(Config.Style(foreground='#ffffff'))
		obj.decode('nope')
		self.assertEqual(obj.style.foreground, '#ffffff')

	def test_reset_restores_default(self) -> None:
		obj = Config.HighlightStyle(Config.Style(foreground='#ffffff'))
		obj.decode({'foreground': '#000000'})
		obj.reset()
		self.assertEqual(obj.style.foreground, '#ffffff')


class Test_FileOpType_title(unittest.TestCase):
	def test_open_save_save(self) -> None:
		self.assertEqual(Config.FileOpType.open_save.title('Unit', True), 'Save Unit')

	def test_open_save_open(self) -> None:
		self.assertEqual(Config.FileOpType.open_save.title('Unit', False), 'Open Unit')

	def test_import_export_save(self) -> None:
		self.assertEqual(Config.FileOpType.import_export.title('Unit', True), 'Export Unit')

	def test_import_export_open(self) -> None:
		self.assertEqual(Config.FileOpType.import_export.title('Unit', False), 'Import Unit')

	def test_plural_lowercase_ending_adds_s(self) -> None:
		self.assertEqual(Config.FileOpType.open_save.title('Unit', True, multiple=True), 'Save Units')

	def test_plural_uppercase_ending_adds_apostrophe_s(self) -> None:
		self.assertEqual(Config.FileOpType.open_save.title('GRP', True, multiple=True), "Save GRP's")


class Test_FileOpType_keys(unittest.TestCase):
	def test_open_save_keys(self) -> None:
		self.assertEqual(Config.FileOpType.open_save.save_key, 'save')
		self.assertEqual(Config.FileOpType.open_save.open_key, 'open')

	def test_import_export_keys(self) -> None:
		self.assertEqual(Config.FileOpType.import_export.save_key, 'export')
		self.assertEqual(Config.FileOpType.import_export.open_key, 'import')


class InnerGroup(Config.Group):
	def __init__(self) -> None:
		self.flag = Config.Boolean(default=False)
		super().__init__()


class SampleGroup(Config.Group):
	def __init__(self) -> None:
		self.name = Config.String(default='d')
		self.count = Config.Int(default=0)
		self.inner = InnerGroup()
		super().__init__()


class UnderscoreGroup(Config.Group):
	def __init__(self) -> None:
		self.import_ = Config.Boolean(default=False)
		super().__init__()


class Test_Group(unittest.TestCase):
	def test_encode_collects_fields(self) -> None:
		self.assertEqual(SampleGroup().encode(), {'name': 'd', 'count': 0, 'inner': {'flag': False}})

	def test_encode_strips_trailing_underscore_from_key(self) -> None:
		self.assertEqual(UnderscoreGroup().encode(), {'import': False})

	def test_decode_applies_values(self) -> None:
		group = SampleGroup()
		group.decode({'name': 'hi', 'count': 5})
		self.assertEqual(group.name.value, 'hi')
		self.assertEqual(group.count.value, 5)

	def test_decode_recurses_into_nested_group(self) -> None:
		group = SampleGroup()
		group.decode({'inner': {'flag': True}})
		self.assertIs(group.inner.flag.value, True)

	def test_decode_maps_key_to_trailing_underscore_attr(self) -> None:
		group = UnderscoreGroup()
		group.decode({'import': True})
		self.assertIs(group.import_.value, True)

	def test_decode_ignores_unknown_keys(self) -> None:
		group = SampleGroup()
		group.decode({'unknown': 1, 'name': 'hi'})
		self.assertEqual(group.name.value, 'hi')

	def test_decode_ignores_underscore_prefixed_keys(self) -> None:
		group = SampleGroup()
		group.decode({'_private': 'x'})
		self.assertEqual(group.name.value, 'd')

	def test_decode_ignores_non_dict(self) -> None:
		group = SampleGroup()
		group.decode([1, 2])
		self.assertEqual(group.name.value, 'd')

	def test_reset_restores_all_fields(self) -> None:
		group = SampleGroup()
		group.name.value = 'changed'
		group.inner.flag.value = True
		group.reset()
		self.assertEqual(group.name.value, 'd')
		self.assertIs(group.inner.flag.value, False)

	def test_store_and_restore_state(self) -> None:
		group = SampleGroup()
		group.name.value = 'stored'
		group.store_state()
		group.name.value = 'temporary'
		group.restore_state()
		self.assertEqual(group.name.value, 'stored')


def _sample_migrate_1_to_2(data: dict) -> None:
	Config.migrate_field(data, ('old_value',), ('value',))


class SampleConfig(Config.Config):
	_name = 'PyMSTestSample'
	_version = 2
	_migrations = {
		1: _sample_migrate_1_to_2
	}

	def __init__(self) -> None:
		self.value = Config.Int(default=0)
		self.name = Config.String(default='d')
		super().__init__()


class Test_Config(unittest.TestCase):
	def _config_reading(self, settings: dict | None) -> SampleConfig:
		# `settings is None` simulates a missing settings file (read raises).
		if settings is None:
			patcher = mock.patch.object(SampleConfig, '_read', side_effect=FileNotFoundError)
		else:
			patcher = mock.patch.object(SampleConfig, '_read', return_value=settings)
		with patcher:
			return SampleConfig()

	def test_load_missing_file_uses_defaults(self) -> None:
		config = self._config_reading(None)
		self.assertEqual(config.value.value, 0)
		self.assertEqual(config.name.value, 'd')

	def test_load_matching_version_decodes_fields(self) -> None:
		config = self._config_reading({'version': 2, 'value': 5, 'name': 'hi'})
		self.assertEqual(config.value.value, 5)
		self.assertEqual(config.name.value, 'hi')

	def test_load_runs_migration_for_old_version(self) -> None:
		config = self._config_reading({'version': 1, 'old_value': 9})
		self.assertEqual(config.value.value, 9)

	def test_load_missing_version_is_discarded(self) -> None:
		config = self._config_reading({'value': 5})
		self.assertEqual(config.value.value, 0)

	def test_save_writes_current_version(self) -> None:
		with mock.patch.object(SampleConfig, '_read', side_effect=FileNotFoundError), \
				mock.patch.object(SampleConfig, '_write') as write_mock:
			SampleConfig().save()
		written = write_mock.call_args.args[0]
		self.assertEqual(written['version'], 2)

	def test_save_round_trips_through_load(self) -> None:
		with mock.patch.object(SampleConfig, '_read', side_effect=FileNotFoundError), \
				mock.patch.object(SampleConfig, '_write') as write_mock:
			config = SampleConfig()
			config.value.value = 7
			config.name.value = 'zz'
			config.save()
		written = write_mock.call_args.args[0]
		reloaded = self._config_reading(written)
		self.assertEqual(reloaded.value.value, 7)
		self.assertEqual(reloaded.name.value, 'zz')
