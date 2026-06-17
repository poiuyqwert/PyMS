
from ...Utilities import IO

import io
import unittest
from unittest.mock import MagicMock, patch


class Test_OutputTextFile(unittest.TestCase):
	def _make_file(self) -> tuple[IO.OutputTextFile, MagicMock]:
		temp_file = MagicMock()
		temp_file.closed = False
		temp_file.name = '/tmp/destination-tempfile'
		with patch('tempfile.NamedTemporaryFile', return_value=temp_file):
			output = IO.OutputTextFile('/tmp/destination')
		return output, temp_file

	def test_clean_exit_commits_temp_file(self) -> None:
		output, temp_file = self._make_file()
		with patch('os.replace') as replace, patch('os.remove') as remove:
			with output:
				pass
			replace.assert_called_once_with(temp_file.name, '/tmp/destination')
			remove.assert_not_called()

	def test_error_exit_discards_without_committing(self) -> None:
		output, temp_file = self._make_file()
		with patch('os.replace') as replace, patch('os.remove') as remove:
			with self.assertRaises(ValueError):
				with output:
					raise ValueError('write failed')
			replace.assert_not_called()
			remove.assert_called_once_with(temp_file.name)


class Test_OutputBytesFile(unittest.TestCase):
	def _make_file(self) -> tuple[IO.OutputBytesFile, MagicMock]:
		temp_file = MagicMock()
		temp_file.closed = False
		temp_file.name = '/tmp/destination-tempfile'
		with patch('tempfile.NamedTemporaryFile', return_value=temp_file):
			output = IO.OutputBytesFile('/tmp/destination')
		return output, temp_file

	def test_clean_exit_commits_temp_file(self) -> None:
		output, temp_file = self._make_file()
		with patch('os.replace') as replace, patch('os.remove') as remove:
			with output:
				pass
			replace.assert_called_once_with(temp_file.name, '/tmp/destination')
			remove.assert_not_called()

	def test_error_exit_discards_without_committing(self) -> None:
		output, temp_file = self._make_file()
		with patch('os.replace') as replace, patch('os.remove') as remove:
			with self.assertRaises(ValueError):
				with output:
					raise ValueError('write failed')
			replace.assert_not_called()
			remove.assert_called_once_with(temp_file.name)


class Test_OutputText(unittest.TestCase):
	def test_owned_file_receives_exception_state_on_error(self) -> None:
		owned = MagicMock(spec=IO.OutputTextFile)
		wrapper = IO.OutputText.__new__(IO.OutputText)
		wrapper.close = True
		wrapper.file = owned
		try:
			raise ValueError('boom')
		except ValueError:
			import sys
			wrapper.__exit__(*sys.exc_info())
		owned.__exit__.assert_called_once()
		self.assertIs(owned.__exit__.call_args.args[0], ValueError)
		owned.close.assert_not_called()

	def test_owned_file_committed_on_clean_exit(self) -> None:
		owned = MagicMock(spec=IO.OutputTextFile)
		wrapper = IO.OutputText.__new__(IO.OutputText)
		wrapper.close = True
		wrapper.file = owned
		wrapper.__exit__(None, None, None)
		owned.__exit__.assert_called_once_with(None, None, None)

	def test_external_file_is_not_closed(self) -> None:
		external = io.StringIO()
		with IO.OutputText(external) as f:
			f.write('hello')
		self.assertFalse(external.closed)
		self.assertEqual(external.getvalue(), 'hello')


class Test_OutputBytes(unittest.TestCase):
	def test_owned_file_receives_exception_state_on_error(self) -> None:
		owned = MagicMock(spec=IO.OutputBytesFile)
		wrapper = IO.OutputBytes.__new__(IO.OutputBytes)
		wrapper.close = True
		wrapper.file = owned
		try:
			raise ValueError('boom')
		except ValueError:
			import sys
			wrapper.__exit__(*sys.exc_info())
		owned.__exit__.assert_called_once()
		self.assertIs(owned.__exit__.call_args.args[0], ValueError)
		owned.close.assert_not_called()

	def test_external_file_is_not_closed(self) -> None:
		external = io.BytesIO()
		with IO.OutputBytes(external) as f:
			f.write(b'hello')
		self.assertFalse(external.closed)
		self.assertEqual(external.getvalue(), b'hello')
