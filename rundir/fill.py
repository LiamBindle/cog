import argparse
import os
import shutil
import pathlib

import yaml

from jinja2 import Environment, FileSystemLoader

if __name__ == '__main__':
    with open('conf.yml', 'r') as conf_file:
        conf = yaml.safe_load(conf_file)

    for template_dir in conf['templates']:
        file_loader = FileSystemLoader(template_dir)
        env = Environment(loader=file_loader, comment_start_string='{##', comment_end_string='##}')
        for root, dirnames, filenames in os.walk(template_dir, followlinks=False):
            localroot = os.path.relpath(root, template_dir)
            for dir in dirnames:
                localdir = os.path.join(localroot, dir)
                pathlib.Path(localdir).mkdir(exist_ok=True)
            for fname in filenames:
                template_file = os.path.join(root, fname)
                localfname = os.path.join(localroot, fname)
                if os.path.islink(template_file):
                    if os.path.exists(localfname):
                        os.remove(localfname)
                    shutil.copy(template_file, localfname, follow_symlinks=False)
                else:
                    template = env.get_template(os.path.relpath(template_file, template_dir))
                    output = template.render(**conf)
                    with open(localfname, 'w') as f:
                        f.write(output)