from . import Assets
from .PyMSConfig import PYMS_CONFIG
from .PyMSDialog import PyMSDialog
from .PyMSError import PyMSError
from .trace import get_tracer
from . import UIKit as UI
from .SemVer import SemVer

import json, ssl, urllib.request
from threading import Thread

from typing import Callable

class UpdateDialog(PyMSDialog):
	BRANCH = 'python3' # Default to `master` branch, but can be update for long-lived branches
	POLL_MS = 100

	@staticmethod
	def fetch_versions() -> dict[str, str]:
		"""Download the latest `versions.json`. Blocks, so call it off the main thread."""
		VERSIONS_URL = f'https://raw.githubusercontent.com/poiuyqwert/PyMS/{UpdateDialog.BRANCH}/PyMS/versions.json'
		try:
			with urllib.request.urlopen(VERSIONS_URL, context=ssl.create_default_context(), timeout=30) as response:
				data = response.read()
		except Exception as e:
			raise PyMSError('Update', f"Couldn't download the latest version information from GitHub ({e}).") from e
		try:
			versions = json.loads(data)
		except ValueError as e:
			raise PyMSError('Update', 'The latest version information downloaded from GitHub is invalid (parse error).') from e
		if not isinstance(versions, dict):
			raise PyMSError('Update', 'The latest version information downloaded from GitHub is invalid (wrong data).')
		return versions

	@staticmethod
	def outdated(program: str, versions: dict[str, str]) -> tuple[bool, bool]:
		"""Return whether (PyMS, `program`) are older than their latest `versions`."""
		try:
			latest_PyMS_version = SemVer(versions['PyMS'])
			latest_program_version = SemVer(versions[program])
		except Exception as e:
			raise PyMSError('Update', f'The latest version information downloaded from GitHub has no valid version for PyMS and {program}.') from e
		try:
			PyMS_version = SemVer(Assets.version('PyMS'))
			program_version = SemVer(Assets.version(program))
		except Exception as e:
			raise PyMSError('Update', f'The installed version of PyMS or {program} is invalid.') from e
		return (PyMS_version < latest_PyMS_version, program_version < latest_program_version)

	@staticmethod
	def reminder_suppressed(program: str, versions: dict[str, str]) -> bool:
		"""Whether "Don't remind me for this version" was checked for both of the latest `versions`."""
		if not (PyMS_dont_remind_me_raw := PYMS_CONFIG.reminder.pyms_version.data.get('PyMS')):
			return False
		if not (program_dont_remind_me_raw := PYMS_CONFIG.reminder.pyms_version.data.get(program)):
			return False
		return SemVer(PyMS_dont_remind_me_raw) >= SemVer(versions['PyMS']) and SemVer(program_dont_remind_me_raw) >= SemVer(versions[program])

	@staticmethod
	def fetch_versions_in_background(widget: UI.WindowExtensions, callback: Callable[[dict[str, str] | PyMSError], None]) -> None:
		"""Run `fetch_versions` on a worker thread and deliver its result to `callback` on the main thread.

		The worker never touches Tk; `widget` polls for the result, so the poll (and `callback`) is dropped if `widget` is destroyed first."""
		result: list[dict[str, str] | PyMSError] = []
		def fetch() -> None:
			try:
				result.append(UpdateDialog.fetch_versions())
			except PyMSError as e:
				result.append(e)
			except Exception as e:
				error = PyMSError('Update', f"Couldn't check for updates ({e}).")
				error.__cause__ = e
				result.append(error)
		Thread(target=fetch, name='PyMS UpdateCheck', daemon=True).start()
		def poll() -> None:
			if not result:
				widget.after_managed(UpdateDialog.POLL_MS, poll)
				return
			callback(result[0])
		widget.after_managed(UpdateDialog.POLL_MS, poll)

	@staticmethod
	def check_update(window: UI.WindowExtensions, program: str) -> None:
		"""Check for updates in the background, only showing the dialog when an update hasn't been dismissed with "Don't remind me"."""
		def fetched(result: dict[str, str] | PyMSError) -> None:
			if isinstance(result, PyMSError):
				return
			versions = result
			try:
				if not any(UpdateDialog.outdated(program, versions)):
					return
				if UpdateDialog.reminder_suppressed(program, versions):
					return
			except Exception:
				if tracer := get_tracer():
					tracer.trace_error()
				return
			def show() -> None:
				if hasattr(window, '_pyms__window_blocking') and window._pyms__window_blocking: # pylint: disable=protected-access
					window.after_managed(1000, show)
					return
				UpdateDialog(window, program, versions)
			show()
		UpdateDialog.fetch_versions_in_background(window, fetched)

	def __init__(self, parent: UI.Misc, program: str, versions: dict[str, str] | None = None) -> None:
		"""Show the available update in `versions`, or with no `versions` check for updates and show the result."""
		self.program = program
		self.versions = versions
		PyMSDialog.__init__(self, parent, 'New Version Found' if versions else 'Check for Updates', resizable=(False, False))

	def widgetize(self) -> UI.Misc | None:
		self.dont_remind_me = UI.BooleanVar()
		self.body = UI.Frame(self)
		self.body.pack(fill=UI.BOTH, expand=1)
		if self.versions:
			return self.build_update_available(self.versions)
		return self.build_loading()

	def set_content(self, build: Callable[[], UI.Misc]) -> None:
		for child in self.body.winfo_children():
			child.destroy()
		focus = build()
		self.recenter()
		focus.focus_set()

	def check(self) -> None:
		self.set_content(self.build_loading)

	def fetched(self, result: dict[str, str] | PyMSError) -> None:
		try:
			if isinstance(result, PyMSError):
				raise result
			outdated = UpdateDialog.outdated(self.program, result)
		except PyMSError as e:
			error = e
			self.set_content(lambda: self.build_error(error))
			return
		self.versions = result
		if any(outdated):
			self.title('New Version Found')
			self.set_content(lambda: self.build_update_available(result))
		else:
			self.set_content(self.build_up_to_date)

	def message(self, text: str) -> None:
		UI.Label(self.body, justify=UI.LEFT, anchor=UI.W, text=text, wraplength=640).pack(pady=5, padx=5, fill=UI.X)

	def buttons(self, *buttons: tuple[str, Callable[[], None]]) -> UI.Button:
		frame = UI.Frame(self.body)
		first: UI.Button | None = None
		for text, command in buttons:
			button = UI.Button(frame, text=text, width=10, command=command)
			button.pack(side=UI.LEFT, padx=3)
			first = first or button
		frame.pack(pady=5)
		assert first is not None
		return first

	def build_loading(self) -> UI.Misc:
		self.message('Checking for updates...')
		cancel = self.buttons(('Cancel', self.cancel))
		UpdateDialog.fetch_versions_in_background(self, self.fetched)
		return cancel

	def build_error(self, error: PyMSError) -> UI.Misc:
		self.message(f'Unable to check for updates.\n{error.error}')
		return self.buttons(('Ok', self.ok), ('Retry', self.check))

	def build_up_to_date(self) -> UI.Misc:
		self.message(f"You're running the latest version of {self.program} ({Assets.version(self.program)}) and PyMS ({Assets.version('PyMS')}).")
		return self.buttons(('Ok', self.ok))

	def build_update_available(self, versions: dict[str, str]) -> UI.Misc:
		PyMS_outdated, program_outdated = UpdateDialog.outdated(self.program, versions)
		lines = []
		if program_outdated:
			lines.append(f'Your version of {self.program} ({Assets.version(self.program)}) is older than the current version ({versions[self.program]}).')
		if PyMS_outdated:
			lines.append(f"Your version of PyMS ({Assets.version('PyMS')}) is older than the current version ({versions['PyMS']}).")
		lines.append('It is recommended that you update as soon as possible.')
		self.message('\n'.join(lines))
		f = UI.Frame(self.body)
		UI.Checkbutton(f, text="Don't remind me for this version", variable=self.dont_remind_me).pack(side=UI.LEFT, padx=5)
		UI.Hotlink(f, 'Github', 'https://github.com/poiuyqwert/PyMS').pack(side=UI.RIGHT, padx=5)
		f.pack(fill=UI.X, expand=1)
		return self.buttons(('Ok', self.ok))

	def ok(self, _: UI.Event | None = None) -> None:
		if self.versions and self.dont_remind_me.get():
			PYMS_CONFIG.reminder.pyms_version.data['PyMS'] = self.versions['PyMS']
			PYMS_CONFIG.reminder.pyms_version.data[self.program] = self.versions[self.program]
			PYMS_CONFIG.save()
		PyMSDialog.ok(self)
