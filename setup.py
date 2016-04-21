#!/usr/bin/python
# -*- coding: utf-8 -*-

# to upload to PyPi, see
# https://stackoverflow.com/questions/14219499/pypi-server-response-500 
#from distutils.core import setup
from setuptools import setup, find_packages
import os
import sys
import re


# a define the version sting inside the package
# see https://stackoverflow.com/questions/458550/standard-way-to-embed-version-into-python-package
VERSIONFILE="SiQt/_version.py"
verstrline = open(VERSIONFILE, "rt").read()
VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
mo = re.search(VSRE, verstrline, re.M)
if mo:
    version = mo.group(1)
else:
    raise RuntimeError("Unable to find version string in %s." % (VERSIONFILE,))

with open('README.rst', 'r') as fh:
    long_description = fh.read()


setup(name='SiQt',
      version=version,
      description='A compatibility library for PyQt4, PyQt5 and PySide',
      author='Roman Yurchak',
      author_email='rth.yurchak@gmail.com',
      url='https://github.com/rth/SiQt',
      license='MIT',
      packages=find_packages(),
      install_requires=['six'],
      long_description=long_description,
      classifiers=[
      # How mature is this project? Common values are
      #   3 - Alpha
      #   4 - Beta
      #   5 - Production/Stable
      #'Development Status :: 2 - Pre-Alpha',

      # Indicate who your project is intended for
      'Intended Audience :: Developers',
      'Topic :: Software Development :: Libraries :: Python Modules',

      # Pick your license as you wish (should match "license" above)
      'License :: OSI Approved :: MIT License',

      # Specify the Python versions you support here. In particular, ensure
      # that you indicate whether you support Python 2, Python 3 or both.
      'Programming Language :: Python :: 2',
      'Programming Language :: Python :: 2.7',
      'Programming Language :: Python :: 3',
      'Programming Language :: Python :: 3.3',
      'Programming Language :: Python :: 3.4',
      'Programming Language :: Python :: 3.5',
      ],
     )

