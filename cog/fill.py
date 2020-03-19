import os
import shutil
import pathlib

import yaml
from jinja2 import Environment, FileSystemLoader

from cog.core import template_hook_file

if __name__ == '__main__':
    # Open the run directory's config file
    with open('conf.yml', 'r') as conf_file:
        conf = yaml.safe_load(conf_file)

    # For each template directory in "templates"
    for template_dir in conf['templates']:

        # Declare Jinja2 objects
        file_loader = FileSystemLoader(template_dir)
        env = Environment(loader=file_loader, comment_start_string='{##', comment_end_string='##}')\

        # Loop through all the files in the directory
        for root, dirnames, filenames in os.walk(template_dir, followlinks=False):
            localroot = os.path.relpath(root, template_dir)

            # Create directories
            for dir in dirnames:
                localdir = os.path.join(localroot, dir)
                pathlib.Path(localdir).mkdir(exist_ok=True)
            for fname in filenames:
                if fname == template_hook_file:
                    continue
                template_file = os.path.join(root, fname)
                localfname = os.path.join(localroot, fname)
                if os.path.islink(template_file):
                    if os.path.islink(localfname):
                        os.remove(localfname)
                    shutil.copy(template_file, localfname, follow_symlinks=False)
                else:
                    template = env.get_template(os.path.relpath(template_file, template_dir))
                    output = template.render(**conf)
                    with open(localfname, 'w') as f:
                        f.write(output)
