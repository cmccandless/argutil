from setuptools import setup
from setuptools.config import read_configuration

conf_dict = read_configuration('setup.cfg')
long_desc = conf_dict['long_description']
try:
    import pypandoc
    long_desc = pypandoc.convert_text(long_desc, 'rst', 'md')
except (IOError, ImportError):
    pass

setup(long_description=long_desc)
