
from ...GRP import image_bounds


def grid(w,h, fill=1):
	return ((fill,) * w,) * h

def run():
	"""Image Bounds"""
	for w in range(1,32):
		for h in range(1,32):
			bx,by,bw,bh = image_bounds(grid(w,h))
			if bx != 0 or by != 0 or bw != w or bh != h:
				return '%d,%d %dx%d != 0,0 %dx%d' % (bx,by, bw,bh, w,h)
	return True
