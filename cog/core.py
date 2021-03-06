import pydoc


class ConfigurationError(ValueError):
    pass


class TemplateDirectoryError(ValueError):
    pass


def safe_field(group, name, **kwargs):
    required_params = ['type', 'desc']
    casts = [pydoc.locate, str]
    field = {'name': name}
    for param, cast in zip(required_params, casts):
        try:
            field[param] = cast(kwargs[param])
        except KeyError as e:
            raise TemplateDirectoryError(f'{group} field "{name}" is missing "{param}"')
    if not isinstance(field['type'], type):
        raise TemplateDirectoryError(f'{group} field "{name}"\'s type is not valid')
    return field


def safe_validate_decl(group, **kwargs):
    if not any([key in kwargs for key in ['required', 'valid_eval', 'invalid_eval']]):
        raise TemplateDirectoryError(f'a validate declaration in {group} is missing the evaluation type')
    if 'required' not in kwargs and 'error' not in kwargs:
        raise TemplateDirectoryError(f'an _eval validate declaration in {group} is missing "error"')
    return kwargs


class SettingsGroup:
    def __init__(self, group_name, **group_def):
        self._group_name = group_name
        if 'validate' in group_def:
            self._validating_statements = [safe_validate_decl(group_name, **validate_decl) for validate_decl in group_def.pop('validate')]
        else:
            self._validating_statements = []
        self._fields = {name: safe_field(group_name, name, **field_def) for name, field_def in group_def.items()}

    def validate(self, **groups):
        locals().update(**groups)
        errors = []

        if self._group_name not in groups:
            raise ConfigurationError(f'\n\t- {self._group_name} group is not configured')

        for statement_decl in self._validating_statements:
            try:
                if 'required' in statement_decl:
                    missing = [f'"{field}"' for field in statement_decl['required'] if field not in groups[self._group_name]]
                    if len(missing) > 0:
                        errors.append(f'required settings: {", ".join(missing)}')
                elif 'valid_eval' in statement_decl:
                    if not eval(statement_decl['valid_eval']):
                        errors.append(statement_decl['error'])
                elif 'invalid_eval' in statement_decl:
                    if eval(statement_decl['invalid_eval']):
                        errors.append(statement_decl['error'])
                else:
                    RuntimeError("This shouldn't happen!")
            except KeyError:
                pass
        if len(errors) > 0:
            raise ConfigurationError(''.join([f'\n\t- {e}' for e in errors]))


template_hook_file='cog.yml'