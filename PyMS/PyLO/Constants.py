
import re

SIGNED_INT = r'-128|-?(?:12[0-7]|1[01]\d|\d?\d)'
RE_COORDINATES = re.compile(fr'^\s*\(\s*({SIGNED_INT})\s*,\s*({SIGNED_INT})\s*\)\s*(?:#.+)?$')
RE_DRAG_COORDS = re.compile(fr'^(\s*\(\s*)(?:{SIGNED_INT})(\s*,\s*)(?:{SIGNED_INT})(\s*\)\s*(?:#.+)?)$')
