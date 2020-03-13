import argparse
from colmap.read_write_model import read_model, CAMERA_MODEL_IDS
from deeparch.deeparc_reader import deeparc_reader

def main(args):
    #this is use for compare
    #o_cameras, o_images, o_points3d = read_model("D:/Datasets/teabottle_green/undistrort/sparse",'.bin')
    #print(o_cameras)
    deeparc_reader(args.input)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='deeparc2colmap.py - convert deeparc back to colmap bin format')
    parser.add_argument(
        '-i',
        '--input',
        type=str,
        # required=True,
        default='teabottle_green.deeparc',
        help='colmap model directory / colmap database file (.db)',
    )
    parser.add_argument(
        '-o',
        '--output',
        type=str,
        # required=True,
        default='output_model/teabottle_test/',
        help='colmap spare model output directory')
    main(parser.parse_args())