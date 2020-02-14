import os
from colmap.database import COLMAPDatabase
from colmap.read_write_model import read_model
import numpy as np


def binary_reader(binary_path):
    cameras, images, points3d = read_model(binary_path,'.bin')
    
    point2d = []
    instrinsic = []
    extrinsic = []
    point3d = []
    
    #filter only useful point3d data
    point_len = 0
    for point_id in points3d:
        pid, xyz, rgb, err, img_ids, kpt_ids = points3d[point_id]
        point3d.append({
            'id': pid,
            'position': xyz,
            'color': rgb
        })

    #filter only useful point3d data
    for cam_id in cameras:
        cid, model, w, h, params = cameras[cam_id]
        instrinsic.append({
            'id': cid, 
            'model': model,
            'params': params
        })
    
    for image_id in images:
        img_id, qvec, tvec, camera_id, name, xys, point3d_ids = images[image_id]
        # filter only useful extrinsic data
        extrinsic.append({
            'id': img_id,
            'rotation': qvec,
            'translation': tvec
        })
        # filter only useful point2d data
        for i in range(len(xys)):
            if point3d_ids[i] != -1:
                x,y = xys[i]
                point2d.append({
                    'image_id': img_id,
                    'camera_id': camera_id,
                    'point3d_id': point3d_ids[i],
                    'position': xys[i]
                })
        

    return (point2d, instrinsic, extrinsic, point3d)


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