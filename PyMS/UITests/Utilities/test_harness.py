
from ..harness import UITestCase
from .. import isolation

from ...Utilities import UIKit as UI


class _Host(UI.MainWindow):
	pass


class Test_CallbackExceptions(UITestCase):
	def test_exception_in_binding_is_recorded(self) -> None:
		window = self.make_window(_Host)
		def fail(_event: object) -> None:
			raise IndexError('raised from a binding')
		window.bind('<<HarnessTest>>', fail)
		window.event_generate('<<HarnessTest>>')
		self.pump(window)
		exceptions = self.take_callback_exceptions()
		self.assertEqual(len(exceptions), 1)
		self.assertIn('IndexError: raised from a binding', exceptions[0])
		self.assertEqual(self.take_callback_exceptions(), [])

	def test_exception_in_after_callback_is_recorded(self) -> None:
		window = self.make_window(_Host)
		def fail() -> None:
			raise ValueError('raised from an after callback')
		window.after_idle(fail)
		self.pump(window)
		exceptions = self.take_callback_exceptions()
		self.assertEqual(len(exceptions), 1)
		self.assertIn('ValueError: raised from an after callback', exceptions[0])

	def test_unclaimed_exception_fails_the_test(self) -> None:
		window = self.make_window(_Host)
		window.after_idle(lambda: 1 // 0)
		self.pump(window)
		with self.assertRaises(AssertionError) as cm:
			self._assert_isolated(isolation.DISK_WRITES.mark(), isolation.MODALS.mark(), isolation.TRACED_ERRORS.mark(), self._callback_exceptions_mark)
		self.assertIn('Exception in Tk callback', str(cm.exception))
		self.assertIn('ZeroDivisionError', str(cm.exception))
