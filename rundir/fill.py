import argparse
import os
import shutil
import pathlib

import yaml

from jinja2 import Environment, FileSystemLoader

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generates a run directory conf file.')
    parser.add_argument('-i',
                        metavar='S',
                        type=str,
                        required=True,
                        help='path to config file')
    parser.add_argument('-t',
                        type=str,
                        nargs='+',
                        required=True,
                        help='path to templates')
    args = parser.parse_args()

    # Parse the input file
    with open(args.i, 'r') as file:
        conf = yaml.safe_load(file)

    output_dir = os.path.dirname(os.path.abspath(args.i))

    # Loop through files in template directory
    for template_dir in args.t:
        # Load templates
        file_loader = FileSystemLoader(template_dir)
        env = Environment(loader=file_loader, comment_start_string='{##', comment_end_string='##}')
        for root, dirs, files in os.walk(template_dir):
            # Copy directories over
            for dir in dirs:
                pathlib.Path(os.path.join(output_dir, dir)).mkdir(exist_ok=True)
            for file in files:
                rpath = os.path.relpath(os.path.join(root, file), template_dir)
                if os.path.islink(os.path.join(root, file)):
                    try:
                        shutil.copy(os.path.join(root, file), os.path.join(output_dir, rpath), follow_symlinks=False)
                    except FileExistsError:
                        print(f'File exists: {os.path.join(output_dir, rpath)}')
                else:
                    template = env.get_template(rpath)
                    output = template.render(**conf)
                    with open(os.path.join(output_dir, rpath), 'w') as f:
                        f.write(output)
