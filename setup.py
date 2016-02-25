#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
@author: sharpdeep
@file:setup.py
@time: 2016-02-24 22:15
"""
import codecs
import os
import sys

try:
	from setuptools import setup
except:
	from distutils.core import setup
"""
打包的用的setup必须引入，
"""


def read(fname):
	return codecs.open(os.path.join(os.path.dirname(__file__), fname)).read()


NAME = "wxrobot"

PACKAGES = ["WxRobot", ]

DESCRIPTION = "a python wechat robot framework for personal account"

LONG_DESCRIPTION = read("README.rst")

KEYWORDS = "wechat weixin robot wxrobot"

AUTHOR = "sharpdeep"

AUTHOR_EMAIL = "cairuishen@gmail.com"

URL = "https://github.com/sharpdeep/WxRobot"

VERSION = "0.13"

LICENSE = "MIT"

setup(
	name=NAME,
	version=VERSION,
	description=DESCRIPTION,
	long_description=LONG_DESCRIPTION,
	install_requires=['qrcode','requests','beautifulsoup4'],
	classifiers=[
		'License :: OSI Approved :: MIT License',
		'Programming Language :: Python :: 3.4',
		'Intended Audience :: Developers',
		'Operating System :: MacOS',
		'Operating System :: POSIX',
		'Operating System :: POSIX :: Linux',
		'Topic :: Software Development :: Libraries',
		'Topic :: Software Development :: Libraries :: Python Modules',
		'Topic :: Utilities',
	],
	keywords=KEYWORDS,
	author=AUTHOR,
	author_email=AUTHOR_EMAIL,
	url=URL,
	license=LICENSE,
	packages=PACKAGES,
	include_package_data=True,
	zip_safe=True,
)
