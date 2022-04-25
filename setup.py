"""A setuptools based setup module.
See:
https://packaging.python.org/guides/distributing-packages-using-setuptools/
https://github.com/pypa/sampleproject
"""
from os.path import dirname, join
from setuptools import setup


def read(fname):
    """Return contents of file `fname` in this directory."""
    return open(
        join(dirname(__file__), fname),
        encoding='utf-8'
    ).read()


setup(
    name='workflow',
    version=read('src/workflow/version'),
    packages=['src/workflow'],
    package_data={'workflow': ['version', 'notificator']}
)
