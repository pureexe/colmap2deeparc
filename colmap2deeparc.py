# colmap to  format
import argparse
from deeparc.writer import write_file
from deeparc.reader import database_reader_bfs, binary_reader, \
    detect_model, detect_database

def main(args):
    colmap_data = {}
    reference_data = None
    if detect_database(args.input):
        # if input is database file do read database
        print("reading database")
        colmap_data = database_reader_bfs(
            args.input,
            args.image_dir,
            shift_point3d=[
                args.shift_point3d_x,
                args.shift_point3d_y,
                args.shift_point3d_z
            ]
        )
        if 'reference_camera_pose' in args and len(args.reference_camera_pose)> 0:
            print("use reference")
            filetype = '.bin' if detect_model(args.reference_camera_pose,filetype='.bin') else '.txt'
            reference_data = binary_reader(args.reference_camera_pose, filetype)

    elif detect_model(args.input,filetype='.bin'):
        colmap_data = binary_reader(args.input,filetype='.bin')
    elif detect_model(args.input,filetype='.txt'):
        colmap_data = binary_reader(args.input,filetype='.txt')
    else:
        raise RuntimeError(
            'input isn\'t valid colmap model (.bin) directory or database(.db)'
        )
    write_file(args.output,colmap_data,reference_data)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='colmap2deeparc.py - convert colmap into deeparc format')
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
        help='deeparc file output')
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
    parser.add_argument(
        '-sx',
        '--shift-point3d-x',
        type=float,
        default=0.0,
        help='shift point3d in x axis (only using .db as input)'
    )
    parser.add_argument(
        '-sy',
        '--shift-point3d-y',
        type=float,
        default=0.0,
        help='shift point3d in y axis (only using .db as input)'
    )
    parser.add_argument(
        '-sz',
        '--shift-point3d-z',
        type=float,
        default=0.0,
        help='shift point3d in z axis (only using .db as input)'
    )    
    main(parser.parse_args())
