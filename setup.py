from os.path import dirname, join
from setuptools import setup


def read(fname):
    """Return contents of file `fname` in this directory."""
    return open(join(dirname(__file__), fname)).read()


setup(
    name='workflow',
    version=read('src/workflow/version'),
    packages=['src/workflow'],
    package_data={'workflow': ['version', 'notificator']}
)
