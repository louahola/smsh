# Copyright (C) 2018 Lou Ahola, HashChain Technology, Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import codecs
import os.path
import re

from setuptools import setup, find_packages


here = os.path.abspath(os.path.dirname(__file__))

requires = [
    'argparse',
    'boto3'
]


def read(*parts):
    return codecs.open(os.path.join(here, *parts), 'r').read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


setup(
    name='smsh',
    version=find_version('smsh', '__init__.py'),

    description='SSH-like Shell via AWS SSM',

    long_description=read('README.md'),
    long_description_content_type='text/markdown',

    author='Lou Ahola',
    author_email='lou@hashchain.ca',
    url='http://github.com/node40/smsh',

    packages=find_packages(exclude=['tests*']),
    install_requires=requires,

    license="GNU General Public License v3.0",
    classifiers=[
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6'
    ],

    test_suite='nose.collector',
    tests_require=['nose'],

    entry_points={
        'console_scripts': [
            'smsh=smsh.__main__:main'
        ]
    }
)
