#!/usr/bin/env python
import os.path
import sys
from glob import glob

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


def readme():
    try:
        with open(os.path.join(os.path.dirname(__file__), 'README.md')) as f:
            return f.read()
    except (IOError, OSError):
        return ''


def get_version():
    src_path = os.path.join(os.path.dirname(__file__), 'src')
    sys.path = [src_path] + sys.path
    import findtools
    findtools.__path__
    return findtools.__version__


setup(
    name='findtools',
    version=get_version(),
    description='Extensions to basic disk tools like du, df, etc, but written in python',
    long_description=readme(),
    author='Yauhen Yakimovich',
    author_email='eugeny.yakimovitch@gmail.com',
    url='https://github.com/ewiger/disktools',
    license='MIT',
    #scripts=glob('bin/*'),
    #data_files=glob('libexec/*'),
    packages=['findtools'],
    package_dir={
        'disktools': 'src/disktools',
    },
    download_url='https://github.com/ewiger/disktools/tarball/master',
)
