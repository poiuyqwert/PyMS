
import struct, os

def resource_path(resource_filename, test_file_path): # type: (str, str) -> str
	return os.path.join(os.path.dirname(test_file_path), resource_filename)

def data_to_hex(data, separator=' '): # type: (str, str) -> str
	return separator.join('%02X' % struct.unpack('<B', b) for b in data)
