
import os

def resource_path(resource_filename: str, test_file_path: str) -> str:
	return os.path.join(os.path.dirname(test_file_path), resource_filename)

def data_to_hex(data: bytes, separator: str = ' ') -> str:
	return separator.join(f'{b:02X}' for b in data)
