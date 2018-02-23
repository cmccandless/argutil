from setuptools import setup
from setuptools.config import read_configuration
import pypandoc

conf_dict = read_configuration('setup.cfg')
long_desc = '\n'.join(
    pypandoc.convert('README.md', 'rst'),
    pypandoc.convert('LICENSE', 'rst', 'md')
)

setup(long_description=long_desc)
