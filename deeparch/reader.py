import os
from colmap.database import COLMAPDatabase, blob_to_array, pair_id_to_image_ids
from colmap.read_write_model import read_model, CAMERA_MODEL_IDS
import multiprocessing
import numpy as np
import sqlite3
import json
import sys
from collections import deque


def binary_reader(binary_path):
  cameras, images, points3d = read_model(binary_path,'.bin')
  point2d = []
  intrinsic = []
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

  #filter only useful intrinsic data
  for cam_id in cameras:
    cid, model, w, h, params = cameras[cam_id]
    intrinsic.append({
        'id': cid,
        'model': model,
        'params': params
    })
  for image_id in images:
    img_id, qvec, tvec, camera_id, name, xys, point3d_ids = images[image_id]
    extrinsic.append({
      'id': img_id,
      'name': name,
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

  return (point2d, intrinsic, extrinsic, point3d)

def database_reader_bfs(database_path,image_dir = ''):
  db = COLMAPDatabase.connect(database_path)
  c = db.cursor()
  c.execute('SELECT camera_id,model,params FROM cameras')
  cameras_data = c.fetchall()
  c.execute('SELECT image_id,camera_id FROM images')
  images_data = c.fetchall()
  c.execute("SELECT pair_id,rows,cols,data FROM two_view_geometries")
  matches_data = c.fetchall()
  c.execute("SELECT image_id,rows,cols,data FROM keypoints")
  keypoints_data = c.fetchall()
  db.close()

  keypoints = {}
  intrinsic = []
  extrinsic = []
  point2d = []
  point3d = []

  print("Building keypoint search")
  for keypoint_image in keypoints_data:
    img_id, r, c, data = keypoint_image
    kpt = blob_to_array(data, np.float32,(r,c))
    keypoints[img_id] = kpt[:, :2]
    print(kpt.shape)


  camera_lookup = {}
  for image in images_data:
    image_id, camera_id = image
    extrinsic.append({
      'id': image_id,
      'rotation': np.random.normal(size=4),
      'translation': np.random.normal(size=3)
    })
    camera_lookup[image_id] = camera_id

  for camera in cameras_data:
    camera_id, model, params = camera
    params = blob_to_array(params, np.float64)
    intrinsic.append({
      'id': camera_id,
      'model': CAMERA_MODEL_IDS[model][1],
      'params': params
    })

  print("Creating graph")
  edges = {}
  cc = 0
  for match_record in matches_data:
    image_from, image_to = pair_id_to_image_ids(match_record[0])
    image_from = int(image_from)
    image_to = int(image_to)
    if match_record[1] == 0: continue

    lookup = blob_to_array(match_record[3], np.int32, (match_record[1], match_record[2]))
    for pair in lookup:
      k0 = (image_from, pair[0])
      k1 = (image_to, pair[1])

      if k0 not in edges: edges[k0] = []
      if k1 not in edges: edges[k1] = []

      edges[k0].append(k1)
      edges[k1].append(k0)

    cc += 1
    if cc % 1000 == 0:
      print('%.2f%%' % (cc / len(matches_data) * 100))


  keypoint_counter = 0
  keypoint_ids = {}

  print("Assigning Ids")
  def bfs(node):
    q = deque()
    q.append(node)
    keypoint_ids[node] = keypoint_counter
    while q:
      node = q.popleft()
      for nnode in edges[node]:
        if nnode not in keypoint_ids:
          keypoint_ids[nnode] = keypoint_counter
          q.append(nnode)
  for k in edges:
    if k in keypoint_ids: continue
    bfs(k)
    keypoint_counter += 1

  print("Verifying track")
  lst = {}
  for k in edges:
    keypoint_id = keypoint_ids[k]
    if keypoint_id not in lst:
      lst[keypoint_id] = []
    lst[keypoint_id].append(k)

  remapper = {}
  num_bad = 0
  keypoint_counter = 0
  for l, v in lst.items():
    check = {}
    bad = False
    for kp in v:
      if kp[0] in check:
        bad = True
        break
      check[kp[0]] = 1
    if bad:
      num_bad += 1
      remapper[l] = -1
    else:
      remapper[l] = keypoint_counter
      keypoint_counter += 1

  print("Removing", num_bad)
  print("Good track", keypoint_counter)

  for k in edges:
    img_id = k[0]
    keypoint_id = remapper[keypoint_ids[k]]
    if keypoint_id == -1: continue
    point2d.append({
      'image_id': img_id,
      'camera_id': camera_lookup[img_id],
      'point3d_id': keypoint_id,
      'position': keypoints[img_id][k[1]]
    })

  for i in range(keypoint_counter):
    point3d.append({
      'id': i,
      'position': list(np.random.normal(0,0.1,3)),
      'color':  [255,255,255]
    })

  print("Done")
  print(keypoint_counter)
  return (point2d, intrinsic, extrinsic, point3d)

def database_reader(database_path,image_dir = ''):
    point2d = []
    instrinsic = []
    extrinsic = []
    point3d = []

    db = COLMAPDatabase.connect(database_path)
    c = db.cursor()
    c.execute('SELECT camera_id,model,params FROM cameras')
    cameras_data = c.fetchall()
    c.execute('SELECT image_id,camera_id FROM images')
    images_data = c.fetchall()
    c.execute("SELECT pair_id,rows,cols,data FROM matches")
    matches_data = c.fetchall()
    c.execute("SELECT image_id,rows,cols,data FROM keypoints")
    keypoints_data = c.fetchall()
    db.close()

    keypoint_search = {}
    match_from = {}
    total_image_list = []
    keypoint_counter = 0
    match_search = {}
    point2d_track = []

    print("building keypoint search")
    for keypoint_image in keypoints_data:
        img_id, r, c, data = keypoint_image
        kpt = blob_to_array(data,np.float32,(r,c))
        image_kpt = {}
        for i in range(r):
            u,v =  kpt[i,:2]
            image_kpt[i] = [u,v]
        keypoint_search[img_id] = image_kpt

    print("building match search")
    for match_record in matches_data:
        image_from , image_to = pair_id_to_image_ids(match_record[0])
        image_from = int(image_from)
        total_image_list.append(image_from)
        if match_record[1] != 0:
            if not image_from in match_from:
                match_from[image_from] = []
            match_from[image_from].append(match_record[0])
            lookup = blob_to_array(match_record[3],np.int32, (match_record[1],match_record[2]))
            match_search[match_record[0]] = dict(lookup)

    print("build point 2d track")
    for image_from, records in match_from.items(): # iterate over match pairs
        for kpt_id, [x,y] in keypoint_search[image_from].items(): # iterate over keypoint of image_from
            buffer = []
            for record in records: # iterate over its matched pair
                if kpt_id in match_search[record]:
                    _, image_to = pair_id_to_image_ids(record)
                    kpt_on_dest = match_search[record][kpt_id]
                    x_ ,y_ = keypoint_search[image_to][kpt_on_dest]
                    buffer.append({
                        'image': image_to,
                        'x': x_,
                        'y': y_,
                        'kpt_id': keypoint_counter
                    })
            if len(buffer) != 0:
                buffer.insert(0,{
                    'image': image_from,
                    'x': x,
                    'y': y,
                    'kpt_id': keypoint_counter
                })
                if keypoint_counter % 1000 == 0:
                    print(keypoint_counter)
                point2d_track = point2d_track + buffer
                keypoint_counter = keypoint_counter + 1

    print(keypoint_counter)
    print("done")
    # print(point2d_track)
    # with open("test.txt", "w") as fo:
      # json.dump(point2d_track, fo)
    exit()

    #create instrinsic
    for camera in cameras_data:
        camera_id, model, params = camera
        params = blob_to_array(params, np.float64)
        instrinsic.append({
            'id': camera_id, 
            'model': CAMERA_MODEL_IDS[model][1],
            'params': params
        })
    #create extrinsic
    camera_lookup = {}
    for image in images_data:
        image_id, camera_id = image
        extrinsic.append({
            'id': image_id,
            'rotation': np.random.normal(size=4), #fill by random
            'translation': np.random.normal(size=3)
        })
        camera_lookup[image_id] = camera_id
    #create point2d
    for point in point2d_track:
        point2d.append({
            'image_id': point['image'],
            'camera_id': camera_lookup[point['image']],
            'point3d_id': point['kpt_id'],
            'position': [point['x'],point['x']]
        })
    #create point3d
    for i in range(keypoint_counter):
        point3d.append({
            'id': i,
            'position': list(np.random.normal(0,0.1,3)),
            'color':  [255,255,255]
        })
    return (point2d, instrinsic, extrinsic, point3d)

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

def database_reader_dset(database_path,image_dir = ''):
  db = COLMAPDatabase.connect(database_path)
  c = db.cursor()
  c.execute('SELECT camera_id,model,params FROM cameras')
  cameras_data = c.fetchall()
  c.execute('SELECT image_id,camera_id FROM images')
  images_data = c.fetchall()
  c.execute("SELECT pair_id,rows,cols,data FROM matches")
  matches_data = c.fetchall()
  c.execute("SELECT image_id,rows,cols,data FROM keypoints")
  keypoints_data = c.fetchall()
  db.close()

  keypoints = {}
  intrinsic = []
  extrinsic = []
  point2d = []
  point3d = []

  print("building keypoint search")
  for keypoint_image in keypoints_data:
    img_id, r, c, data = keypoint_image
    kpt = blob_to_array(data, np.float32,(r,c))
    keypoints[img_id] = kpt[:, :2]

  camera_lookup = {}
  for image in images_data:
    image_id, camera_id = image
    extrinsic.append({
      'id': image_id,
      'rotation': np.random.normal(size=4),
      'translation': np.random.normal(size=3)
    })
    camera_lookup[image_id] = camera_id

  for camera in cameras_data:
    camera_id, model, params = camera
    params = blob_to_array(params, np.float64)
    intrinsic.append({
      'id': camera_id,
      'model': CAMERA_MODEL_IDS[model][1],
      'params': params
    })

  dset = {}
  print("creating disjoint set")
  cc = 0
  for match_record in matches_data:
    image_from, image_to = pair_id_to_image_ids(match_record[0])
    image_from = int(image_from)
    image_to = int(image_to)
    if match_record[1] == 0: continue

    lookup = blob_to_array(match_record[3], np.int32, (match_record[1], match_record[2]))
    for pair in lookup:
      k0 = (image_from, pair[0])
      k1 = (image_to, pair[1])

      if k0 in dset and k1 in dset: # par(k0) -> par(k1)
        tmp = []
        while dset[k1] != k1:
          tmp.append(k1)
          k1 = dset[k1]
        for t in tmp:
          dset[t] = k1

        while dset[k0] != k0:
          old = k0
          k0 = dset[k0]
          dset[old] = k1

        dset[k0] = k1

      elif k0 not in dset and k1 not in dset:
        dset[k0] = dset[k1] = k1
      elif k0 in dset and k1 not in dset:
        dset[k1] = k0
      else:
        dset[k0] = k1

    cc += 1
    if cc % 1000 == 0:
      print('%.2f%%' % (cc / len(matches_data) * 100))


  keypoint_counter = 0
  for k, v in dset.items():
    if k == v:
      dset[k] = keypoint_counter
      keypoint_counter += 1

  lst = {}

  for k, v in dset.items():
    while type(v) == tuple:
      v = dset[v]

    img_id, keypoint_id = k[0], v
    if keypoint_id not in lst:
      lst[keypoint_id] = []
    lst[keypoint_id].append(k)

    point2d.append({
      'image_id': img_id,
      'camera_id': camera_lookup[img_id],
      'point3d_id': keypoint_id,
      'position': keypoints[img_id]
    })
    point3d.append({
      'id': keypoint_id,
      'position': list(np.random.normal(0,0.1,3)),
      'color':  [255,255,255]
    })

  sizes = [len(lst[g]) for g in lst]
  sizes.sort()
  print("size max", max(sizes))
  for g in lst:
    if len(lst[g]) == 1308076:
      # print(lst[g])
      print("still found", g)

  print(sizes)
  print("done")
  print(len(point2d))
  print(len(dset))
  print(keypoint_counter)

  exit()
  return (point2d, intrinsic, extrinsic, point3d)
