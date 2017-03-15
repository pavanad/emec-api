# -*- conding: utf-8 -*-

import json
import base64
import requests
from bs4 import BeautifulSoup
from utils import normalize_key
from unicodedata import normalize

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
			return

		self._parse_institution_details()
		self._parse_campus()

	def _parse_institution_details(self):    
    	
		url = 'http://emec.mec.gov.br/emec/consulta-ies/index/d96957f455f6405d14c6542552b0f6eb/' + base64.b64encode(str(self.code_ies))

		try:
			response = requests.get(url)
		except Exception as e:
			return str(e)

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

	def _parse_campus(self):
    
		campus = []
		url = 'http://emec.mec.gov.br/emec/consulta-ies/listar-endereco/d96957f455f6405d14c6542552b0f6eb/' + base64.b64encode(str(self.code_ies)) + '/list/1000'
    
		response = requests.get(url)
		soup = BeautifulSoup(response.content, 'html.parser')
    
		table = soup.find(id='listar-ies-cadastro')
		rows = table.tbody.find_all('tr')
    
		for r in rows:
			cells = r.find_all('td')
			item = {
				'code': cells[0].get_text(strip=True),
				'city': cells[4].get_text(strip=True),
				'uf': cells[5].get_text(strip=True) ,
				'courses': self._parse_courses(int(cells[0].get_text(strip=True)))
			}
			campus.append(item)
    
		self.data_ies['campus'] = campus

		return campus

	def _parse_courses(self, code_campus):

		url = 'http://emec.mec.gov.br/emec/consulta-ies/listar-curso-endereco/d96957f455f6405d14c6542552b0f6eb/' + base64.b64encode(str(self.code_ies)) + '/aa547dc9e0377b562e2354d29f06085f/' + base64.b64encode(str(code_campus)) + '/list/1000'

		try:
			response = requests.get(url)
		except Exception as e:
			return str(e)

		soup = BeautifulSoup(response.content, 'html.parser')
    
		table = soup.find(id='listar-ies-cadastro')
		rows = table.find_all('tbody')

		data = []
		for r in rows:                
			course = r.tr.td.get_text(strip=True)
			data.append(normalize('NFKD',course).encode('utf-8').capitalize())
    
		return data

	def get_full_data(self):

		if len(self.data_ies):
			return self.data_ies

		return None

	def write_json(self, filename):

		if len(self.data_ies):
			with open(filename, 'w') as outfile:
				json.dump(self.data_ies, outfile)


				

		