
from ..harness import UITestCase

from ...PyMPQ.PyMPQ import PyMPQ

from unittest import mock

# These tests drive PyMPQ through its public command methods. The harness
# neutralizes settings I/O, analytics, the update check, and the tracer; the
# archive, file dialogs, and file I/O are mocked so no files are read or
# written.


class PyMPQTestCase(UITestCase):
	def make_pympq(self) -> PyMPQ:
		return self.make_window(PyMPQ)

	def seed_mpq(self, gui: PyMPQ, file_names: list[bytes]) -> mock.MagicMock:
		# Stand in for an opened archive: commands open it as a context manager
		# and call `read_file`, taking entries from `display_files`.
		mpq = mock.MagicMock()
		mpq.read_file.return_value = b'data'
		gui.mpq = mpq
		gui.display_files = [mock.Mock(file_name=file_name, locale=0) for file_name in file_names]
		return mpq
