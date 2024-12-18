
from __future__ import annotations

from .CodeType import CodeType

from ..PyMSError import PyMSError

import enum

from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from .CodeCommand import CodeCommandDefinition

class PluginStatus(enum.StrEnum):
	unknown = enum.auto()
	in_use = enum.auto()
	unavailable = enum.auto()

class LanguageContext:
	def __init__(self) -> None:
		self._plugin_statuses: dict[str, PluginStatus] = {}
		self._status_reasons: dict[str, dict[str, bool]] = {}
		self.reset()

	def reset(self) -> None:
		self._plugin_statuses = {
			LanguagePlugin.CORE_ID: PluginStatus.in_use
		}
		self._status_reasons = {
			LanguagePlugin.CORE_ID: {f'`{LanguagePlugin.CORE_ID}` is always active': True}
		}

	def get_status(self, plugin_id: str) -> PluginStatus:
		return self._plugin_statuses.get(plugin_id, PluginStatus.unknown)

	def set_status(self, plugin_id: str, status: PluginStatus, reason: str) -> None:
		if plugin_id in self._plugin_statuses and status != self._plugin_statuses[plugin_id]:
			raise PyMSError('Language', f'Attempting to set language plugin `{plugin_id}` status to `{status}` when it is already `{self._plugin_statuses[plugin_id]}`')
		self._plugin_statuses[plugin_id] = status
		if not plugin_id in self._status_reasons:
			self._status_reasons[plugin_id] = {}
		self._status_reasons[plugin_id][reason] = True

	def get_reasons(self, plugin_id: str) -> list[str]:
		if not plugin_id in self._status_reasons:
			return ['Unknown']
		return list(self._status_reasons[plugin_id].keys())

	def active_plugins(self, ignore_core: bool = True) -> set[str]:
		return set(id for id,status in self._plugin_statuses.items() if status == PluginStatus.in_use and (id != LanguagePlugin.CORE_ID or ignore_core == False))

class LanguageDefinition:
	def __init__(self, plugins: list[LanguagePlugin] = []) -> None:
		self.plugins = plugins
		for plugin in plugins:
			if plugin.id == LanguagePlugin.CORE_ID:
				break
		else:
			raise PyMSError('Internal', f'Language being setup without a "{LanguagePlugin.CORE_ID}" plugin')

	def lookup_command(self, id_or_name: int | str, language_context: LanguageContext) -> CodeCommandDefinition | None:
		found: tuple[CodeCommandDefinition, LanguagePlugin] | None = None
		for plugin in self.plugins:
			if cmd_def := plugin.lookup_command(id_or_name):
				plugin_status = language_context.get_status(plugin.id)
				if plugin_status != PluginStatus.unavailable or found is None:
					found = (cmd_def, plugin)
		if found is not None:
			cmd_def, plugin = found
			if language_context.get_status(plugin.id) == PluginStatus.unavailable:
				reasons = language_context.get_reasons(plugin.id)
				reason = reasons[0]
				if len(reasons) > 1:
					reason = f'{reason}, and {len(reasons)-1} other reasons'
				raise PyMSError('Language', f'Command `{cmd_def.name}` is invalid as language plugin `{plugin.id}` is not avaialable ({reason})')
			plugin.activate(f'Command `{cmd_def.name}` referenced', language_context)
			return cmd_def
		return None

	def lookup_type(self, name: str, language_context: LanguageContext) -> CodeType | None:
		found: tuple[CodeType, LanguagePlugin] | None = None
		for plugin in self.plugins:
			if code_type := plugin.lookup_type(name):
				plugin_status = language_context.get_status(plugin.id)
				if plugin_status != PluginStatus.unavailable or found is None:
					found = (code_type, plugin)
		if found is not None:
			code_type, plugin = found
			if language_context.get_status(plugin.id) == PluginStatus.unavailable:
				reasons = language_context.get_reasons(plugin.id)
				reason = reasons[0]
				if len(reasons) > 1:
					reason = f'{reason}, and {len(reasons)-1} other reasons'
				raise PyMSError('Language', f'Type `{code_type.name}` is invalid as language plugin `{plugin.id}` is not avaialable ({reason})')
			plugin.activate(f'Type `{code_type.name}` referenced', language_context)
			return code_type
		return None

class LanguagePlugin:
	CORE_ID = 'core'

	def __init__(self, id: str, cmd_defs: list[CodeCommandDefinition], code_types: list[CodeType]) -> None:
		self.id = id

		self._cmd_id_lookup: dict[int, CodeCommandDefinition] = {}
		self._cmd_name_lookup: dict[str, CodeCommandDefinition] = {}
		for cmd_def in cmd_defs:
			if cmd_def.byte_code_id is not None:
				if cmd_def.byte_code_id in self._cmd_id_lookup:
					raise PyMSError('Internal', f'Command with id `{cmd_def.byte_code_id}` (`{self._cmd_id_lookup[cmd_def.byte_code_id].name}`) already exists')
				self._cmd_id_lookup[cmd_def.byte_code_id] = cmd_def
			if cmd_def.name in self._cmd_name_lookup:
				raise PyMSError('Internal', f'Command with name `{cmd_def.name}` (`{self._cmd_name_lookup[cmd_def.name].byte_code_id}`) already exists')
			self._cmd_name_lookup[cmd_def.name] = cmd_def
		
		self._type_name_lookup: dict[str, CodeType] = {}
		for code_type in code_types:
			if code_type.name in self._type_name_lookup:
				raise PyMSError('Internal', f'Type with name `{code_type.name}` already exists')
			self._type_name_lookup[code_type.name] = code_type

	def lookup_command(self, id_or_name: int | str) -> CodeCommandDefinition | None:
		if isinstance(id_or_name, str):
			return self._cmd_name_lookup.get(id_or_name)
		else:
			return self._cmd_id_lookup.get(id_or_name)

	def lookup_type(self, name: str) -> CodeType | None:
		return self._type_name_lookup.get(name)

	def activate(self, reason: str, language_context: LanguageContext) -> None:
		language_context.set_status(self.id, PluginStatus.in_use, reason)
