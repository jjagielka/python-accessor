#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='Accessor',
    version='0.0.1',
    description='Access nested dicts',
    long_description=open('README.md').read(),
    author='Jakub Jagielka',
    author_email='jjagielka@gmail.com',
    url='https://github.com/jjagielka/python-accessor',
    license=open('LICENSE').read(),
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
