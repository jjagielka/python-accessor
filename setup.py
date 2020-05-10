#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='python-accessor',
    version='0.0.1',
    description='Access nested dicts',
    author='Jakub Jagielka',
    author_email='jjagielka@gmail.com',
    url='https://github.com/jjagielka/python-accessor',
    packages=find_packages(exclude=('tests', 'docs')),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    keywords='accessor itemgetter rest api'
)
