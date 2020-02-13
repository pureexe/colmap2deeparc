import os
from colmap.database import COLMAPDatabase
from colmap.read_write_model import read_model
import numpy as np

def parse_intrinsic_params(model,params):
    if model == 'SIMPLE_PINHOLE':
        return [
            params[1],
            params[2],
            1, #only 1 focal length
            params[0],
            0, # no distrotion
        ]
    elif model == 'PINHOLE':
        return [
            params[2],
            params[3],
            2, # 2 focal length
            params[0],
            params[1],
            0, # no distrotion
        ]
    elif model == 'SIMPLE_RADIAL':
        return [
                    params[1],
                    params[2],
                    1, #only 1 focal length
                    params[0],
                    1, # simple_radial have 1 distrotion parameter
                    params[3] 
                ]
            )
        elif model == 'RADIAL':
            instrinsic_info.append(
                [
                    params[1],
                    params[2],
                    1, #only 1 focal length
                    params[0],
                    2, # simple_radial have 1 distrotion parameter
                    params[3],
                    params[4]
                ]
            )
        else:
            raise RuntimeError(
                'Camera number {} using {} which is currently not support'
                    .format(cid, model)
            )

def binary_reader(binary_path):
    cameras, images, points3d = read_model(binary_path,'.bin')
    point2d_info = []
    instrinsic_info = []
    extrinsic_info = []
    point3d_info = []
    point3d_lookup = {}
    camera_lookup = {}

    #build point3d
    point_len = 0
    for point_id in points3d:
        pid, xyz, rgb, err, img_ids, kpt_ids = points3d[point_id]
        point3d_lookup[pid] = point_len
        point3d_info.append(np.concatenate((xyz, rgb)))
        point_len = point_len + 1

    #build camera 
    for cam_id in cameras:
        cid, model, w, h, params = cameras[cam_id]
        #<center_x> <center_y>  <num_of_focal_length> <focal_length_0> <focal_length_1> ... <num_of_distortion> <distrotion_0> <distrotion_1>
        




def database_reader():
    pass

def detect_database(database_path):
    """
    make sure file end with (.db) and db file also exist
    """
    if database_path[-3:] != '.db':
        return False
    if not os.path.exists(database_path):
        return False
    return True

def detect_model(model_path):
    """ 
        detect is this colmap model directory by detect 3 files
        which is cameras.bin images.bin and points3D.bin
    """
    paths = [
        os.path.join(model_path,'cameras.bin'),
        os.path.join(model_path,'images.bin'),
        os.path.join(model_path,'points3D.bin'),
    ]
    for path in paths:
        if not os.path.exists(path):
            return False
    return True