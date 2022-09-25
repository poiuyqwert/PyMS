
import pkware

from .....Utilities.PyMSError import PyMSError

class AlgorithmID:
	huffman     = 0x01
	zlib        = 0x02
	pkware      = 0x08 # Implode/Explode
	bz2         = 0x10
	# sparse      = 0x20
	wave_mono   = 0x40
	wave_stereo = 0x80

AlgorithmID.COMPRESSION_ORDER = [
	# AlgorithmID.sparse,
	AlgorithmID.wave_mono,
	AlgorithmID.wave_stereo,
	AlgorithmID.huffman,
	AlgorithmID.zlib,
	AlgorithmID.pkware,
	AlgorithmID.bz2
]

AlgorithmID.COMPRESSION_ALGORITHM = {

}
AlgorithmID.DECOMPRESSION_ALGORITHM = {
	AlgorithmID.pkware: pkware.explode
}

def compress(algorithm_ids, data):
	for algorithm_id in AlgorithmID.COMPRESSION_ORDER:
		if not (algorithm_id & algorithm_ids):
			continue
		algorithm = AlgorithmID.COMPRESSION_ALGORITHM.get(algorithm_id)
		if algorithm == None:
			raise PyMSError('Compression', "Unsupported or invalid algorithm ID '0x%02X'" % algorithm_id)
		data = algorithm(data)
	return data

def decompress(algorithm_ids, data):
	for algorithm_id in reversed(AlgorithmID.COMPRESSION_ORDER):
		if not (algorithm_id & algorithm_ids):
			continue
		algorithm = AlgorithmID.DECOMPRESSION_ALGORITHM.get(algorithm_id)
		if algorithm == None:
			raise PyMSError('Decompression', "Unsupported or invalid algorithm ID '0x%02X'" % algorithm_id)
		data = algorithm(data)
	return data

__all__ = [
	'AlgorithmID',
	'compress',
	'decompress'
]