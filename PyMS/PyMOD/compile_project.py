
from .CompileThread import CompileThread
from .Project import Project

from ..Utilities.PyMSError import PyMSError

import os

def compile_project(project_path: str) -> bool:
	project_path = os.path.abspath(project_path)
	if not os.path.isdir(project_path):
		print(f"`{project_path}` doesn't exist or is not a directory")
		return False
	project = Project(project_path)
	try:
		project.load()
	except PyMSError as e:
		print(repr(e))
		return False
	project.update_source_graph()
	if not project.source_graph:
		print('No source files to compile')
		return False
	compile_thread = CompileThread(project)
	compile_thread.start()
	success = True
	while True:
		alive = compile_thread.is_alive()
		while True:
			try:
				message = compile_thread.output_queue.get(False)
			except Exception:
				break
			if isinstance(message, CompileThread.OutputMessage.Log):
				print(message.text)
				if message.tag == 'error':
					success = False
			compile_thread.output_queue.task_done()
		if not alive:
			break
		compile_thread.join(0.1)
	return success
