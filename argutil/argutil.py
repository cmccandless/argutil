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
import json
import os
import shutil
from sys import exit
from .deepcopy import deepcopy
import logging


logger = logging.getLogger('argutil')
logger.setLevel(logging.ERROR)


try:
    FileNotFoundError  # noqa: F821
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


def init(module, definitions_file='commandline.json'):
    module_path = '{}.py'.format(module)
    if not os.path.isfile(module_path):
        argutil_path = os.path.abspath(__file__)
        argutil_dir = os.path.dirname(argutil_path)
        template_path = os.path.join(argutil_dir, 'template.py')
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


def add_example(module, example_text, definitions_file='commandline.json'):
    if not isinstance(example_text, str):
        raise ValueError('example_text must be a string!')
    json_data = load(definitions_file)
    json_data['modules'][module]['examples'].append(example_text)
    save(json_data, definitions_file)


def add_argument(module, name, help='', short=None, action=None,
                 nargs=None, const=None, default=None, type=None,
                 choices=None, required=None, metavar=None, dest=None,
                 definitions_file='commandline.json'):
    json_data = load(definitions_file)
    arg = {}
    if short is not None:
        arg['short'] = short
    arg['long'] = name
    if action is not None:
        arg['action'] = action
    if nargs is not None:
        arg['nargs'] = nargs
    if const is not None:
        arg['const'] = const
    if default is not None:
        arg['default'] = default
    if type is not None:
        arg['type'] = type
    if choices is not None:
        arg['choices'] = choices
    if required is not None:
        arg['required'] = required
    if metavar is not None:
        arg['metavar'] = metavar
    if dest is not None:
        arg['dest'] = dest
    arg['help'] = help

    json_data['modules'][module]['args'].append(arg)
    save(json_data, definitions_file)


def set_defaults(module, args, defaults_file='defaults.json'):
    json_data = load(defaults_file)
    for k, v in args.items():
        json_data[module][k] = v
    save(json_data, defaults_file)


def get_defaults(module, defaults_file='defaults.json'):
    json_data = load(defaults_file)
    return json_data[module]


def split_any(text, delimiters=[]):
    parts = [text]
    for delim in delimiters:
        parts = [p for ps in parts for p in ps.split(delim)]
    return parts


def config(module, configs, defaults_file='defaults.json'):
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


def add_argument_to_parser(parser, param, env={}):
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


def add_example_to_parser(parserArgs, example):
    if 'epilog' not in parserArgs:
        parserArgs['epilog'] = 'examples:'
    parserArgs['epilog'] += '\n    {:<44}{}'.format(*(example.values()))


def _build_parser(name, definition, defaults={}, env={},
                  subparsers=None, templates={}):
    parserArgs = dict(prog=name, formatter_class=RawWithDefaultsFormatter)

    if 'template' in definition:
        template_name = definition['template']
        if template_name not in templates:
            raise ValueError('unknown template ' + template_name)
        template = templates[template_name]
        if 'examples' in template:
            for example in template['examples']:
                add_example_to_parser(parserArgs, example)
    else:
        template = None

    if 'examples' in definition and definition['examples']:
        for example in definition['examples']:
            add_example_to_parser(parserArgs, example)

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
            add_argument_to_parser(parser, param, env)

    if template:
        if 'args' in template:
            for param in template['args']:
                add_argument_to_parser(parser, param, env)

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
            _build_parser(
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
def create_parser(module, definitions_file='commandline.json',
                  defaults_file='defaults.json', env=None):
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

    return _build_parser(module, json_data, defaults=defaults, env=env)


def get_parser(__file__, env=None):
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
        return create_parser(__module__, env=env)
