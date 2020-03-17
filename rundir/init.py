import argparse
import os
import shutil
import pathlib

import yaml



def parse_grid_args(parser: argparse.ArgumentParser):
    parser.add_argument('-sf',
                        metavar='S',
                        type=float,
                        help='stretch factor')
    parser.add_argument('-lon0',
                        metavar='X',
                        type=float,
                        help='target longitude')
    parser.add_argument('-lat0',
                        metavar='Y',
                        type=float,
                        help='target latitude')
    parser.add_argument('-csres',
                        metavar='R',
                        type=int,
                        required=True,
                        help='cubed-sphere resolution')

    def parser_cb(args):
        grid_conf = {'cs_res': args.csres}
        if args.sf is not None:
            grid_conf = {
                **grid_conf,
                'stretch_factor': args.sf,
                'target_lat': args.lat0,
                'target_lon': args.lon0,
            }
        return {'grid': grid_conf}
    return parser_cb


def parse_job_args(parser: argparse.ArgumentParser):
    parser.add_argument('-ncores',
                        metavar='C',
                        type=int,
                        required=True,
                        help='total number of cores')
    parser.add_argument('-cpn',
                        metavar='P',
                        type=int,
                        required=True,
                        help='cores per node')
    parser.add_argument('-q',
                        metavar='Y',
                        type=str,
                        required=True,
                        help='job queue')

    def parser_cb(args):
        job_conf = {
            'queue': args.q,
            'cores_per_node': args.cpn,
            'num_cores': args.ncores,
            'num_nodes': args.ncores // args.cpn,
        }
        return {'job': job_conf}
    return parser_cb


def parse_paths_args(parser: argparse.ArgumentParser):
    parser.add_argument('-rst',
                        metavar='C',
                        type=str,
                        required=True,
                        help='restart file')

    def parser_cb(args):
        paths_conf = {
            'restart_file': args.rst
        }
        return {'paths': paths_conf}
    return parser_cb

def parse_templates_args(parser: argparse.ArgumentParser):
    parser.add_argument('templates',
                        type=str,
                        nargs='+',
                        help='template directories')

    def parser_cb(args):
        templates_conf = {
            'templates': [os.path.abspath(template_dir) for template_dir in args.templates]
        }
        return templates_conf
    return parser_cb




if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Initialize the cwd as a run directory')
    subparsers = parser.add_subparsers(dest='command')
    parse_grid = parse_grid_args(subparsers.add_parser('grid'))
    parse_job = parse_job_args(subparsers.add_parser('job'))
    parse_paths = parse_paths_args(subparsers.add_parser('paths'))
    parse_templates = parse_templates_args(subparsers.add_parser('templates'))
    args = parser.parse_args()

    if args.command == 'grid':
        conf = parse_grid(args)
    elif args.command == 'job':
        conf = parse_job(args)
    elif args.command == 'paths':
        conf = parse_paths(args)
    elif args.command == 'templates':
        conf = parse_templates(args)
    else:
        raise ValueError('Unknown command')

    if not os.path.exists('conf.yml'):
        pathlib.Path('conf.yml').touch()

    with open('conf.yml', 'r') as f:
        cur_conf = yaml.safe_load(f)
        if cur_conf is None:
            cur_conf = {}

    cur_conf.update(conf)

    with open('conf.yml', 'w') as f:
        yaml.dump(cur_conf, f)

    print('Updated conf.yml')

