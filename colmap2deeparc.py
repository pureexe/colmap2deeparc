# colmap to deeparch format
import argparse
from deeparch.writer import write_file
from deeparch.reader import database_reader_bfs, binary_reader, \
    detect_model, detect_database

def main(args):
    colmap_data = {}
    if detect_database(args.input):
        # if input is database file do read database
        print("reading database")
        colmap_data = database_reader_bfs(args.input,args.image_dir, shift_point3d=[0.0,0.0,0.0])
        if 'reference_camera_pose' in args and len(args.reference_camera_pose)> 0:
            print("use reference")
            reference_data = binary_reader(args.reference_camera_pose)
            new_colmap_data = (colmap_data[0],reference_data[1],reference_data[2],colmap_data[3])
            colmap_data = new_colmap_data
    elif detect_model(args.input,filetype='.bin'):
        colmap_data = binary_reader(args.input,,filetype='.bin'))
    elif detect_model(args.input,filetype='.txt'):
        colmap_data = binary_reader(args.input,,filetype='.txt'))
    else:
        raise RuntimeError(
            'input isn\'t valid colmap model (.bin) directory or database(.db)'
        )
    write_file(args.output,colmap_data)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='colmap2deeparc.py - convert colmap into deeparch format')
    parser.add_argument(
        '-i',
        '--input',
        type=str,
        required=True,
        help='colmap model directory / colmap database file (.db)',
    )
    parser.add_argument(
        '-o',
        '--output',
        type=str,
        required=True,
        help='deeparch file output')
    parser.add_argument(
        '-r',
        '--reference-camera-pose',
        type=str,
        default='',
        help='reference camera pose model')
    parser.add_argument(
        '-d',
        '--image_dir',
        type=str,
        default='',
        help='image directory for get pixel info'
    )
    main(parser.parse_args())
