import numpy as np
from scipy.spatial.transform import Rotation

def instrinsic_builder(intrisics):
    model = intrisics['model']
    params = intrisics['params']
    params.astype(np.float32)
    if model == 'SIMPLE_PINHOLE':
        return '{:f} {:f} 1 {:f} 0\n'.format(
            params[1],
            params[2],
            params[0],
        )
    elif model == 'PINHOLE':
        return "{:f} {:f} 2 {:f} {:f} 0\n".format(
            params[2],
            params[3],
            params[0],
            params[1],
        )
    elif model == 'SIMPLE_RADIAL':
        return '{:f} {:f} 1 {:f} 1 {:f}\n'.format(
            params[1],
            params[2],
            params[0],
            params[3] 
        )
    elif model == 'RADIAL':
        return '{:f} {:f} 1 {:f} 2 {:f} {:f}\n' [
            params[1],
            params[2],
            params[0],
            params[3],
            params[4]
        ]
    else:
        raise RuntimeError(
            'Camera number {} using {} which is currently not support'
                .format(intrisics['id'], model)
        )

def detech_share_extrinsic(extrinsics):
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

# ขโมย base เฉลี่ย คูณ inverse ของ base บริเวณ arc
# วิธีแปลง 0,0 เป็น identity ด้วย inverse

def write_instrinsic(f, intrinsics):
    for intrinsic in intrinsics:
        f.write(instrinsic_builder(intrinsic))

def write_point3d(f, point3ds):
    for point3d in point3ds:
            x, y, z = point3d['position']
            #x,y,z = np.random.normal(0, 0.1, 3)
            r, g, b = point3d['color']
            f.write('{:f} {:f} {:f} {:d} {:d} {:d}\n'.format(
                float(x), float(y), float(z), int(r), int(g), int(b)
            ))

def write_extrinsic_with_inv(f, extrinsic,origin_rot_inv):
    tvec = extrinsic['translation']
    qvec = extrinsic['rotation']
    rotation = Rotation.from_quat([qvec[1],qvec[2],qvec[3],qvec[0]])
    rot_mat = rotation.as_dcm()
    rot_mat = np.matmul(rot_mat, origin_rot_inv)
    rotation = Rotation.from_dcm(rot_mat)
    rotvec = rotation.as_rotvec()
    f.write('{:f} {:f} {:f} 3 {:f} {:f} {:f}\n'.format(
        tvec[0],
        tvec[1],
        tvec[2],
        rotvec[0],
        rotvec[1],
        rotvec[2]
    ))


def write_file(output_path, data):
    api_version = 0.01
    point2ds, intrinsics, extrinsics, point3ds = data
    share_extrinsic = detech_share_extrinsic(extrinsics) 
    max_row = len(extrinsics)
    max_col = 0
    if share_extrinsic:
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
            
        if share_extrinsic:
            # get row and column from image name 
            image_rc = {}
            for image in extrinsics:
                r,c = position_from_image_name(image['name'])
                image_rc[image['id']] = [r,c]
            for point2d in point2ds:
                point2d['rc'] = image_rc[point2d['image_id']]
            for point2d in point2ds:
                x,y = point2d['position']
                r,c = point2d['rc']
                f.write('{:d} {:d} {:d} {:f} {:f}\n'.format(
                    int(r),
                    int(r*max_col + c),
                    int(point3d_ids[point2d['point3d_id']]),
                    float(x),
                    float(y)
                ))
            write_instrinsic(f,intrinsics)
            # sort extrinsic first
            extrinsic_row = {}
            extrinsic_col = {}
            for extrinsic in extrinsics:
                r,c = image_rc[extrinsic['id']]
                # extrinsic of arc
                if c == 0:
                    extrinsic_row[r] = extrinsic
                # extrinsic of base
                if r == 0 and c != 0:
                    extrinsic_col[c] = extrinsic
            
            #origin rotation need to be Identity for compose
            ref_cam = extrinsic_row[0]
            qvec = extrinsic_row[0]['rotation']
            rotation = Rotation.from_quat([qvec[1],qvec[2],qvec[3],qvec[0]])
            rot_mat = rotation.as_dcm()            
            for point3d in point3ds:
                current_point = np.asarray(point3d['position']).reshape((3,1))
                transform_point = np.matmul(rot_mat,current_point)
                point3d['position'] = transform_point.reshape((3,))

            #extrinsic_mat = np.eye(4)
            #extrinsic_mat[:3,:3] = rot_mat
            #extrinsic_mat[:3,3] = extrinsic_row[0]['translation']

            #origin_rot_inv = rot_mat.T
            #origin_tran_inv = (-np.matmul(rot_mat.T,extrinsic_row[0]['translation'].reshape((3,1)))).reshape((3,))
            # origin_rot_inv = np.eye(3) # identifiy for debug
            for i in range(max_row):
                write_extrinsic_with_inv(f, extrinsic_row[i], origin_rot_inv)
            for i in range(1,max_col):
                write_extrinsic_with_inv(f, extrinsic_col[i], origin_rot_inv)    
            #write_extrinsic_with_inv(f, ref_cam, np.eye(3))
        else:
            for point2d in point2ds:
                x,y = point2d['position']
                f.write('{:d} {:d} {:d} {:f} {:f}\n'.format(
                    int(point2d['camera_id'] - 1), #index start from 0
                    int(point2d['image_id'] - 1),
                    int(point3d_ids[point2d['point3d_id']]),
                    float(x),
                    float(y)
                ))
            write_instrinsic(f,intrinsics)
            for extrinsic in extrinsics:
                tvec = extrinsic['translation']
                qvec = extrinsic['rotation']
                rotation = Rotation.from_quat([qvec[1],qvec[2],qvec[3],qvec[0]])
                rotvec = rotation.as_rotvec()
                f.write('{:f} {:f} {:f} 3 {:f} {:f} {:f}\n'.format(
                    tvec[0],
                    tvec[1],
                    tvec[2],
                    rotvec[0],
                    rotvec[1],
                    rotvec[2]
                ))
        write_point3d(f, point3ds)
        
