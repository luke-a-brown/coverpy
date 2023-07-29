# -*- coding: utf-8 -*-
"""
Created on Mon Aug  1 17:09:40 2022

@author: Luke Brown
"""

from distutils.core import setup

setup(
    name = 'coverpy',
    packages = ['coverpy'],
    version = '0.1.0',
    description = 'Automated estimates of plant area index, vegetation cover, crown cover, crown porosity, and uncertainties from digital cover photography in Python',
    author = 'Luke A. Brown',
    author_email = 'l.a.brown4@salford.ac.uk',
    url = 'https://github.com/luke-a-brown/CoverPy',
    install_requires = ['rawpy',
                        'numpy',
                        'scikit-image',
                        'imageio',
                        'uncertainties']
)