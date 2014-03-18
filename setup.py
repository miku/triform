#!/usr/bin/env python
# coding: utf-8

"""
triform gathers data for a same-as hub, similar to sameas.org
"""

import os

try:
    from setuptools import setup
except:
    from distutils.core import setup


setup(name='triform',
      version='0.0.1',
      description='Gather data for a same-as service.',
      author='Martin Czygan',
      author_email='martin.czygan@gmail.com',
      packages=[
        'triform',
      ],
      package_dir={'triform': 'triform'},
      # package_data={'triform': ['assets/*']},
      scripts=[
        'bin/triform',
      ],
)
