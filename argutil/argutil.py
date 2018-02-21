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


logger = logging.getLogger('argutil')
logger.setLevel(logging.ERROR)


try:
    FileNotFoundError
except NameError:
    FileNotFoundError = IOError


class RawWithDefaultsFormatter(
    RawTextHelpFormatter,
    ArgumentDefaultsHelpFormatter
):
    pass


def load(json_file, mode='a'):
    if mode in 'ar':
        if os.path.isfile(json_file):
            with open(json_file, 'r') as f:
                return json.load(f)
        elif mode == 'r':
            raise FileNotFoundError('file could not be read: ' + json_file)
    if mode in 'wca':
        return {'modules': {}}
    raise ValueError('Unknown file mode "{}"'.format(mode))


def save(json_data, json_file):
    with open(json_file, 'w') as f:
        f.write(json.dumps(json_data, indent=2))


def init(module, definitions_file=defaults.DEFINITIONS_FILE):
    module_path = '{}.py'.format(module)
    if not os.path.isfile(module_path):
        argutil_path = os.path.abspath(__file__)
        argutil_dir = os.path.dirname(argutil_path)
        template_path = os.path.join(argutil_dir, defaults.TEMPLATE_FILE)
        shutil.copy2(template_path, module_path)
    if not os.path.isfile(definitions_file):
        save({'modules': {}}, definitions_file)
    json_data = load(definitions_file)
    if 'modules' not in json_data:
        raise KeyError(
            '{} does not contain key "modules"'.format(definitions_file)
        )
    json_data['modules'][module] = {'examples': [], 'args': []}
    save(json_data, definitions_file)


def add_example(
    module,
    usage,
    description='',
    definitions_file=defaults.DEFINITIONS_FILE
):
    if not isinstance(usage, str):
        raise ValueError('usage must be a string!')
    if not isinstance(description, str):
        raise ValueError('description must be a string!')
    json_data = load(definitions_file)
    example = {
        'usage': usage,
        'description': description
    }
    json_data['modules'][module]['examples'].append(example)
    save(json_data, definitions_file)


def add_argument(module, name, short=None,
                 definitions_file=defaults.DEFINITIONS_FILE, **kwargs):
    json_data = load(definitions_file)
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
        arg[k] = v
    help = kwargs.get('help', None)
    if help is None:
        help = []
    elif isinstance(help, str):
        help = help.split('\n')
    elif isinstance(help, list):
        for line in help:
            if not isinstance(line, str):
                raise TypeError(
                    'help must be either a string or a list of strings'
                )
    else:
        raise TypeError('help must be either a string or a list of strings')
    arg['help'] = help

    json_data['modules'][module]['args'].append(arg)
    save(json_data, definitions_file)


def set_defaults(module, args, defaults_file=defaults.DEFAULTS_FILE):
    json_data = load(defaults_file)
    for k, v in args.items():
        json_data[module][k] = v
    save(json_data, defaults_file)


def get_defaults(module, defaults_file=defaults.DEFAULTS_FILE):
    json_data = load(defaults_file)
    return json_data[module]


def split_any(text, delimiters=[]):
    parts = [text]
    for delim in delimiters:
        parts = [p for ps in parts for p in ps.split(delim)]
    return parts


def config(module, configs, defaults_file=defaults.DEFAULTS_FILE):
    if len(configs) == 0:
        defaults = get_defaults(module, defaults_file=defaults_file)
        for t in defaults.items():
            yield '{}={}'.format(*t)
    else:
        defaults = {}
        for k, v in [split_any(kv, '=:') for kv in configs]:
            if v[0] == '[' and v[-1] == ']':
                v = [s.strip() for s in v[1:-1].split(',')]
            else:
                try:
                    v = float(v) if '.' in v else int(v)
                except ValueError:
                    if v.lower() == 'true':
                        v = True
                    elif v.lower() == 'false':
                        v = False
                    elif v.lower() == 'none':
                        v = None
            defaults[k] = v
        set_defaults(module, defaults, defaults_file=defaults_file)


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
                param['type'] = globals()[func]
            except KeyError:
                pass
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


##
#  @brief Builds an instance of argparse.ArgumentParser
#  @param [in] module Name of module
#  @param [in] [definitionsFile] Name of file containing argument definitions
#  @param [in] [defaultsFile] Name of file containing argument defaults
#  @return ArgumentParser
#
def __create_parser__(module, definitions_file=defaults.DEFINITIONS_FILE,
                      defaults_file=defaults.DEFAULTS_FILE, env=None):
    if not os.path.isfile(definitions_file):
        logger.error(
            'Argument definition file "{}" not found!'.format(
                definitions_file
            )
        )
        exit(1)
    if env is None:
        env = {}

    json_data = load(definitions_file)

    if 'modules' not in json_data:
        return ArgumentParser(
            epilog='{} does not contain any modules'.format(
                definitions_file
            )
        )
    json_data = json_data['modules']
    if module not in json_data:
        return ArgumentParser(
            epilog='No entry for {} in {}'.format(
                module,
                definitions_file
            )
        )
    json_data = json_data[module]

    if os.path.isfile(defaults_file):
        defaults = load(defaults_file)
        if module in defaults:
            defaults = defaults[module]
        else:
            defaults = {}
    else:
        logger.error('Defaults file "{}" not found!'.format(defaults_file))
        exit(1)

    return __build_parser__(module, json_data, defaults=defaults, env=env)


def get_parser(__file__, definitions_file=defaults.DEFINITIONS_FILE,
               defaults_file=defaults.DEFAULTS_FILE, env=None):
    if env is None:
        env = {}
    __filename__ = '.'.join(__file__.split(os.path.sep)[-1].split('.')[:-1])
    try:
        if __module__ is None:
            __module__ = __filename__
    except NameError:
        __module__ = __filename__
    if __module__.startswith('__') and __module__.endswith('__'):
        __module__ = os.path.basename(os.path.dirname(__file__))

    with WorkingDirectory(__file__):
        return __create_parser__(
            __module__,
            definitions_file,
            defaults_file,
            env=env
        )
