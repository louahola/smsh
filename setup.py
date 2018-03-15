#!/usr/bin/env python
import os.path

from setuptools import setup, find_packages


here = os.path.abspath(os.path.dirname(__file__))

requires = [
    'argparse',
    'boto3'
]

setup_options = dict(
    name='smsh',
    version='0.0.1',
    description='Interactive Shell via SSM',
    long_description=open('README.md').read(),
    author='Lou Ahola',
    url='http://aws.amazon.com/cli/',
    packages=find_packages(exclude=['tests*']),
    install_requires=requires,
    license="Apache License 2.0",
    classifiers=(
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ),
    entry_points={
        'console_scripts': [
            'smsh=smsh.__main__:main'
        ]
    }
)

setup(**setup_options)
