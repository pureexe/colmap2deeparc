# colmap to deeparch format
import argparse
from deeparch.writer import write_file
from deeparch.reader import database_reader, binary_reader, \
    detect_model, detect_database

def main(args):
    colmap_data = {}
    if detect_database(args.input):
        # if input is database file do read database
        colmap_data = database_reader(args.input,args.image_dir)
    elif detect_model(args.input):
        # if input is model do binary read
        colmap_data = binary_reader(args.input)
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
        '-d',
        '--image_dir',
        type=str,
        default='',
        help='image directory for get pixel info'
    )
    main(parser.parse_args())
