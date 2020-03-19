import argparse
import os.path
import pathlib

import yaml
from cog.core import ConfigurationError, TemplateDirectoryError, SettingsGroup


class SettingsSubArgParser(SettingsGroup):
    def __init__(self, group_name, subargparser: argparse.ArgumentParser, **group_def):
        super().__init__(group_name, **group_def)
        for name, field in self._fields.items():
            subargparser.add_argument(f'--{name}', type=field['type'], help=field['desc'])


if __name__ == '__main__':
    # Open conf dict
    pathlib.Path('conf.yml').touch()
    with open('conf.yml', 'r') as f:
        conf = yaml.safe_load(f)
    if conf is None:
        conf = {}

    try:
        # Determine stage. If "templates" is in conf then we're initializing sections and fields, otherwise we're
        # setting template directories.
        parser = argparse.ArgumentParser(description='Configure run directory settings.')
        if 'templates' not in conf:
            parser.add_argument('template_dirs', nargs='+', type=str, help='Paths to template directories')
            args = parser.parse_args()
            conf['templates'] = [os.path.abspath(template_dir) for template_dir in args.template_dirs]

            # Check template dirs exist
            for template_dir in conf['templates']:
                if not os.path.exists(template_dir):
                    raise ConfigurationError(f'template directory "{template_dir}" doesn\'t exist!')
                if not os.path.exists(os.path.join(template_dir, 'intf_decl.yml')):
                    raise ConfigurationError(f'template directory "{template_dir}" doesn\'t contain an intf_decl.yml file!')

            print("Updated run directory templates.")
        else:
            subparsers = parser.add_subparsers(dest='group')

            # Join template directory's interface declarations
            intf_decl = {}
            for template_dir in conf['templates'][::-1]:
                defs_fname = os.path.join(template_dir, 'intf_decl.yml')
                if os.path.exists(defs_fname):
                    with open(defs_fname, 'r') as f:
                        template_intf_decl = yaml.safe_load(f)
                        if template_intf_decl is None:
                            template_intf_decl = {}
                        intf_decl.update(template_intf_decl)

            # Make a dict of group parsers (so we can validate the settings)
            settings_groups = {}
            for group, group_def in intf_decl.items():
                settings_groups[group] = SettingsSubArgParser(group, subparsers.add_parser(group), **group_def)
            subparsers.add_parser('check')

            # Parse arguments
            args = parser.parse_args()
            new_values = vars(args)
            group = new_values.pop('group')
            if group is None:
                group = 'check'

            if group != 'check':
                # Fill conf group with values from arguments
                new_values = {k: v for k, v in new_values.items() if v is not None}
                if group not in conf:
                    conf[group] = {}
                conf[group].update(new_values)

                settings_groups[group].validate(**conf)
            else:
                # Loop through other groups
                errors = []
                for group_name in settings_groups:
                    try:
                        settings_groups[group_name].validate(**conf)
                    except ConfigurationError as e:
                        errors.append(str(e))
                if len(errors) > 0:
                    print(f"init.py: configuration error(s): {''.join(errors)}")
                    exit(1)
                else:
                    exit(0)

        with open('conf.yml', 'w') as f:
            yaml.safe_dump(conf, f)

    except ConfigurationError as e:
        print(f"init.py: configuration error(s): {str(e)}")
        exit(1)
    except TemplateDirectoryError as e:
        print(f"init.py: template error(s): {str(e)}")
        exit(1)



