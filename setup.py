#!/usr/bin/env python
# coding: utf-8

"""
luigi tasks for norm-data (dnb, viaf, dbpedia, and others)
"""

import os

try:
    from setuptools import setup
except:
    from distutils.core import setup


setup(name='triform',
      version='0.0.2',
      description='Gather data for a same-as service.',
      author='Martin Czygan',
      author_email='martin.czygan@gmail.com',
      packages=[
        'triform',
      ],
      package_dir={'triform': 'triform'},
)
