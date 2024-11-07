
import re

SIGNED_INT = r'-128|-?(?:12[0-7]|1[01]\d|\d?\d)'
RE_COORDINATES = re.compile(r'^\s*\(\s*(%s)\s*,\s*(%s)\s*\)\s*(?:#.+)?$' % (SIGNED_INT,SIGNED_INT))
RE_DRAG_COORDS = re.compile(r'^(\s*\(\s*)(?:%s)(\s*,\s*)(?:%s)(\s*\)\s*(?:#.+)?)$' % (SIGNED_INT,SIGNED_INT))
