# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
	name = 'emec-api',
	version = '0.1.3',
	url = 'https://github.com/pavanad/emec-api',
	license = 'MIT License',
	author = 'Adilson Pavan',
	author_email = 'adilson.pavan@gmail.com',
	keywords = 'universidades cursos emec e-mec api brasil',
	description = 'API Python para obter informacoes de instituicoes de ensino superior.',
	packages=find_packages(),
	install_requires=[
		'beautifulsoup4==4.5.3',
		'requests==2.13.0'
	]
)