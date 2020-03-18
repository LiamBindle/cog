import collections
import io
import argparse

import yaml
# conf.yaml ->  dict of kwargs -+-> templates -> output
#        ^-------init generator---------+


# Interface for defining configuration fields
# - dict -> ConfigurationEntry
# - dict of dicts -> ConfigurationEntryBundle (bundle of ConfigurationEntry)

# Interface for querying configuration fields
# ConfigurationEntriesBundle -> ConfigurationQuery (command line and wizard interfaces)
# Therefore ConfigurationEntriesBundle must provide:
# - group_name
# - entry definitions (name, type, description)
# - method for validating

# Interfaces for generating conf.yml files.
# - command line
# - wizard


class _MutableMap(collections.MutableMapping):
    def __init__(self, *args, **kwargs):
        self._store = dict()
        self._store.update(dict(*args, **kwargs))

    def __getitem__(self, item):
        return self._store[item]

    def __setitem__(self, item, value):
        self._store[item] = value

    def __delitem__(self, key):
        del self._store[key]

    def __iter__(self):
        return iter(self._store)

    def __len__(self) -> int:
        return len(self._store)

    def __str__(self) -> str:
        string_stream = io.StringIO()
        yaml.dump(self._store, string_stream)
        return string_stream.getvalue()


class EntryDefinition(_MutableMap):
    def __init__(self, name: str, type: str, desc="",):
        super().__init__(name=name, type=eval(type), desc=desc)


class GroupDefinition(_MutableMap):
    def __init__(self, group_name, validate=[], **spec_definitions):
        super().__init__(**{k: EntryDefinition(name=k, **v) for k, v in spec_definitions.items()})
        self._validating_statements = validate.copy()
        self._group_name = group_name

    def validate(self, **groups):
        # This function should return a tuple of (ok, bad variables, reasoning)
        #
        locals().update(**groups)
        for v in self._validating_statements:
            if 'required' in v:
                missing = [field for field in v['required'] if field not in groups[self._group_name]]
                if len(missing) > 0:
                    raise ValueError(', '.join(missing) + ' are required')
            elif 'valid_if_true' in v:
                if not eval(v['valid_if_true']):
                    raise ValueError(v['error'])
            elif 'valid_if_false' in v:
                if eval(v['valid_if_false']):
                    raise ValueError(v['error'])


class GroupArgParser(GroupDefinition):
    def __init__(self, group_name, subargparser: argparse.ArgumentParser, validate=[], **spec_definitions):
        super().__init__(group_name, validate, **spec_definitions)
        for field in spec_definitions.keys():
            subargparser.add_argument(f'--{field}', type=self[field]['type'], help=self[field]['desc'])




if __name__ == '__main__':
    import yaml

    with open('/home/liam/RunDirTemplates/templates/GCHPctm-13.0.0-alpha.3/foo.yml', 'r') as f:
        conf = yaml.safe_load(f)

    with open('/home/liam/RunDirTemplates/scratch/conf.yml', 'r') as f:
        filled = yaml.safe_load(f)

    #group = GroupDefinition(group_name='job', **conf['job'])
    #group.validate(**filled)

    arparser = argparse.ArgumentParser()
    subparser = arparser.add_subparsers(dest='command')
    GroupArgParser('job', subparser.add_parser('job'), **conf['job'])

    arparser.parse_args()