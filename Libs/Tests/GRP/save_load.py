
from ...utils import FFile
from ... import GRP

def run(path_to):
	"""Save then Load"""
	w = 16
	h = 16
	image = list(range(n*w,(n+1)*w) for n in range(h))

	saved_file = FFile()

	save_grp = GRP.GRP()
	save_grp.load_data(image)
	save_grp.save_file(saved_file)

	load_grp = GRP.GRP()
	load_grp.load_file(saved_file)

	if load_grp.width != w:
		return 'Width %d != %d' % (load_grp.width, w)

	if load_grp.height != h or len(load_grp.images[0]) != len(image):
		return 'Height %d != %d' % (load_grp.height, h)

	for y in range(h):
		for x in range(w):
			if load_grp.images[0][y][x] != image[y][x]:
				return "Images don't match at %d,%d (%d != %d)" % (x,y, load_grp.images[0][y][x], image[y][x])

	return True
