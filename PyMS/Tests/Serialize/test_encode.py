
from ...Utilities.Serialize import IntEncoder, StrEncoder, IntFlagEncoder, ReferenceEncoder, Definition, IDMode, encode_json, encode_jsons, encode_text, encode_texts
from ...Utilities.PyMSError import PyMSError

import unittest


class Sample:
	def __init__(self, count: int = 0, label: str = '', enabled: bool = False) -> None:
		self.count = count
		self.label = label
		self.enabled = enabled
		self.ref: 'Sample | None' = None


def sample_definition(id_mode: IDMode = IDMode.comment) -> Definition:
	return Definition('Sample', id_mode, {
		'count': IntEncoder(),
		'label': StrEncoder(),
		'enabled': IntEncoder(),
	})


class Test_encode_json(unittest.TestCase):
	def test_includes_field_values(self) -> None:
		json = encode_json(Sample(count=5, label='hi'), None, sample_definition())
		self.assertEqual(json['count'], 5)
		self.assertEqual(json['label'], 'hi')

	def test_type_and_id_lead_in_order(self) -> None:
		json = encode_json(Sample(count=5, label='hi'), 7, sample_definition())
		self.assertEqual(list(json.keys())[:2], ['_type', '_id'])
		self.assertEqual(json['_type'], 'Sample')
		self.assertEqual(json['_id'], 7)

	def test_no_id_omits_id_key(self) -> None:
		json = encode_json(Sample(), None, sample_definition(IDMode.comment))
		self.assertNotIn('_id', json)
		self.assertEqual(json['_type'], 'Sample')

	def test_header_mode_without_id_raises(self) -> None:
		with self.assertRaises(PyMSError) as cm:
			encode_json(Sample(), None, sample_definition(IDMode.header))
		self.assertIn('Missing ID', str(cm.exception))

	def test_missing_attribute_raises(self) -> None:
		definition = Definition('Sample', IDMode.none, {'missing': IntEncoder()})
		with self.assertRaises(PyMSError) as cm:
			encode_json(Sample(), None, definition)
		self.assertIn('is not a valid attribute name', str(cm.exception))

	def test_empty_fields_filter_raises(self) -> None:
		with self.assertRaises(PyMSError) as cm:
			encode_json(Sample(), None, sample_definition(), {})
		self.assertIn('No fields to encode', str(cm.exception))

	def test_fields_filter_selects_subset(self) -> None:
		json = encode_json(Sample(count=5, label='hi'), None, sample_definition(), {'count': True})
		self.assertIn('count', json)
		self.assertNotIn('label', json)

	def test_group_encoder_nested_object(self) -> None:
		definition = Definition('Flagged', IDMode.none, {'flags': IntFlagEncoder({'a': 1, 'b': 2})})
		obj = type('Flagged', (), {'flags': 1})()
		json = encode_json(obj, None, definition)
		self.assertEqual(json['flags'], {'a': True, 'b': False})

	def test_nested_substructure(self) -> None:
		definition = Definition('Outer', IDMode.none, {'inner': {'count': IntEncoder()}})
		outer = type('Outer', (), {'inner': Sample(count=9)})()
		json = encode_json(outer, None, definition)
		inner = json['inner']
		assert isinstance(inner, dict)
		self.assertEqual(inner['count'], 9)


class Test_encode_jsons(unittest.TestCase):
	def test_encodes_each_object(self) -> None:
		definition = sample_definition()
		jsons = encode_jsons([(Sample(count=1), 0), (Sample(count=2), 1)], lambda _: definition)
		self.assertEqual([j['count'] for j in jsons], [1, 2])

	def test_missing_definition_raises(self) -> None:
		with self.assertRaises(PyMSError) as cm:
			encode_jsons([(Sample(), 0)], lambda _: None)
		self.assertIn('has no definition', str(cm.exception))


class Test_encode_text(unittest.TestCase):
	def test_comment_mode_header(self) -> None:
		text = encode_text(Sample(count=5), 7, sample_definition(IDMode.comment))
		self.assertTrue(text.startswith('# Export of Sample 7\nSample:\n'))

	def test_header_mode_header(self) -> None:
		text = encode_text(Sample(count=5), 7, sample_definition(IDMode.header))
		self.assertTrue(text.startswith('Sample(7):\n'))

	def test_no_id_plain_header(self) -> None:
		text = encode_text(Sample(count=5), None, sample_definition(IDMode.none))
		self.assertTrue(text.startswith('Sample:\n'))

	def test_none_mode_with_id_uses_plain_header(self) -> None:
		# A supplied id with id_mode none should still produce the plain header,
		# not crash, and must not leak the id into the text body.
		text = encode_text(Sample(count=5), 7, sample_definition(IDMode.none))
		self.assertTrue(text.startswith('Sample:\n'))
		self.assertNotIn('7', text.splitlines()[0])

	def test_field_lines_are_tab_indented(self) -> None:
		text = encode_text(Sample(count=5, label='hi'), None, sample_definition(IDMode.none))
		self.assertIn('\tcount 5\n', text)
		self.assertIn('\tlabel hi\n', text)

	def test_underscore_keys_are_omitted(self) -> None:
		text = encode_text(Sample(), 7, sample_definition(IDMode.comment))
		self.assertNotIn('_type', text)
		self.assertNotIn('_id', text)

	def test_bool_rendered_as_int(self) -> None:
		definition = Definition('Sample', IDMode.none, {'enabled': IntFlagEncoder({'enabled': 1})})
		obj = type('Sample', (), {'enabled': 1})()
		text = encode_text(obj, None, definition)
		self.assertIn('\tenabled.enabled 1\n', text)

	def test_multiline_string_is_block_indented(self) -> None:
		text = encode_text(Sample(label='one\ntwo'), None, sample_definition(IDMode.none))
		self.assertIn('\tlabel:\n\t\tone\n\t\ttwo\n', text)

	def test_empty_string_is_block_form(self) -> None:
		# An empty value on a flat `key value` line can't be parsed back, so
		# empty strings use the multi-line block form with no lines.
		text = encode_text(Sample(count=5, label=''), None, sample_definition(IDMode.none))
		self.assertIn('\tlabel:\n', text)
		self.assertNotIn('\tlabel \n', text)

	def test_header_mode_without_id_raises(self) -> None:
		with self.assertRaises(PyMSError) as cm:
			encode_text(Sample(), None, sample_definition(IDMode.header))
		self.assertIn('Missing ID', str(cm.exception))


class Test_encode_references(unittest.TestCase):
	def ref_definition(self) -> Definition:
		return Definition('Sample', IDMode.header, {
			'count': IntEncoder(),
			'ref': ReferenceEncoder('Sample'),
		})

	def test_reference_encodes_as_target_id(self) -> None:
		definition = self.ref_definition()
		target = Sample(count=1)
		referencer = Sample(count=2)
		referencer.ref = target
		text = encode_texts([(target, 7), (referencer, 8)], lambda _: definition)
		self.assertIn('\tref None\n', text)
		self.assertIn('\tref 7\n', text)

	def test_unencoded_reference_target_raises(self) -> None:
		referencer = Sample()
		referencer.ref = Sample()
		with self.assertRaises(PyMSError) as cm:
			encode_texts([(referencer, 0)], lambda _: self.ref_definition())
		self.assertIn("Referenced 'Sample' object has no ID", str(cm.exception))


class Test_encode_texts(unittest.TestCase):
	def test_objects_separated_by_blank_line(self) -> None:
		definition = sample_definition(IDMode.none)
		text = encode_texts([(Sample(count=1), 0), (Sample(count=2), 1)], lambda _: definition)
		self.assertEqual(text.count('Sample:\n'), 2)
		self.assertIn('\n\nSample:\n', text)

	def test_missing_definition_raises(self) -> None:
		with self.assertRaises(PyMSError) as cm:
			encode_texts([(Sample(), 0)], lambda _: None)
		self.assertIn('has no definition', str(cm.exception))
