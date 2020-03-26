import numpy as np
from scipy.spatial.transform import Rotation

def detect_share_extrinsic(extrinsics):
    if 'name' in extrinsics[0] and extrinsics[0]['name'][:3] == 'cam':
        return True
    return False

def position_from_image_name(image_name):
    row = int(image_name[3:6])
    column = int(image_name.split('_')[1].split('.')[0])
    return row, column

def get_extrinsic_layout(extrinsics):
    max_row = 0
    max_col = 0
    for extrinsic in extrinsics:
        cam_id, view_id = position_from_image_name(extrinsic['name'])
        if max_row < cam_id:
            max_row = cam_id
        if max_col < view_id:
            max_col = view_id
    #index start from 0 so we need +1
    return max_row + 1, max_col + 1

def write_instrinsic(f, intrinsics):
    for intrinsic in intrinsics:
        params = intrinsic['params']
        f.write('{:f} {:f} 1 {:f} 1 {:f}\n'.format(
            params[1],
            params[2],
            params[0],
            params[3] 
        ))

def write_point3d(f, point3ds):
    for point3d in point3ds:
            x, y, z = point3d['position']
            #x,y,z = np.random.normal(0, 0.1, 3)
            r, g, b = point3d['color']
            f.write('{:f} {:f} {:f} {:d} {:d} {:d}\n'.format(
                float(x), float(y), float(z), int(r), int(g), int(b)
            ))

def camera_matrix(extrinsic):
    qvec = extrinsic['rotation']
    rotation = Rotation.from_quat([qvec[1],qvec[2],qvec[3],qvec[0]])
    cam_mat = np.eye(4)
    cam_mat[:3,:3] = rotation.as_dcm()
    cam_mat[:3,3] = extrinsic['translation']
    return cam_mat

def write_extrinsic_with_inv(f, extrinsic,refcam_inv):
    cam_mat = camera_matrix(extrinsic)
    cam_mat = np.matmul(cam_mat, refcam_inv)
    rotation = Rotation.from_dcm(cam_mat[:3,:3])
    rotvec = rotation.as_rotvec()
    tvec = cam_mat[:3,3]
    f.write('{:f} {:f} {:f} 3 {:f} {:f} {:f}\n'.format(
        tvec[0],
        tvec[1],
        tvec[2],
        rotvec[0],
        rotvec[1],
        rotvec[2]
    ))


def write_file(output_path, data, reference_model = None):
    api_version = 0.01
    point2ds, intrinsics, extrinsics, point3ds = data

    if reference_model is not None:
        extrinsics_for_point2d = extrinsics
        _, intrinsics, extrinsics, _ = reference_model
    else:
        extrinsics_for_point2d = extrinsics

    max_row = len(extrinsics)
    max_col = 0
    max_row, max_col = get_extrinsic_layout(extrinsics)
    
    with open(output_path,'w') as f:
        f.write('{:f}\n'.format(api_version)) #version at head
        #print file number
        f.write('{:d} {:d} {:d} {:d} {:d}\n'.format(
            len(point2ds),
            len(intrinsics),
            max_row,
            max_col,
            len(point3ds)
        ))

        point3d_ids = {}
        point3d_count = 0

        #build lookup for point2d
        for point3d in point3ds:
            point3d_ids[point3d['id']] = point3d_count
            point3d_count = point3d_count + 1

        # get row and column from image name 
        image_rc = {}
        for image in extrinsics_for_point2d:
            r,c = position_from_image_name(image['name'])
            image_rc[image['id']] = [r,c]
        for point2d in point2ds:
            point2d['rc'] = image_rc[point2d['image_id']]
        for point2d in point2ds:
            x,y = point2d['position']
            r,c = point2d['rc']
            f.write('{:d} {:d} {:d} {:f} {:f}\n'.format(
                int(r),
                int(c),
                int(point3d_ids[point2d['point3d_id']]),
                float(x),
                float(y)
            ))
        write_instrinsic(f,intrinsics)
        # sort extrinsic first
        extrinsic_row = {}
        extrinsic_col = {}
        for extrinsic in extrinsics:
            r,c = position_from_image_name(extrinsic['name'])
            # extrinsic of arc
            if c == 0:
                extrinsic_row[r] = extrinsic
            # extrinsic of base
            if r == 0 and c != 0:
                extrinsic_col[c] = extrinsic
        #origin rotation need to be Identity for compose
        refcam_mat = camera_matrix(extrinsic_row[0])
        refcam_inv = np.linalg.inv(refcam_mat)

        # apply rotation from refcam to all 3d point
        current_point = np.ones((4,1))
        for i in range(len(point3ds)):
            current_point[:3,0] = point3ds[i]['position']
            transform_point = np.matmul(refcam_mat,current_point)
            point3ds[i]['position'] = transform_point[:3,0]

        for i in range(max_row):
            write_extrinsic_with_inv(f, extrinsic_row[i], refcam_inv)
        for i in range(1,max_col):
            write_extrinsic_with_inv(f, extrinsic_col[i], refcam_inv)
        write_point3d(f, point3ds)
