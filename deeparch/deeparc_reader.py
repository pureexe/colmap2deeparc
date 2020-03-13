def deeparc_reader(path):
    cameras = []
    images = []
    points3D = []
    with open(path,'r') as f:
        version_number = float(f.readline().strip())
        header = f.readline().strip()
        block_size, intrinsic_size, arc_size, ring_size, point3d_size = header.split(" ")
        blocks = read_block(f,block_size)
    return cameras, images, points3D

def read_block(f,size):
    blocks = []
    for i in range(size):
        blocks.append(f.readline())
    return blocks

def read_intrinsic(f,size):
    intrinsics = []
    for i in range(size):
        block = f.readline().strip().split(" ")
        intrinsic = {
            "center": [float(block[0]),float(block[1])],
            "focal": [],
            "distrotion" : []
        }
        focal_stop = 3+int(block[2])
        distrotion_start = 3+int(block[2])
        for j in range(3,focal_stop):
            intrinsic['focal'].append(block[j])
        """    
        for j in range(,int(block[2])):
            intrinsic['focal'].append(block[j])
        """
    return intrinsics

def read_extrinsics():
    extrinsics = []
    return extrinsics

def build_hemisphere():
    pass

def read_point3d():
    points = []
    return points