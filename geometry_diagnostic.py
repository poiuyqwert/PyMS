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

VERSION = '1.0'

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
try:
	from PyMS.Utilities import Config
	from PyMS.Utilities.UIKit import Utils
except Exception:
	PYMS_IMPORT_ERROR = traceback.format_exc()

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
			anomaly('Tk virtual root (%dx%d at %d,%d) differs from Tk screen size (%dx%d)' % (vroot_w, vroot_h, vroot_x or 0, vroot_y or 0, screen_w, screen_h))


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


def _clamp_issues(geometry, screen_w, screen_h):
	issues = []
	if geometry.size.width < 100:
		issues.append('very THIN (width=%d)' % geometry.size.width)
	if geometry.size.height < 100:
		issues.append('very SHORT (height=%d)' % geometry.size.height)
	if (geometry.pos.x >= screen_w or geometry.pos.y >= screen_h
			or geometry.pos.x + geometry.size.width <= 0 or geometry.pos.y + geometry.size.height <= 0):
		issues.append('entirely OFF the primary screen (pos +%d+%d)' % (geometry.pos.x, geometry.pos.y))
	elif (geometry.pos.x + geometry.size.width > screen_w or geometry.pos.y + geometry.size.height > screen_h
			or geometry.pos.x < 0 or geometry.pos.y < 0):
		issues.append('partially off the primary screen')
	return issues


def _run_clamp_case(name, saved, screen_w, screen_h, min_w, min_h, record):
	geometry = Utils.Geometry.parse(saved)
	if geometry is None:
		log('  %-46s %r -> <Geometry.parse REJECTED it>' % (name + ':', saved))
		return
	geometry.clamp(size=Utils.Size(screen_w, screen_h), min_size=Utils.Size(min_w, min_h))
	issues = _clamp_issues(geometry, screen_w, screen_h)
	log('  %-46s %r -> %r%s' % (name + ':', saved, geometry.text, ('  <-- ' + ', '.join(issues)) if issues else ''))
	if issues:
		record('load_size clamp of %r (screen %dx%d, minsize %dx%d) produces %r: %s' % (saved, screen_w, screen_h, min_w, min_h, geometry.text, ', '.join(issues)))


def section_clamp_battery():
	if PYMS_IMPORT_ERROR:
		log('  Skipped: PyMS could not be imported.')
		return

	screens = [('assumed 1920x1080 screen', 1920, 1080)]
	if TK_SCREEN and TK_SCREEN != (1920, 1080):
		screens.append(('this machine\'s Tk-reported primary screen', TK_SCREEN[0], TK_SCREEN[1]))

	for screen_label, screen_w, screen_h in screens:
		log('')
		log('  Synthetic scenarios on %s (%dx%d), minsize 1x1 (the default for PyAI\'s code edit window):' % (screen_label, screen_w, screen_h))
		for name, template in SYNTHETIC_CASES:
			_run_clamp_case(name, _fill_case(template, screen_w, screen_h), screen_w, screen_h, 1, 1, finding)
		log('')
		log('  Key scenarios repeated with minsize 550x430 (a window that sets a real minimum size):')
		for name, template in SYNTHETIC_CASES:
			if 'second monitor' in name or 'zoomed' in name:
				_run_clamp_case(name, _fill_case(template, screen_w, screen_h), screen_w, screen_h, 550, 430, finding)

	if not USER_GEOMETRIES:
		log('')
		log('  No saved geometries were found in Settings/PyAI.txt to analyze.')
		return
	if not TK_SCREEN:
		log('')
		log('  Tk screen size unavailable - cannot analyze the saved geometries against it.')
		return
	screen_w, screen_h = TK_SCREEN
	log('')
	log('  YOUR saved geometries from Settings/PyAI.txt, analyzed against the Tk primary screen (%dx%d):' % (screen_w, screen_h))
	for geometry_path, geometry_string in USER_GEOMETRIES:
		geometry = Utils.Geometry.parse(geometry_string)
		if geometry is None:
			log('  %s = %r  <-- not a full WxH+X+Y geometry (PyAI would ignore it on load)' % (geometry_path, geometry_string))
			continue
		on_primary = (0 <= geometry.pos.x and 0 <= geometry.pos.y
			and geometry.pos.x + geometry.size.width <= screen_w and geometry.pos.y + geometry.size.height <= screen_h)
		containing = None
		for monitor in MONITORS:
			left, top, right, bottom = monitor['monitor']
			center_x = geometry.pos.x + geometry.size.width // 2
			center_y = geometry.pos.y + geometry.size.height // 2
			if left <= center_x < right and top <= center_y < bottom:
				containing = monitor
				break
		monitor_note = ''
		if containing is not None:
			monitor_note = ' [center is on %r%s]' % (containing['device'], ' PRIMARY' if containing['primary'] else ' NON-PRIMARY')
		elif MONITORS:
			monitor_note = ' [center is not on ANY current monitor]'
		log('  %s = %r  fully-on-Tk-primary: %s%s' % (geometry_path, geometry_string, on_primary, monitor_note))
		if not on_primary:
			clamped = Utils.Geometry.parse(geometry_string)
			clamped.clamp(size=Utils.Size(screen_w, screen_h), min_size=Utils.Size(1, 1))
			issues = _clamp_issues(clamped, screen_w, screen_h)
			anomaly('Saved geometry %s = %r is NOT fully on the Tk primary screen; on load PyAI will clamp it to %r%s' % (
				geometry_path, geometry_string, clamped.text, (' (%s)' % ', '.join(issues)) if issues else ''))


# ---------------------------------------------------------------------------
# Section 6+: Live Tk window tests
# ---------------------------------------------------------------------------

def make_top(title):
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
			# predict what load_size's clamp should request
			predicted = Utils.Geometry.parse(saved)
			predicted.clamp(size=Utils.Size(screen_w, screen_h), min_size=Utils.Size(min_size[0], min_size[1]))
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
			log('    load_size should request: %r' % predicted.text)
			log('    actual window ended at:   %r (wm_state=%r)' % (actual, state))
			actual_tuple = parse_geometry_tuple(actual)
			if actual_tuple is not None:
				issues = []
				if actual_tuple[0] < 100:
					issues.append('very THIN (width=%d)' % actual_tuple[0])
				if actual_tuple[1] < 100:
					issues.append('very SHORT (height=%d)' % actual_tuple[1])
				if actual_tuple[2] >= screen_w or actual_tuple[3] >= screen_h:
					issues.append('positioned off the primary screen')
				if issues and state == 'normal':
					finding('live load_size of %r produced %r: %s' % (saved, actual, ', '.join(issues)))
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
		log('  wm_state after zoom request: %r' % top.wm_state())
		zoomed_raw = top.geometry()
		log('  raw geometry() while zoomed: %r' % zoomed_raw)
		zoomed_geometry = Utils.Geometry.of(top)
		log('  Geometry.of(window).maximized = %r' % zoomed_geometry.maximized)
		if top.wm_state() == 'zoomed' and not zoomed_geometry.maximized:
			finding('Tk geometry() for a zoomed window is %r with no "^" marker - PyMS save_size cannot detect the maximized state, so closing a maximized window saves the zoomed pixel rect as if it were a normal window position/size' % zoomed_raw)
		geometry_config.save_size(top)
		log('  save_size on the zoomed window encoded: %r' % geometry_config.encode())
		log('  wm_state after save_size: %r' % top.wm_state())
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
		final_tuple = parse_geometry_tuple(final)
		if final_tuple is not None and TK_SCREEN:
			issues = []
			if final_tuple[0] < 100:
				issues.append('very THIN (width=%d)' % final_tuple[0])
			if final_tuple[1] < 100:
				issues.append('very SHORT (height=%d)' % final_tuple[1])
			if final_tuple[2] >= TK_SCREEN[0] or final_tuple[3] >= TK_SCREEN[1]:
				issues.append('positioned off the primary screen')
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
