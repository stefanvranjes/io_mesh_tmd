class ListDict(dict):
    def __init__(self):
        dict.__init__(self)
        self.list = []
        self._len = 0

    def add(self, item):
        """
        Add a value to the Set, return its position in it.
        """
        value = self.setdefault(item, self._len)
        if value == self._len:
            self.list.append(item)
            self._len += 1

        return value
    
BINARY_STRIDE_TRI = 8 * 3 + 4 + 4 * 3
BINARY_STRIDE_QUAD = 8 * 4 + 4 + 4 * 4
    
def _binary_read(data):
    # Skip header...

    import os
    import struct

    tri_offset = struct.unpack('<I', data.read(4))[0]
    quad_offset = struct.unpack('<I', data.read(4))[0]
    tri_count = struct.unpack('<H', data.read(2))[0]
    quad_count = struct.unpack('<H', data.read(2))[0]

    # temporery ramAddress fix
    quad_offset = quad_offset - tri_offset + 12
    tri_offset = 12

    data.seek(tri_offset, os.SEEK_SET)
    tri_unpack = struct.Struct('<20h').unpack_from
    tri_buf = data.read(BINARY_STRIDE_TRI * tri_count)
    for i in range(tri_count):
        # read the colors, uvs and points coordinates of each triangle
        pt = tri_unpack(tri_buf, BINARY_STRIDE_TRI * i)
        t = (pt[:3], pt[4:7], pt[8:11])
        yield tuple(tuple(map(float, tup)) for tup in t)

    data.seek(quad_offset, os.SEEK_SET)
    quad_unpack = struct.Struct('<26h').unpack_from
    quad_buf = data.read(BINARY_STRIDE_QUAD * quad_count)
    for j in range(quad_count):
        # read the colors, uvs and points coordinates of each quad
        pt = quad_unpack(quad_buf, BINARY_STRIDE_QUAD * j)
        t = (pt[:3], pt[4:7], pt[12:15], pt[8:11])
        yield tuple(tuple(map(float, tup)) for tup in t)

def read_tmd(filepath):
    import time
    start_time = time.process_time()

    indices, pts = [], ListDict()

    with open(filepath, 'rb') as data:
        # check for ascii or binary
        gen = _binary_read

        for pt in gen(data):
            # Add the triangle (quad) and the point.
            # If the point is already in the list of points, the
            # index returned by pts.add() will be the one from the
            # first equal point inserted.
            indices.append([pts.add(p) for p in pt])

    print('Import finished in %.4f sec.' % (time.process_time() - start_time))

    return indices, pts.list