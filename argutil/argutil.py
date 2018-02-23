##
#  @package argutil
#  Package for streamlining command line parser creation

from argparse import (
    ArgumentParser,
    RawTextHelpFormatter,
    ArgumentDefaultsHelpFormatter,
    SUPPRESS
)
from .working_directory import WorkingDirectory
from . import defaults
import json
import os
import shutil
from sys import exit
from .deepcopy import deepcopy
import logging

VERSION = '1.1.0'

logger = logging.getLogger('argutil')
logger.setLevel(logging.ERROR)

try:
    FileNotFoundError
except NameError:
    FileNotFoundError = IOError


primitives = {
    'int': int,
    'float': float,
    'complex': complex,
    'str': str,
    'list': list,
    'tuple': tuple,
    'bytes': bytes,
    'memoryview': memoryview,
    'bytearray': bytearray,
    'range': range,
    'set': set,
    'frozenset': frozenset,
    'dict': dict,
}

# Python 2 compatibility
try:
    primitives['long'] = long
except NameError:
    pass

try:
    primitives['unicode'] = unicode
except NameError:
    pass

try:
    primitives['buffer'] = buffer
except NameError:
    pass

try:
    primitives['xrange'] = xrange
except NameError:
    primitives['xrange'] = range


class RawWithDefaultsFormatter(
    RawTextHelpFormatter,
    ArgumentDefaultsHelpFormatter
):
    pass


class ParserDefinition(object):
    @staticmethod
    def create(
        filepath,
        definitions_file=defaults.DEFINITIONS_FILE,
        defaults_file=defaults.DEFAULTS_FILE,
        fail_if_exists=False,
    ):
        module = get_module(filepath)
        if not os.path.isfile(filepath):
            argutil_path = os.path.abspath(__file__)
            argutil_dir = os.path.dirname(argutil_path)
            template_path = os.path.join(argutil_dir, defaults.TEMPLATE_FILE)
            shutil.copy2(template_path, filepath)
        if not os.path.isfile(definitions_file):
            save({'modules': {}}, definitions_file)
        json_data = load(definitions_file)
        if 'modules' not in json_data:
            raise KeyError(
                '{} does not contain key "modules"'.format(definitions_file)
            )
        if module in json_data:
            if fail_if_exists:
                raise KeyError('module already defined')
        else:
            json_data['modules'][module] = {'examples': [], 'args': []}
        save(json_data, definitions_file)
        return ParserDefinition(filepath, definitions_file, defaults_file)

    def __init__(
        self,
        filepath,
        definitions_file=defaults.DEFINITIONS_FILE,
        defaults_file=defaults.DEFAULTS_FILE
    ):
        self.filepath = filepath
        self.module = get_module(filepath)
        self.definitions_file = definitions_file
        self.defaults_file = defaults_file

    def add_example(
        self,
        usage,
        description='',
    ):
        if not isinstance(usage, str):
            raise ValueError('usage must be a string!')
        if not isinstance(description, str):
            raise ValueError('description must be a string!')
        json_data = load(self.definitions_file)
        example = {
            'usage': usage,
            'description': description
        }
        json_data['modules'][self.module]['examples'].append(example)
        save(json_data, self.definitions_file)

    def add_argument(
        self,
        name,
        short=None,
        **kwargs
    ):
        json_data = load(self.definitions_file)
        arg = {}
        if short is not None:
            arg['short'] = short
        arg['long'] = name
        params = {
            'action', 'nargs', 'const', 'default', 'type',
            'choices', 'required', 'help', 'metavar', 'dest'
        }
        for k, v in kwargs.items():
            if k not in params:
                raise KeyError('unrecognized key "{}"'.format(k))
            elif k == 'type' and isinstance(v, type):
                v = v.__name__
            arg[k] = v
        help = kwargs.get('help', None)
        help_err_msg = 'help must be None, a string, or a list of strings'
        if help is not None:
            if isinstance(help, str):
                help = help.split('\n')
            elif isinstance(help, list):
                for line in help:
                    if not isinstance(line, str):
                        raise TypeError(help_err_msg)
            else:
                raise TypeError(help_err_msg)
        arg['help'] = help

        json_data['modules'][self.module]['args'].append(arg)
        save(json_data, self.definitions_file)

    def set_defaults(self, **kwargs):
        json_data = load(self.defaults_file)
        if self.module not in json_data:
            json_data[self.module] = {}
        module = json_data[self.module]
        for k, v in kwargs.items():
            module[k] = v
        save(json_data, self.defaults_file)

    def get_defaults(self):
        json_data = load(self.defaults_file)
        return json_data.get(self.module, {})

    def config(self, configs=None):
        if configs:
            defaults = {}
            for k, v in [__split_any__(kv, '=:') for kv in configs]:
                if v[0] == '[' and v[-1] == ']':
                    v = [__parse_value__(s) for s in v[1:-1].split(',')]
                else:
                    v = __parse_value__(v)
                defaults[k] = v
            self.set_defaults(**defaults)
        else:
            defaults = self.get_defaults()
            return ['{}={}'.format(*t) for t in defaults.items()]

    def get_parser(self, env=None):
        with WorkingDirectory(self.filepath):
            if not os.path.isfile(self.definitions_file):
                logger.error(
                    'Argument definition file "{}" not found!'.format(
                        self.definitions_file
                    )
                )
                exit(1)
            if env is None:
                env = {}

            json_data = load(self.definitions_file)

            if 'modules' not in json_data:
                return ArgumentParser(
                    epilog='{} does not contain any modules'.format(
                        self.definitions_file
                    )
                )
            json_data = json_data['modules']
            if self.module not in json_data:
                return ArgumentParser(
                    epilog='No entry for {} in {}'.format(
                        self.module,
                        self.definitions_file
                    )
                )
            json_data = json_data[self.module]

            if os.path.isfile(self.defaults_file):
                defaults = load(self.defaults_file)
                if self.module in defaults:
                    defaults = defaults[self.module]
                else:
                    defaults = {}
            else:
                defaults = {}

            return __build_parser__(
                self.module,
                json_data,
                defaults=defaults,
                env=env
            )


def load(json_file, mode='a'):
    if mode in 'ar':
        if os.path.isfile(json_file):
            with open(json_file, 'r') as f:
                return json.load(f)
        elif mode == 'r':
            raise FileNotFoundError('file could not be read: ' + json_file)
    if mode in 'wca':
        return {}
    raise ValueError('Unknown file mode "{}"'.format(mode))


def save(json_data, json_file):
    with open(json_file, 'w') as f:
        f.write(json.dumps(json_data, indent=2))


def __split_any__(text, delimiters=[]):
    parts = [text]
    for delim in delimiters:
        parts = [p for ps in parts for p in ps.split(delim)]
    return parts


def __parse_value__(value):
    v = value.strip()
    try:
        if '.' in value:
            return float(v)
        else:
            return int(v)
    except ValueError:
        if v.lower() == 'true':
            return True
        elif v.lower() == 'false':
            return False
        elif v.lower() in ['none', 'null']:
            return None
        elif v[0] in '\'"' and v[-1] in '\'"':
            return v[1:-1]
        else:
            return v


def __add_argument_to_parser__(parser, param, env={}):
    param = dict(param)
    if 'help' in param:
        if param['help'] is None:
            param['help'] = SUPPRESS
        else:
            param['help'] = '\n'.join(
                h.format(**env) for h in param['help']
            )
    if 'type' in param:
        func = param['type']
        try:
            param['type'] = env[func]
        except KeyError:
            try:
                param['type'] = primitives[func]
            except KeyError:
                param['type'] = globals()[func]
    if 'long' not in param:
        raise ValueError('args must contain "long" key')
    long_form = param['long']
    del param['long']
    if 'short' in param:
        short_form = param['short']
        del param['short']
        parser.add_argument(short_form, long_form, **param)
    else:
        parser.add_argument(long_form, **param)


def __add_example_to_parser__(parserArgs, example):
    if 'epilog' not in parserArgs:
        parserArgs['epilog'] = 'examples:'
    parserArgs['epilog'] += '\n    {:<44}{}'.format(*(example.values()))


def __build_parser__(name, definition, defaults={}, env={},
                     subparsers=None, templates={}):
    parserArgs = dict(prog=name, formatter_class=RawWithDefaultsFormatter)

    if 'template' in definition:
        template_name = definition['template']
        if template_name not in templates:
            raise ValueError('unknown template ' + template_name)
        template = templates[template_name]
        if 'examples' in template:
            for example in template['examples']:
                __add_example_to_parser__(parserArgs, example)
    else:
        template = None

    if 'examples' in definition and definition['examples']:
        for example in definition['examples']:
            __add_example_to_parser__(parserArgs, example)

    if subparsers is None:
        parser = ArgumentParser(**parserArgs)
    else:
        for k in ['help', 'aliases']:
            if k in definition:
                parserArgs[k] = definition[k]
        parser = subparsers.add_parser(name, **parserArgs)
        if name in env:
            parser.set_defaults(func=env[name])
    if 'args' in definition:
        for param in definition['args']:
            __add_argument_to_parser__(parser, param, env)

    if template:
        if 'args' in template:
            for param in template['args']:
                __add_argument_to_parser__(parser, param, env)

    # Apply default values
    for k, v in defaults.items():
        try:
            defaults[k] = v.format(**env)
        except AttributeError:
            continue
    parser.set_defaults(**defaults)

    if 'templates' in definition:
        templates = dict(templates)
        for k, v in definition['templates'].items():
            if 'parent' in v:
                parent_name = v['parent']
                if parent_name not in templates:
                    raise ValueError('unknown parent template ' + parent_name)
                new_v = deepcopy(templates[parent_name])
                for k2, v2 in v.items():
                    if k2 not in new_v:
                        new_v[k2] = []
                    new_v2 = deepcopy(new_v[k2])
                    if k2 == 'args':
                        new_v2 = list(
                            {
                                v['long']: v for v in deepcopy(new_v2 + v2)
                            }.values()
                        )
                    else:
                        new_v2 += deepcopy(v2)
                    new_v[k2] = new_v2
                templates[k] = new_v
            else:
                templates[k] = v

    if 'modules' in definition:
        subparsers = parser.add_subparsers(dest='command')
        for name, submodule in definition['modules'].items():
            if name in defaults:
                sub_defaults = defaults[name]
            else:
                sub_defaults = {}
            __build_parser__(
                name,
                submodule,
                sub_defaults,
                env,
                subparsers,
                templates
            )

    return parser


def get_module(filepath):
    __filename__ = os.path.splitext(filepath)[0]
    return os.path.basename(__filename__)
