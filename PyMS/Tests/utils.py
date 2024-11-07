
import struct, os

def resource_path(resource_filename: str, test_file_path: str) -> str:
	return os.path.join(os.path.dirname(test_file_path), resource_filename)

def data_to_hex(data: bytes, separator: str = ' ') -> str:
	return separator.join('%02X' % b for b in data)
