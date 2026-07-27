
from ..harness import UITestCase

from ...PyMOD.PyMOD import PyMOD
from ...PyMOD.Project import Project

import os
from unittest import mock

# These tests drive PyMOD through its public command methods, asserting on both
# widget and model state. The harness neutralizes settings I/O, analytics, the
# update check, and the tracer; project folders are supplied by stubbing the
# project marker check and the directory walk so no files are read.

PROJECT_PATH = os.path.join(os.sep, 'fake', 'project')


class PyMODTestCase(UITestCase):
	def open_project(self, gui: PyMOD, files: list[str] | None = None) -> None:
		def fake_walk(path: str, topdown: bool = True) -> list[tuple[str, list[str], list[str]]]:
			assert topdown, 'The source walk must be top-down so directory pruning works'
			return [(path, [], list(files or ['sound.wav']))]
		with mock.patch.object(Project, 'load', autospec=True, return_value=None), \
				mock.patch('PyMS.PyMOD.Project._os.walk', side_effect=fake_walk):
			gui.open(PROJECT_PATH)
		self.pump(gui)
