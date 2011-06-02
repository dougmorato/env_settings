#!/usr/bin/env python
#This file is part of hgnested.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.

import os
from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(name='hgreview',
    version='0.1',
    author='B2CK',
    author_email='info@b2ck.com',
    url="http://hg.openhex.org/hgreview",
    description="Mercurial extension to work with rietveld codereview",
    long_description=read('README'),
    packages=find_packages(),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Plugins',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Version Control',
    ],
    license='GPL-3',
    install_requires=[
        'Mercurial >= 1.5.0',
    ],
)
