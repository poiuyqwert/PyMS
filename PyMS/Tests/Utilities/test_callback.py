
from ...Utilities.Callback import Callback

import unittest


class Test_Callback(unittest.TestCase):
	def test_iadd_registers_callback(self) -> None:
		callback: Callback[str] = Callback()
		received: list[str] = []
		callback += received.append
		callback('x')
		self.assertEqual(received, ['x'])

	def test_isub_removes_callback(self) -> None:
		callback: Callback[str] = Callback()
		received: list[str] = []
		fn = received.append
		callback += fn
		callback -= fn
		callback('x')
		self.assertEqual(received, [])

	def test_iadd_returns_same_instance(self) -> None:
		callback: Callback[str] = Callback()
		result = callback
		result += (lambda _: None)
		self.assertIs(result, callback)

	def test_all_registered_callbacks_are_invoked(self) -> None:
		callback: Callback[str] = Callback()
		received: list[str] = []
		callback += (lambda v: received.append(f'a{v}'))
		callback += (lambda v: received.append(f'b{v}'))
		callback('!')
		self.assertEqual(received, ['a!', 'b!'])

	def test_callback_removed_during_dispatch_does_not_skip_others(self) -> None:
		# Dispatch must iterate a snapshot so a callback that detaches itself
		# mid-dispatch doesn't cause the following callback to be skipped.
		callback: Callback[None] = Callback()
		seen: list[str] = []
		def first(_: None) -> None:
			seen.append('first')
			callback.remove(first)
		def second(_: None) -> None:
			seen.append('second')
		callback += first
		callback += second
		callback(None)
		self.assertEqual(seen, ['first', 'second'])
