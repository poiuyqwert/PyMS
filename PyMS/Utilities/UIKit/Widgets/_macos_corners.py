"""Force square corners on borderless NSWindows on macOS.

Tk 9.0 on macOS Big Sur+ renders `wm_overrideredirect(True)` Toplevels with a
26pt rounded-corner mask, and exposes no Tcl API to disable it. Reach into the
NSWindow via libobjc and call the private `_setCornerRadius:` setter. Apple's
implementation clamps 0 back to the system default of 26, so we pass a sub-pixel
radius that renders as square at any sane window size.

The NSWindow is identified by tagging the Tk Toplevel with a unique title and
walking `[NSApp windows]` for an NSWindow whose title matches; the original
title is restored afterwards. If anything fails (non-macOS, libobjc not
loadable, NSWindow not found, private selector missing) this is a silent no-op.
"""
from __future__ import annotations

import ctypes
import sys
from .Extensions import WindowExtensions
import uuid
from typing import Any

# Sub-pixel — visually square at any window size. Must be non-zero: Apple's
# `_setCornerRadius:` clamps 0 back to the system default.
_SQUARE_RADIUS = 0.001

_msg_id: Any = None
_msg_id_double: Any = None
_msg_id_ulong: Any = None
_msg_id_sel: Any = None
_msg_ulong: Any = None
_msg_charp: Any = None
_sel: Any = None
_ns_app_class: int = 0
_initialized = False


def _initialize() -> bool:
	global _initialized, _msg_id, _msg_id_double, _msg_id_ulong, _msg_id_sel, _msg_ulong, _msg_charp, _sel, _ns_app_class # pylint: disable=global-statement

	if _initialized:
		return _ns_app_class != 0
	_initialized = True

	if sys.platform != 'darwin':
		return False

	try:
		libobjc = ctypes.CDLL('/usr/lib/libobjc.dylib')
		# Force AppKit to load so NSApplication is registered with the runtime.
		ctypes.CDLL('/System/Library/Frameworks/AppKit.framework/AppKit')

		libobjc.objc_getClass.restype = ctypes.c_void_p
		libobjc.objc_getClass.argtypes = [ctypes.c_char_p]
		libobjc.sel_registerName.restype = ctypes.c_void_p
		libobjc.sel_registerName.argtypes = [ctypes.c_char_p]
		_sel = libobjc.sel_registerName

		# objc_msgSend's C signature depends on the method called, so we expose it
		# as several CFUNCTYPE wrappers — one per signature we use.
		msg_addr = ctypes.cast(libobjc.objc_msgSend, ctypes.c_void_p).value
		if msg_addr is None:
			return False
		void_p = ctypes.c_void_p
		_msg_id = ctypes.CFUNCTYPE(void_p, void_p, void_p)(msg_addr)
		_msg_id_double = ctypes.CFUNCTYPE(void_p, void_p, void_p, ctypes.c_double)(msg_addr)
		_msg_id_ulong = ctypes.CFUNCTYPE(void_p, void_p, void_p, ctypes.c_ulong)(msg_addr)
		_msg_id_sel = ctypes.CFUNCTYPE(ctypes.c_bool, void_p, void_p, void_p)(msg_addr)
		_msg_ulong = ctypes.CFUNCTYPE(ctypes.c_ulong, void_p, void_p)(msg_addr)
		_msg_charp = ctypes.CFUNCTYPE(ctypes.c_char_p, void_p, void_p)(msg_addr)

		_ns_app_class = libobjc.objc_getClass(b'NSApplication') or 0
		return _ns_app_class != 0
	except Exception:
		return False


def disable_rounded_corners(toplevel: WindowExtensions) -> None:
	if not _initialize():
		return

	marker = f'__pyms_corner_fix_{uuid.uuid4().hex}__'
	try:
		original_title = toplevel.wm_title()
		toplevel.wm_title(marker)
	except Exception:
		return
	toplevel.update_idletasks()

	try:
		ns_window = _find_window_by_title(marker.encode('utf-8'))
	finally:
		try:
			toplevel.wm_title(original_title)
		except Exception:
			pass

	if not ns_window:
		return

	# Guard the private setter behind respondsToSelector so we don't crash on a
	# future macOS that doesn't have it.
	set_radius = _sel(b'_setCornerRadius:')
	if _msg_id_sel(ns_window, _sel(b'respondsToSelector:'), set_radius):
		_msg_id_double(ns_window, set_radius, _SQUARE_RADIUS)
		_msg_id(ns_window, _sel(b'display'))


def _find_window_by_title(marker: bytes) -> int:
	ns_app = _msg_id(_ns_app_class, _sel(b'sharedApplication'))
	if not ns_app:
		return 0
	windows = _msg_id(ns_app, _sel(b'windows'))
	if not windows:
		return 0
	count = _msg_ulong(windows, _sel(b'count'))
	object_at = _sel(b'objectAtIndex:')
	title_sel = _sel(b'title')
	utf8_sel = _sel(b'UTF8String')
	for i in range(count):
		window = _msg_id_ulong(windows, object_at, i)
		if not window:
			continue
		title = _msg_id(window, title_sel)
		if title and _msg_charp(title, utf8_sel) == marker:
			return window
	return 0
