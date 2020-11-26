# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open('requirements.txt') as f:
	install_requires = f.read().strip().split('\n')

# get version from __version__ variable in version2_app/__init__.py
from version2_app import __version__ as version

setup(
	name='version2_app',
	version=version,
	description='version 2 features',
	author='caratred',
	author_email='info@caratred.com',
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
