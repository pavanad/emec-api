# -*- conding: utf-8 -*-

import sys
import json
import base64
from unicodedata import normalize

from bs4 import BeautifulSoup
import requests

from utils import normalize_key


class Institution(object):

	def __init__(self, code_ies=None):
		
		self.data_ies = {}		
		self.code_ies = code_ies

	def set_code_ies(self, code_ies):

		self.data_ies = {}		
		self.code_ies = code_ies

	def parse(self):

		if self.code_ies == None or self.code_ies == 0:
			print 'informe o codigo da ies'
			return False

		self.__parse_institution_details()
		self.__parse_campus()
		self.__parse_courses()

	def __parse_institution_details(self):    
			
		url = 'http://emec.mec.gov.br/emec/consulta-ies/index/d96957f455f6405d14c6542552b0f6eb/' + base64.b64encode(str(self.code_ies))

		try:
			response = requests.get(url)
		except Exception as e:
			print str(e)
			return False

		soup = BeautifulSoup(response.content, 'html.parser')

		fields_ies = soup.find_all('tr', 'avalLinhaCampos')
		for fields in fields_ies:
			key = ''
			value = ''
			for f in fields.find_all('td'):    
				aux = f.get_text(strip=True)
				if len(aux):
					if 'avalTituloCamposLeft' in f['class']:
						key = normalize_key(aux)
					else:
						value = aux
						self.data_ies[key] = value

		# pega as notas de conceito da ies do MEC

		table = soup.find(id='listar-ies-cadastro')		
		if table.tbody:		
				
			index = table.tbody.find_all('td')
			
			if len(index) == 9:
				item = {
					'ci': index[1].get_text(strip=True),
					'year_ci': index[2].get_text(strip=True),
					'igc': index[4].get_text(strip=True),
					'year_igc': index[5].get_text(strip=True),
					'igcc': index[7].get_text(strip=True),
					'year_igcc': index[8].get_text(strip=True)
				}
				self.data_ies['conceito'] = item

		return self.data_ies

	def __parse_campus(self):

		campus = []
		url = 'http://emec.mec.gov.br/emec/consulta-ies/listar-endereco/d96957f455f6405d14c6542552b0f6eb/' + base64.b64encode(str(self.code_ies)) + '/list/1000'

		response = requests.get(url)
		soup = BeautifulSoup(response.content, 'html.parser')
		table = soup.find(id='listar-ies-cadastro')
		
		if table.tbody:			
			rows = table.tbody.find_all('tr')	
			for r in rows:
				cells = r.find_all('td')
				if len(cells) > 1:
					item = {
						'code': cells[0].get_text(strip=True),
						'city': cells[4].get_text(strip=True),
						'uf': cells[5].get_text(strip=True) ,
					}
					campus.append(item)
	
			self.data_ies['campus'] = campus
			
			return campus

	def __parse_courses(self):

		#url = 'http://emec.mec.gov.br/emec/consulta-ies/listar-curso-endereco/d96957f455f6405d14c6542552b0f6eb/' + base64.b64encode(str(self.code_ies)) + '/aa547dc9e0377b562e2354d29f06085f/' + base64.b64encode(str(code_campus)) + '/list/1000'
		url = 'http://emec.mec.gov.br/emec/consulta-ies/listar-curso-agrupado/d96957f455f6405d14c6542552b0f6eb/' + base64.b64encode(str(self.code_ies)) + '/list/1000?no_curso='
		
		try:	
			response = requests.get(url)
		except Exception as e:
			print str(e)
			return False
		
		soup = BeautifulSoup(response.content, 'html.parser')
		table = soup.find(id='listar-ies-cadastro')
		
		if table.tbody:
					
			courses = []
			rows = table.tbody.find_all('tr')
			
			for r in rows: 
				if r.td.a:
					url_list = r.td.a['href'].split('/')
					code_course = url_list[len(url_list)-1]
					
					course_details = self.__parse_course_details(code_course)
					courses += course_details
					
					sys.stdout.write('.')
					sys.stdout.flush()
					
			
			self.data_ies['courses'] = courses
			
			return courses

	def __parse_course_details(self, code_course):
		
		url = 'http://emec.mec.gov.br/emec/consulta-curso/listar-curso-desagrupado/9f1aa921d96ca1df24a34474cc171f61/'+ code_course + '/d96957f455f6405d14c6542552b0f6eb/' + base64.b64encode(str(self.code_ies))

		try:
			response = requests.get(url)
		except Exception as e:
			print str(e)
			return False
		
		soup = BeautifulSoup(response.content, 'html.parser')
		table = soup.find(id='listar-ies-cadastro')
		
		if table.tbody:
			courses_details = []
			rows = table.tbody.find_all('tr')
			
			for r in rows:
				cells = r.find_all('td')
				
				if len(cells) >= 9:
					item = {
						'codigo': cells[0].get_text(strip=True),
						'modalidade': cells[1].get_text(strip=True),
						'grau': cells[2].get_text(strip=True),
						'curso': normalize('NFKD', cells[3].get_text(strip=True)).encode('utf-8').capitalize(),
						'uf': cells[4].get_text(strip=True),
						'municipio': cells[5].get_text(strip=True),
						'enade': cells[6].get_text(strip=True),
						'cpc': cells[7].get_text(strip=True),
						'cc': cells[8].get_text(strip=True),
					}
					courses_details.append(item)
					
			return courses_details

	def get_full_data(self):

		if len(self.data_ies):
			return self.data_ies

		return None

	def write_json(self, filename):

		if len(self.data_ies):
			with open(filename, 'w') as outfile:
				json.dump(self.data_ies, outfile)


				

		
		
		