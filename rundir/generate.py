import argparse
import configparser

import pathlib

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generates a run directory conf file.')
    parser.add_argument('-i',
                        metavar='S',
                        type=str,
                        required=True,
                        help='path to config file')
    parser.add_argument('-o',
                        type=str,
                        required=True,
                        help='path of output directory')
    args = parser.parse_args()

    # Parse the input file
    conf = configparser.ConfigParser()
    conf.read(args.i)
    conf = {s: dict(conf.items(s)) for s in conf.sections()}
    print(conf)