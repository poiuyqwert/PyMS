
from tkinter import Event

EVENT_ATTRS = [
	'serial',
	'num',
	'focus',
	'height',
	'width',
	'keycode',
	'state',
	'time',
	'x',
	'y',
	'x_root',
	'y_root',
	'char',
	'send_event',
	'keysym',
	'keysym_num',
	'type',
	'widget',
	'delta',
]

def repr_event(event: Event) -> str:
	result = '<Event'
	for attr in EVENT_ATTRS:
		if hasattr(event, attr):
			value = getattr(event, attr)
			result += f'\n\t{attr} = {value!r}'
			if attr == 'widget':
				result += f' ({value})'
	return result + '\n>'

__all__ = [
	'Event',
	'repr_event',
]
