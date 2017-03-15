# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open('requirements.txt') as reqs:
	install_requires = reqs.readlines()

setup(
	name = 'emec-api',
	version = '0.1.0',
	url = 'https://github.com/pavanad/emec-api',
	license = 'MIT License',
	author = 'Adilson Pavan',
	author_email = 'adilson.pavan@gmail.com',
	keywords = 'universidades cursos emec e-mec api brasil',
	description = 'API Python para obter informacoes de instituicoes de ensino superior.',
	long_description = open('README.md').read(),
	packages=find_packages(),
	install_requires=install_requires,
)