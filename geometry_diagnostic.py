#!/usr/bin/env python3
# pylint: disable=consider-using-f-string
"""PyMS window geometry diagnostic.

Instructions:
  1. Place this file in the same folder as `PyAI.pyw` (next to the `PyMS` folder
     and the `Settings` folder).
  2. Run it (double-click it, or run `python geometry_diagnostic.py` from a
     command prompt). A few small invisible/blank test windows may flash briefly.
  3. When it finishes, it will have created a file named
     `geometry_diagnostic_<date>_<time>.log` next to this script.
     Please send that file back.

Version 2.0 validates the multi-monitor geometry fixes: any ANOMALY or FINDING
in the log indicates the fixes are not working correctly on this machine.

This script only READS your settings - it never modifies them or any other file
(other than writing its own log).
"""

import sys

sys.dont_write_bytecode = True

import os
import re
import json
import time
import platform
import traceback
import datetime

VERSION = '2.0'

if sys.version_info[0] < 3:
	print('This diagnostic requires Python 3, but it is running under Python %s.' % sys.version.split()[0])
	print('Try running it with the same Python that runs PyAI.pyw.')
	try:
		raw_input('Press Enter to exit...')
	except Exception:
		pass
	sys.exit(1)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

LOG_PATH = os.path.join(SCRIPT_DIR, 'geometry_diagnostic_%s.log' % datetime.datetime.now().strftime('%Y%m%d_%H%M%S'))

POS_TOLERANCE = 40 # px of set-vs-read position drift considered normal (window decorations)
SIZE_TOLERANCE = 10 # px of set-vs-read size drift considered normal


class Log(object):
	def __init__(self, path):
		self.file = None
		try:
			self.file = open(path, 'w', encoding='utf-8')
		except Exception:
			print('!! Could not create log file at %s - continuing with console output only' % path)
			print(traceback.format_exc())

	def __call__(self, message=''):
		text = str(message)
		try:
			print(text)
		except Exception:
			pass
		if self.file:
			try:
				self.file.write(text + '\n')
				self.file.flush()
			except Exception:
				pass


log = Log(LOG_PATH)

# Machine-specific findings (things unique to this machine/config that likely explain the bug)
anomalies = []
# Behavioral findings (results that demonstrate how the code behaves; may reproduce on any machine)
findings = []


def anomaly(message):
	anomalies.append(message)
	log('  ANOMALY: %s' % message)


def finding(message):
	findings.append(message)
	log('  FINDING: %s' % message)


def probe(label, func):
	try:
		value = func()
		log('  %s = %r' % (label, value))
		return value
	except Exception as exception:
		log('  %s = <error: %r>' % (label, exception))
		return None


def run_section(title, func):
	log('')
	log('=' * 78)
	log('SECTION: %s' % title)
	log('=' * 78)
	try:
		func()
	except Exception:
		log('!! Section failed with an unexpected exception:')
		log(traceback.format_exc())


# ---------------------------------------------------------------------------
# Guarded imports
# ---------------------------------------------------------------------------

TK_IMPORT_ERROR = None
try:
	import tkinter
except Exception:
	tkinter = None
	TK_IMPORT_ERROR = traceback.format_exc()

PYMS_IMPORT_ERROR = None
Config = None
Utils = None
UIKit = None
try:
	from PyMS.Utilities import Config
	from PyMS.Utilities import UIKit
	from PyMS.Utilities.UIKit import Utils
except Exception:
	PYMS_IMPORT_ERROR = traceback.format_exc()

# True when this PyMS installation includes the multi-monitor geometry fixes
# (Rect.clamp clamps to desktop `bounds` instead of shrinking into a single screen)
CLAMP_IS_FIXED = False
if Utils is not None:
	try:
		import inspect
		CLAMP_IS_FIXED = 'bounds' in inspect.signature(Utils.Rect.clamp).parameters
	except Exception:
		pass

# ---------------------------------------------------------------------------
# Shared state gathered by early sections
# ---------------------------------------------------------------------------

ROOT = None # the single Tk root
TK_SCREEN = None # (width, height) as reported by Tk
MONITORS = [] # [{'device', 'monitor': (l,t,r,b), 'work': (l,t,r,b), 'primary'}] (Windows only)
SECONDARY_POINT = None # (x, y) inside a non-primary monitor, if one exists
USER_GEOMETRIES = [] # [('windows.code_edit', '865x493+889+501'), ...] from Settings/PyAI.txt
CODE_EDIT_SAVED = None # the user's actual saved code edit geometry string

GEOMETRY_RE = re.compile(r'(\d+)x(\d+)\+(-?\d+)\+(-?\d+)')


def parse_geometry_tuple(text):
	"""Local minimal geometry parser (works even if PyMS failed to import)."""
	match = GEOMETRY_RE.match(text or '')
	if not match:
		return None
	return (int(match.group(1)), int(match.group(2)), int(match.group(3)), int(match.group(4)))


# ---------------------------------------------------------------------------
# Section 1: Python / process environment
# ---------------------------------------------------------------------------

def section_process():
	probe('script version', lambda: VERSION)
	probe('script path', lambda: os.path.abspath(__file__))
	probe('platform.platform()', platform.platform)
	probe('platform.machine()', platform.machine)
	probe('sys.version', lambda: sys.version)
	probe('sys.executable', lambda: sys.executable)
	probe('sys.platform', lambda: sys.platform)
	log('')
	if TK_IMPORT_ERROR:
		log('!! tkinter FAILED to import:')
		log(TK_IMPORT_ERROR)
	else:
		log('  tkinter imported OK')
	if PYMS_IMPORT_ERROR:
		log('!! PyMS modules FAILED to import (PyMS-specific tests will be skipped):')
		log(PYMS_IMPORT_ERROR)
	else:
		log('  PyMS.Utilities.Config and PyMS.Utilities.UIKit.Utils imported OK')
		if CLAMP_IS_FIXED:
			log('  This PyMS includes the multi-monitor geometry fixes')
		else:
			log('!! This PyMS PREDATES the multi-monitor geometry fixes - update PyMS and re-run to validate them')


# ---------------------------------------------------------------------------
# Section 2: Tk environment
# ---------------------------------------------------------------------------

def section_tk_env():
	global ROOT, TK_SCREEN
	if tkinter is None:
		log('  Skipped: tkinter is not available.')
		return
	ROOT = tkinter.Tk()
	ROOT.withdraw()
	probe('tkinter.TkVersion', lambda: tkinter.TkVersion)
	probe('tkinter.TclVersion', lambda: tkinter.TclVersion)
	probe("tk patchlevel ('info patchlevel')", lambda: ROOT.tk.call('info', 'patchlevel'))
	probe('windowingsystem', lambda: ROOT.tk.call('tk', 'windowingsystem'))
	screen_w = probe('winfo_screenwidth (primary monitor width in Tk coordinates)', ROOT.winfo_screenwidth)
	screen_h = probe('winfo_screenheight (primary monitor height in Tk coordinates)', ROOT.winfo_screenheight)
	vroot_x = probe('winfo_vrootx', ROOT.winfo_vrootx)
	vroot_y = probe('winfo_vrooty', ROOT.winfo_vrooty)
	vroot_w = probe('winfo_vrootwidth', ROOT.winfo_vrootwidth)
	vroot_h = probe('winfo_vrootheight', ROOT.winfo_vrootheight)
	probe("winfo_fpixels('1i') (effective DPI)", lambda: ROOT.winfo_fpixels('1i'))
	probe("tk scaling ('tk scaling')", lambda: ROOT.tk.call('tk', 'scaling'))
	probe('root maxsize()', ROOT.maxsize)
	probe('root minsize()', ROOT.minsize)
	probe('root wm_state()', ROOT.wm_state)
	if screen_w and screen_h:
		TK_SCREEN = (screen_w, screen_h)
	if vroot_w and vroot_h and screen_w and screen_h:
		if (vroot_w, vroot_h) != (screen_w, screen_h) or vroot_x or vroot_y:
			log('  NOTE: virtual desktop (%dx%d at %d,%d) extends beyond the primary screen (%dx%d) - multiple monitors' % (vroot_w, vroot_h, vroot_x or 0, vroot_y or 0, screen_w, screen_h))


# ---------------------------------------------------------------------------
# Section 3: Windows-native monitor layout and DPI awareness
# ---------------------------------------------------------------------------

def section_windows_native():
	global SECONDARY_POINT
	if sys.platform != 'win32':
		log('  Not Windows (sys.platform=%r) - skipping native monitor/DPI queries.' % sys.platform)
		return
	import ctypes
	import ctypes.wintypes as wintypes
	user32 = ctypes.windll.user32

	log('  -- GetSystemMetrics --')
	sm_metrics = (
		('SM_CXSCREEN (primary width)', 0),
		('SM_CYSCREEN (primary height)', 1),
		('SM_XVIRTUALSCREEN (virtual desktop left)', 76),
		('SM_YVIRTUALSCREEN (virtual desktop top)', 77),
		('SM_CXVIRTUALSCREEN (virtual desktop width)', 78),
		('SM_CYVIRTUALSCREEN (virtual desktop height)', 79),
		('SM_CMONITORS (monitor count)', 80),
	)
	sm_values = {}
	for label, index in sm_metrics:
		value = probe(label, lambda index=index: user32.GetSystemMetrics(index))
		if value is not None:
			sm_values[index] = value

	log('  -- EnumDisplayMonitors --')
	try:
		class MONITORINFOEXW(ctypes.Structure):
			_fields_ = [
				('cbSize', wintypes.DWORD),
				('rcMonitor', wintypes.RECT),
				('rcWork', wintypes.RECT),
				('dwFlags', wintypes.DWORD),
				('szDevice', ctypes.c_wchar * 32),
			]

		MonitorEnumProc = ctypes.WINFUNCTYPE(wintypes.BOOL, ctypes.c_void_p, ctypes.c_void_p, ctypes.POINTER(wintypes.RECT), ctypes.c_void_p)

		def _enum_callback(hmonitor, _hdc, _lprect, _lparam):
			try:
				info = MONITORINFOEXW()
				info.cbSize = ctypes.sizeof(MONITORINFOEXW)
				if user32.GetMonitorInfoW(hmonitor, ctypes.byref(info)):
					MONITORS.append({
						'device': info.szDevice,
						'monitor': (info.rcMonitor.left, info.rcMonitor.top, info.rcMonitor.right, info.rcMonitor.bottom),
						'work': (info.rcWork.left, info.rcWork.top, info.rcWork.right, info.rcWork.bottom),
						'primary': bool(info.dwFlags & 1),
					})
			except Exception:
				pass
			return True

		# keep the callback object referenced for the duration of the call
		callback = MonitorEnumProc(_enum_callback)
		user32.EnumDisplayMonitors(None, None, callback, 0)
		for index, monitor in enumerate(MONITORS):
			left, top, right, bottom = monitor['monitor']
			log('  Monitor %d: %r%s' % (index, monitor['device'], ' (PRIMARY)' if monitor['primary'] else ''))
			log('    full rect: left=%d top=%d right=%d bottom=%d (%dx%d)' % (left, top, right, bottom, right - left, bottom - top))
			work_l, work_t, work_r, work_b = monitor['work']
			log('    work area: left=%d top=%d right=%d bottom=%d (%dx%d)' % (work_l, work_t, work_r, work_b, work_r - work_l, work_b - work_t))
			if not monitor['primary'] and SECONDARY_POINT is None:
				SECONDARY_POINT = (left + 50, top + 50)
		if len(MONITORS) > 1:
			log('  NOTE: multiple monitors detected (%d)' % len(MONITORS))
		if not MONITORS:
			log('  <no monitors reported>')
	except Exception:
		log('  EnumDisplayMonitors failed:')
		log(traceback.format_exc())

	log('  -- DPI awareness --')
	awareness = None
	try:
		value = ctypes.c_int(-1)
		hresult = ctypes.windll.shcore.GetProcessDpiAwareness(None, ctypes.byref(value))
		awareness = value.value
		names = {0: 'DPI_UNAWARE (Windows scales/virtualizes all coordinates)', 1: 'SYSTEM_DPI_AWARE', 2: 'PER_MONITOR_DPI_AWARE'}
		log('  GetProcessDpiAwareness = %d (%s) [hresult=%d]' % (awareness, names.get(awareness, 'unknown'), hresult))
	except Exception as exception:
		log('  GetProcessDpiAwareness = <error: %r>' % exception)
	probe('IsProcessDPIAware', lambda: bool(user32.IsProcessDPIAware()))
	system_dpi = probe('GetDpiForSystem', lambda: user32.GetDpiForSystem())
	if ROOT is not None:
		def _window_dpi():
			try:
				hwnd = int(ROOT.wm_frame(), 16)
			except Exception:
				hwnd = ROOT.winfo_id()
			return user32.GetDpiForWindow(hwnd)
		probe('GetDpiForWindow(root)', _window_dpi)

	if awareness == 0 and system_dpi and system_dpi > 96:
		anomaly('Process is DPI-unaware and system DPI is %d - Windows virtualizes ALL coordinates Tk sees, so positions/sizes will not match physical pixels' % system_dpi)
	if TK_SCREEN and 0 in sm_values and 1 in sm_values:
		if (sm_values[0], sm_values[1]) != TK_SCREEN:
			anomaly('Tk screen size %r differs from GetSystemMetrics primary %r - coordinate systems disagree (DPI awareness mismatch)' % (TK_SCREEN, (sm_values[0], sm_values[1])))
	if 76 in sm_values and 77 in sm_values and (sm_values[76], sm_values[77]) != (0, 0):
		log('  NOTE: virtual desktop origin is (%d,%d) - a monitor exists left of / above the primary' % (sm_values[76], sm_values[77]))


# ---------------------------------------------------------------------------
# Section 4: Settings files (read-only dump)
# ---------------------------------------------------------------------------

def _collect_geometry_strings(value, path, out):
	if isinstance(value, dict):
		for key in sorted(value.keys()):
			_collect_geometry_strings(value[key], path + '.' + key, out)
	elif isinstance(value, str):
		out.append((path, value))


def section_settings():
	global CODE_EDIT_SAVED
	for name in ('PyAI', 'PyMS'):
		path = os.path.join(SCRIPT_DIR, 'Settings', name + os.extsep + 'txt')
		log('  -- %s --' % path)
		if not os.path.isfile(path):
			log('  <file does not exist>')
			continue
		probe('size (bytes)', lambda path=path: os.path.getsize(path))
		probe('modified', lambda path=path: datetime.datetime.fromtimestamp(os.path.getmtime(path)).isoformat())
		try:
			with open(path, 'r', encoding='utf-8') as settings_file:
				raw = settings_file.read()
		except Exception:
			log('  <could not read file>')
			log(traceback.format_exc())
			continue
		log('  ---- raw contents start ----')
		log(raw)
		log('  ---- raw contents end ----')
		if name != 'PyAI':
			continue
		try:
			data = json.loads(raw)
		except Exception as exception:
			anomaly('Settings/PyAI.txt is not valid JSON (%r) - PyAI will discard it and fall back to defaults' % exception)
			continue
		_collect_geometry_strings(data.get('windows', {}), 'windows', USER_GEOMETRIES)
		log('  Saved window geometries found:')
		for geometry_path, geometry_string in USER_GEOMETRIES:
			log('    %s = %r' % (geometry_path, geometry_string))
			if geometry_path == 'windows.code_edit':
				CODE_EDIT_SAVED = geometry_string
		if not USER_GEOMETRIES:
			log('    <none>')


# ---------------------------------------------------------------------------
# Section 5: Pure-logic clamp battery (uses the real PyMS code, no windows)
# ---------------------------------------------------------------------------

SYNTHETIC_CASES = (
	('fully on primary', '865x493+400+300'),
	('exactly fills primary', '{W}x{H}+0+0'),
	('partially off right edge', '800x600+{W_MINUS_400}+200'),
	('partially off bottom edge', '800x600+200+{H_MINUS_300}'),
	('on a right-hand second monitor', '800x600+{W_PLUS_580}+200'),
	('on a left-hand second monitor (negative x)', '800x600+-{W}+200'),
	('on a monitor above (negative y)', '800x600+200+-{H_PLUS_120}'),
	('maximized flag (^ suffix)', '1136x670+100+100^'),
	('bigger than the screen', '3000x2000+0+0'),
	('Windows zoomed rect saved as normal (primary)', '{W_PLUS_16}x{H_PLUS_16}+-8+-8'),
	('Windows zoomed rect saved as normal (second monitor)', '{W_PLUS_16}x{H_PLUS_16}+{W_MINUS_8}+-8'),
	('previously-mangled 1px-wide save', '1x600+{W_PLUS_580}+200'),
)


def _fill_case(template, screen_w, screen_h):
	return (template
		.replace('{W_MINUS_400}', str(screen_w - 400))
		.replace('{H_MINUS_300}', str(screen_h - 300))
		.replace('{W_PLUS_580}', str(screen_w + 580))
		.replace('{H_PLUS_120}', str(screen_h + 120))
		.replace('{W_PLUS_16}', str(screen_w + 16))
		.replace('{H_PLUS_16}', str(screen_h + 16))
		.replace('{W_MINUS_8}', str(screen_w - 8))
		.replace('{W}', str(screen_w))
		.replace('{H}', str(screen_h)))


def _bounds_text(bounds):
	return '%dx%d at %d,%d' % (bounds.size.width, bounds.size.height, bounds.pos.x, bounds.pos.y)


def _screen_bounds(screen_w, screen_h):
	return Utils.Rect(Utils.Point(0, 0), Utils.Size(screen_w, screen_h))


def desktop_bounds(window):
	"""The clamp bounds load_size uses: the virtual desktop unioned with the primary screen."""
	screen = _screen_bounds(window.winfo_screenwidth(), window.winfo_screenheight())
	if not CLAMP_IS_FIXED:
		return screen
	vroot = Utils.Rect(
		Utils.Point(window.winfo_vrootx(), window.winfo_vrooty()),
		Utils.Size(window.winfo_vrootwidth(), window.winfo_vrootheight())
	)
	return vroot.union(screen)


def _clamp_issues(saved, result, bounds):
	"""Regression checks for the fixed clamp: sizes must never shrink below the saved size
	(beyond capping to the desktop) and the window must always overlap the desktop."""
	issues = []
	if result.size.width < min(saved.size.width, bounds.size.width):
		issues.append('width shrunk to %d (saved %d)' % (result.size.width, saved.size.width))
	if result.size.height < min(saved.size.height, bounds.size.height):
		issues.append('height shrunk to %d (saved %d)' % (result.size.height, saved.size.height))
	if result.pos.x >= bounds.max_x or result.pos.x + result.size.width <= bounds.pos.x:
		issues.append('no horizontal overlap with the desktop (x=%d)' % result.pos.x)
	if result.pos.y >= bounds.max_y or result.pos.y + result.size.height <= bounds.pos.y:
		issues.append('no vertical overlap with the desktop (y=%d)' % result.pos.y)
	return issues


def _run_clamp_case(name, saved_text, bounds, min_w, min_h, record):
	saved = Utils.Geometry.parse(saved_text)
	if saved is None:
		log('  %-46s %r -> <Geometry.parse REJECTED it>' % (name + ':', saved_text))
		return
	result = Utils.Geometry.parse(saved_text)
	result.clamp(bounds=bounds, min_size=Utils.Size(min_w, min_h))
	issues = _clamp_issues(saved, result, bounds)
	log('  %-46s %r -> %r%s' % (name + ':', saved_text, result.text, ('  <-- ' + ', '.join(issues)) if issues else ''))
	if issues:
		record('clamp of %r (bounds %s, minsize %dx%d) produced %r: %s' % (saved_text, _bounds_text(bounds), min_w, min_h, result.text, ', '.join(issues)))


def section_clamp_battery():
	if PYMS_IMPORT_ERROR:
		log('  Skipped: PyMS could not be imported.')
		return
	if not CLAMP_IS_FIXED:
		anomaly('This PyMS installation predates the multi-monitor geometry fixes - update PyMS and re-run')
		return
	log('  Any FINDING in this section indicates a regression in the fixed clamp behavior.')

	runs = [('assumed single 1920x1080 monitor', 1920, 1080, _screen_bounds(1920, 1080))]
	if TK_SCREEN:
		if TK_SCREEN != (1920, 1080):
			runs.append(("this machine's primary screen only", TK_SCREEN[0], TK_SCREEN[1], _screen_bounds(TK_SCREEN[0], TK_SCREEN[1])))
		if ROOT is not None:
			real_bounds = desktop_bounds(ROOT)
			if real_bounds != _screen_bounds(TK_SCREEN[0], TK_SCREEN[1]):
				runs.append(("this machine's full virtual desktop (what load_size actually uses)", TK_SCREEN[0], TK_SCREEN[1], real_bounds))

	for run_label, fill_w, fill_h, bounds in runs:
		log('')
		log('  Scenarios sized against a %dx%d primary, clamped to %s (%s), minsize 1x1:' % (fill_w, fill_h, run_label, _bounds_text(bounds)))
		for name, template in SYNTHETIC_CASES:
			_run_clamp_case(name, _fill_case(template, fill_w, fill_h), bounds, 1, 1, finding)
		log('')
		log('  Key scenarios repeated with minsize 550x430:')
		for name, template in SYNTHETIC_CASES:
			if 'second monitor' in name or 'zoomed' in name:
				_run_clamp_case(name, _fill_case(template, fill_w, fill_h), bounds, 550, 430, finding)

	if not USER_GEOMETRIES:
		log('')
		log('  No saved geometries were found in Settings/PyAI.txt to analyze.')
		return
	if ROOT is None:
		log('')
		log('  No Tk root available - cannot analyze the saved geometries.')
		return
	bounds = desktop_bounds(ROOT)
	log('')
	log('  YOUR saved geometries from Settings/PyAI.txt, as load_size will restore them (desktop %s):' % _bounds_text(bounds))
	for geometry_path, geometry_string in USER_GEOMETRIES:
		saved = Utils.Geometry.parse(geometry_string)
		if saved is None:
			log('  %s = %r  (position-only or partial value)' % (geometry_path, geometry_string))
			continue
		result = Utils.Geometry.parse(geometry_string)
		result.clamp(bounds=bounds, min_size=Utils.Size(1, 1))
		if result.text == saved.text:
			log('  %s = %r  -> restored exactly' % (geometry_path, geometry_string))
		else:
			log('  %s = %r  -> adjusted to %r' % (geometry_path, geometry_string, result.text))
		issues = _clamp_issues(saved, result, bounds)
		if issues:
			anomaly('Saved geometry %s = %r would restore badly as %r: %s' % (geometry_path, geometry_string, result.text, ', '.join(issues)))


# ---------------------------------------------------------------------------
# Section 6+: Live Tk window tests
# ---------------------------------------------------------------------------

def make_top(title):
	# Real PyMS windows are UIKit.Toplevel (WindowExtensions) - the fixed maximize
	# detection only engages for those, so plain tkinter.Toplevel would not be representative
	if UIKit is not None:
		top = UIKit.Toplevel(ROOT)
	else:
		top = tkinter.Toplevel(ROOT)
	top.title(title)
	try:
		top.attributes('-alpha', 0.0)
	except Exception as exception:
		log('  (could not make test window invisible, it may flash briefly: %r)' % exception)
	top.resizable(True, True)
	return top


def settle(top, duration=0.15):
	try:
		top.update_idletasks()
	except Exception:
		pass
	end = time.time() + duration
	while time.time() < end:
		try:
			ROOT.update()
		except Exception:
			break
		time.sleep(0.02)


def geometry_delta(requested, actual):
	req = parse_geometry_tuple(requested)
	act = parse_geometry_tuple(actual)
	if req is None or act is None:
		return None
	return (act[0] - req[0], act[1] - req[1], act[2] - req[2], act[3] - req[3])


def _require_live():
	if ROOT is None:
		log('  Skipped: no Tk root available.')
		return False
	return True


def live_set_read():
	if not _require_live():
		return
	cases = [
		('on primary', '400x300+100+100'),
		('at origin', '400x300+0+0'),
		('negative x', '400x300+-200+100'),
	]
	if SECONDARY_POINT is not None:
		cases.append(('on secondary monitor', '400x300+%d+%d' % SECONDARY_POINT))
	for name, requested in cases:
		top = make_top('PyMS diagnostic - set/read')
		try:
			settle(top)
			top.geometry(requested)
			immediate = top.geometry()
			top.update_idletasks()
			after_idle = top.geometry()
			settle(top)
			settled = top.geometry()
			log('  %-22s set %r' % (name + ':', requested))
			log('    read immediately:        %r' % immediate)
			log('    after update_idletasks:  %r' % after_idle)
			log('    after ~150ms of updates: %r' % settled)
			delta = geometry_delta(requested, settled)
			if delta is not None:
				log('    settled delta (w,h,x,y) = %r' % (delta,))
				if abs(delta[2]) > POS_TOLERANCE or abs(delta[3]) > POS_TOLERANCE:
					anomaly('set/read position drift for %r: set %r, settled at %r' % (name, requested, settled))
				if abs(delta[0]) > SIZE_TOLERANCE or abs(delta[1]) > SIZE_TOLERANCE:
					anomaly('set/read size drift for %r: set %r, settled at %r' % (name, requested, settled))
			if after_idle != settled:
				anomaly('geometry read after update_idletasks (%r) differs from settled read (%r) - the window manager applies geometry asynchronously, so PyAI can read stale values' % (after_idle, settled))
		finally:
			try:
				top.destroy()
			except Exception:
				pass


def live_load_battery():
	if not _require_live():
		return
	if PYMS_IMPORT_ERROR:
		log('  Skipped: PyMS could not be imported.')
		return
	screen_w, screen_h = TK_SCREEN if TK_SCREEN else (1920, 1080)
	for name, template in SYNTHETIC_CASES:
		saved = _fill_case(template, screen_w, screen_h)
		top = make_top('PyMS diagnostic - load_size')
		try:
			settle(top)
			geometry_config = Config.WindowGeometry()
			geometry_config.decode(saved)
			if geometry_config.encode() != saved:
				log('  %-46s decode() REJECTED %r (stored %r)' % (name + ':', saved, geometry_config.encode()))
				continue
			min_size = top.minsize()
			bounds = desktop_bounds(top)
			predicted = None
			if CLAMP_IS_FIXED:
				# predict what load_size's clamp should request
				predicted = Utils.Geometry.parse(saved)
				predicted.clamp(bounds=bounds, min_size=Utils.Size(min_size[0], min_size[1]))
			try:
				geometry_config.load_size(top)
			except Exception as exception:
				log('  %-46s saved %r' % (name + ':', saved))
				log('    load_size RAISED: %r' % exception)
				finding('load_size of %r raised %r - a saved geometry like this crashes the window open sequence' % (saved, exception))
				continue
			settle(top)
			actual = top.geometry()
			state = top.wm_state()
			log('  %-46s saved %r (window minsize %r)' % (name + ':', saved, min_size))
			if predicted is not None:
				log('    load_size should request: %r' % predicted.text)
			log('    actual window ended at:   %r (wm_state=%r)' % (actual, state))
			saved_geometry = Utils.Geometry.parse(saved)
			actual_geometry = Utils.Geometry.parse(actual)
			if state == 'normal' and saved_geometry is not None and actual_geometry is not None:
				issues = _clamp_issues(saved_geometry, actual_geometry, bounds)
				if saved_geometry.size.width > bounds.size.width or saved_geometry.size.height > bounds.size.height:
					# oversized windows may additionally be constrained by the window manager
					issues = [issue for issue in issues if 'shrunk' not in issue]
				if issues:
					finding('live load_size of %r produced %r: %s' % (saved, actual, ', '.join(issues)))
		finally:
			try:
				top.destroy()
			except Exception:
				pass

	# The position-only format saved by non-resizable windows must decode and restore
	top = make_top('PyMS diagnostic - position only')
	try:
		settle(top)
		geometry_config = Config.WindowGeometry()
		geometry_config.decode('+250+260')
		if geometry_config.encode() != '+250+260':
			log('  position-only save "+250+260": decode() REJECTED it')
			finding('decode() rejected the position-only format saved by non-resizable windows')
		else:
			geometry_config.load_size(top)
			settle(top)
			log('  position-only save "+250+260" restored window at: %r' % top.geometry())
	finally:
		try:
			top.destroy()
		except Exception:
			pass


def _round_trip(label, initial_geometry):
	geometry_config = Config.WindowGeometry()
	top = make_top('PyMS diagnostic - save')
	try:
		settle(top)
		top.geometry(initial_geometry)
		settle(top)
		actual_before = top.geometry()
		geometry_config.save_size(top)
		encoded = geometry_config.encode()
		log('  %s:' % label)
		log('    window placed at:  %r (requested %r)' % (actual_before, initial_geometry))
		log('    save_size encoded: %r' % encoded)
	finally:
		try:
			top.destroy()
		except Exception:
			pass
	top = make_top('PyMS diagnostic - load')
	try:
		settle(top)
		geometry_config.load_size(top)
		settle(top)
		reloaded = top.geometry()
		log('    load_size restored: %r' % reloaded)
		delta = geometry_delta(encoded or '', reloaded)
		if delta is None:
			log('    <could not compare>')
		elif abs(delta[0]) > SIZE_TOLERANCE or abs(delta[1]) > SIZE_TOLERANCE or abs(delta[2]) > POS_TOLERANCE or abs(delta[3]) > POS_TOLERANCE:
			anomaly('save/load round-trip (%s) does not restore the window: saved %r but restored to %r' % (label, encoded, reloaded))
		else:
			log('    round-trip OK (delta w,h,x,y = %r)' % (delta,))
	finally:
		try:
			top.destroy()
		except Exception:
			pass


def live_round_trip():
	if not _require_live():
		return
	if PYMS_IMPORT_ERROR:
		log('  Skipped: PyMS could not be imported.')
		return
	_round_trip('window on primary monitor', '640x480+150+120')
	if SECONDARY_POINT is not None:
		_round_trip('window on SECONDARY monitor (the suspected failure sequence)', '640x480+%d+%d' % SECONDARY_POINT)
	else:
		log('  (no secondary monitor detected - skipping the secondary-monitor round-trip)')


def live_zoomed():
	if not _require_live():
		return
	if PYMS_IMPORT_ERROR:
		log('  Skipped: PyMS could not be imported.')
		return
	top = make_top('PyMS diagnostic - zoomed')
	geometry_config = Config.WindowGeometry()
	was_zoomed = False
	try:
		settle(top)
		top.geometry('640x480+150+120')
		settle(top)
		try:
			top.wm_state('zoomed')
		except Exception as exception:
			log('  wm_state("zoomed") raised %r - maximize testing is not possible on this platform.' % exception)
			return
		settle(top)
		was_zoomed = (top.wm_state() == 'zoomed')
		log('  wm_state after zoom request: %r' % top.wm_state())
		log('  raw geometry() while zoomed: %r' % top.geometry())
		zoomed_geometry = Utils.Geometry.of(top)
		log('  Geometry.of(window).maximized = %r' % zoomed_geometry.maximized)
		if was_zoomed and not zoomed_geometry.maximized:
			finding('Geometry.of does not report a zoomed window as maximized - the maximized state will not be saved')
		geometry_config.save_size(top)
		encoded = geometry_config.encode()
		log('  save_size on the zoomed window encoded: %r' % encoded)
		log('  wm_state after save_size: %r' % top.wm_state())
		if was_zoomed and (encoded is None or not encoded.endswith('^')):
			finding('save_size on a maximized window encoded %r without the "^" maximized flag - the window will not re-maximize on next open' % encoded)
	finally:
		try:
			top.destroy()
		except Exception:
			pass
	top = make_top('PyMS diagnostic - restore zoomed')
	try:
		settle(top)
		try:
			geometry_config.load_size(top)
			settle(top)
			log('  load_size of that saved value -> wm_state=%r geometry=%r' % (top.wm_state(), top.geometry()))
			if was_zoomed and top.wm_state() != 'zoomed':
				finding('a maximized save did not restore as maximized (wm_state=%r)' % top.wm_state())
		except Exception as exception:
			log('  load_size of that saved value RAISED: %r' % exception)
			finding('load_size of the zoomed-save value %r raised %r' % (geometry_config.encode(), exception))
	finally:
		try:
			top.destroy()
		except Exception:
			pass
	# Also verify an explicit '^' string restores as maximized
	geometry_config = Config.WindowGeometry()
	geometry_config.decode('640x480+150+120^')
	top = make_top('PyMS diagnostic - restore ^ flag')
	try:
		settle(top)
		try:
			geometry_config.load_size(top)
			settle(top)
			log('  load_size of "640x480+150+120^" -> wm_state=%r geometry=%r' % (top.wm_state(), top.geometry()))
		except Exception as exception:
			log('  load_size of "640x480+150+120^" RAISED: %r' % exception)
			finding('load_size of a "^"-suffixed (maximized) saved geometry raises %r - the "^" is passed through to Tk in the geometry string, which Tk rejects' % exception)
	finally:
		try:
			top.destroy()
		except Exception:
			pass


def live_code_edit_flow():
	if not _require_live():
		return
	if PYMS_IMPORT_ERROR:
		log('  Skipped: PyMS could not be imported.')
		return
	saved = CODE_EDIT_SAVED or '865x493+889+501'
	log('  Simulating PyAI\'s code edit window open sequence with saved geometry %r%s' % (saved, '' if CODE_EDIT_SAVED else ' (fallback sample - no saved value found)'))
	top = make_top('PyMS diagnostic - code edit flow')
	try:
		# step 1: widgets give the window its requested size
		filler = tkinter.Frame(top, width=865, height=493)
		filler.pack()
		top.update_idletasks()
		required = Utils.Size(top.winfo_reqwidth(), top.winfo_reqheight())
		log('  step 1 - widgets built, requested size: %dx%d' % (required.width, required.height))
		# step 2: PyMSDialog centers the window on the primary screen (position only)
		screen = Utils.Size(top.winfo_screenwidth(), top.winfo_screenheight())
		top.geometry(Utils.GeometryAdjust(pos=required.centered_in(screen)).text)
		settle(top)
		log('  step 2 - after centering: geometry=%r' % top.geometry())
		# step 3: PyMSDialog applies resizable
		top.resizable(True, True)
		# step 4: setup_complete -> load_size
		geometry_config = Config.WindowGeometry()
		geometry_config.decode(saved)
		log('  step 3 - minsize at load time: %r, resizable: %r' % (top.minsize(), top.resizable()))
		try:
			geometry_config.load_size(top)
		except Exception as exception:
			log('  step 4 - load_size RAISED: %r' % exception)
			anomaly('Simulated code edit window open with YOUR saved geometry %r crashed in load_size: %r' % (saved, exception))
			return
		settle(top)
		final = top.geometry()
		log('  step 4 - after load_size: geometry=%r wm_state=%r' % (final, top.wm_state()))
		saved_geometry = Utils.Geometry.parse(saved)
		final_geometry = Utils.Geometry.parse(final)
		if top.wm_state() == 'normal' and saved_geometry is not None and final_geometry is not None:
			issues = _clamp_issues(saved_geometry, final_geometry, desktop_bounds(top))
			if issues:
				anomaly('Simulated code edit window open with YOUR saved geometry %r ends at %r: %s' % (saved, final, ', '.join(issues)))
			else:
				log('  Result looks normal.')
	finally:
		try:
			top.destroy()
		except Exception:
			pass


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

def section_summary():
	if anomalies:
		log('  Machine-specific anomalies (%d):' % len(anomalies))
		for message in anomalies:
			log('    ANOMALY: %s' % message)
	else:
		log('  No machine-specific anomalies detected.')
	log('')
	if findings:
		log('  Behavioral findings (%d):' % len(findings))
		for message in findings:
			log('    FINDING: %s' % message)
	else:
		log('  No behavioral findings recorded.')


def main():
	started = time.time()
	log('PyMS window geometry diagnostic v%s' % VERSION)
	log('Run at: %s' % datetime.datetime.now().isoformat())
	log('Log file: %s' % LOG_PATH)

	run_section('Python / process environment', section_process)
	run_section('Tk environment', section_tk_env)
	run_section('Windows native monitor layout & DPI', section_windows_native)
	run_section('Settings files (read-only)', section_settings)
	run_section('Pure-logic geometry clamp tests (no windows)', section_clamp_battery)
	run_section('Live Tk: set/read geometry round-trip & timing', live_set_read)
	run_section('Live Tk: WindowGeometry.load_size scenario battery', live_load_battery)
	run_section('Live Tk: save_size -> load_size round-trip', live_round_trip)
	run_section('Live Tk: maximized (zoomed) window behavior', live_zoomed)
	run_section('Live Tk: code edit window open sequence simulation', live_code_edit_flow)
	run_section('Summary', section_summary)

	if ROOT is not None:
		try:
			ROOT.destroy()
		except Exception:
			pass

	log('')
	log('Diagnostic completed in %.1f seconds.' % (time.time() - started))
	log('Please send back the log file:')
	log('  %s' % LOG_PATH)
	try:
		input('\nDone. Press Enter to exit...')
	except Exception:
		pass


if __name__ == '__main__':
	main()
