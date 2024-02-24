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
BINARY_STRIDE_TRI2 = 2 * 3 + 4 + 2 * 3
BINARY_STRIDE_QUAD = 8 * 4 + 4 + 4 * 4
BINARY_STRIDE_QUAD2 = 2 * 4 + 4 + 2 * 4
BINARY_STRIDE_VERT = 4 * 2
TRANSLATE_FACTOR = 16
TRANSLATE_FACTOR_NRML = 4096

def translate(n):
    return float(n / TRANSLATE_FACTOR)

def translate2(n):
    return float(n / TRANSLATE_FACTOR_NRML)
    
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
        yield tuple(tuple(map(translate, tup)) for tup in t)

    data.seek(quad_offset, os.SEEK_SET)
    quad_unpack = struct.Struct('<26h').unpack_from
    quad_buf = data.read(BINARY_STRIDE_QUAD * quad_count)
    for j in range(quad_count):
        # read the colors, uvs and points coordinates of each quad
        pt = quad_unpack(quad_buf, BINARY_STRIDE_QUAD * j)
        t = (pt[:3], pt[4:7], pt[12:15], pt[8:11])
        yield tuple(tuple(map(translate, tup)) for tup in t)

def _binary_read2(data):
    # Skip header...

    import os
    import struct

    vert_offset = struct.unpack('<I', data.read(4))[0]
    nrml_offset = struct.unpack('<I', data.read(4))[0]
    tri_offset = struct.unpack('<I', data.read(4))[0]
    quad_offset = struct.unpack('<I', data.read(4))[0]
    tri_count = struct.unpack('<H', data.read(2))[0]
    quad_count = struct.unpack('<H', data.read(2))[0]
    bone_count = struct.unpack('<I', data.read(4))[0]
    vert_count = (nrml_offset - vert_offset) // 8

    # temporery ramAddress fix
    nrml_offset = nrml_offset - vert_offset + 24
    tri_offset = tri_offset - vert_offset + 24
    quad_offset = quad_offset - vert_offset + 24
    vert_offset = bone_count * 20 + 24

    verts, nors, indices = [], [], []

    data.seek(vert_offset, os.SEEK_SET)
    vert_unpack = struct.Struct('<4h').unpack_from
    vert_buf = data.read(BINARY_STRIDE_VERT * vert_count)
    for i in range(vert_count):
        pt = vert_unpack(vert_buf, BINARY_STRIDE_VERT * i)
        verts.append(map(translate, pt[:3]))
    
    data.seek(nrml_offset, os.SEEK_SET)
    nrml_unpack = struct.Struct('<4h').unpack_from
    nrml_buf = data.read(BINARY_STRIDE_VERT * vert_count)
    for j in range(vert_count):
        pt = nrml_unpack(nrml_buf, BINARY_STRIDE_VERT * j)
        nors.append(map(translate2, pt[:3]))

    data.seek(tri_offset, os.SEEK_SET)
    tri_unpack = struct.Struct('<8H').unpack_from
    tri_buf = data.read(BINARY_STRIDE_TRI2 * tri_count)
    for k in range(tri_count):
        # read uvs and triangles
        pt = tri_unpack(quad_buf, BINARY_STRIDE_TRI2 * k)
        indices.append(pt[:3])

    data.seek(quad_offset, os.SEEK_SET)
    quad_unpack = struct.Struct('<10H').unpack_from
    quad_buf = data.read(BINARY_STRIDE_QUAD2 * quad_count)
    for m in range(quad_count):
        # read uvs and quads
        pt = quad_unpack(quad_buf, BINARY_STRIDE_QUAD2 * m)
        indices.append(pt[:4])

    return verts, nors, indices

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

def read_tmd2(filepath):
    import time
    start_time = time.process_time()

    indices, nors, pts = [], [], []

    with open(filepath, 'rb') as data:
        # check for ascii or binary
        gen = _binary_read
        pts, nors, indices = gen(data)

    print('Import finished in %.4f sec.' % (time.process_time() - start_time))

    return indices, nors, pts