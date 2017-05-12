# -*- conding: utf-8 -*-

import json
import base64
from unicodedata import normalize

from bs4 import BeautifulSoup
import requests

from utils import normalize_key


class Institution(object):
	"""
	Classe responsavel pela coleta de todos os daddos da instituicao no site do e-MEC.
	
	Realiza o scraping em busca de dados detalhados da instituicao e dos cursos de cada campus.
	"""

	def __init__(self, code_ies=None):
		"""
		Construtor da classe.
		
		Args:
			code_ies (int):		Codigo da instituicao de ensino na base de dados do MEC
		"""
		
		self.data_ies = {}		
		self.code_ies = code_ies

	def set_code_ies(self, code_ies):
		"""
		Informa o codigo da ies
		
		Args:
			code_ies (int):		Codigo da instituicao de ensino na base de dados do MEC
		"""
		
		self.data_ies = {}		
		self.code_ies = code_ies

	def parse(self):
		"""
		Realiza o parse completo de todos os dados da ies. 
		"""
		
		if self.code_ies == None or self.code_ies == 0:
			print 'informe o codigo da ies'
			return False

		self.__parse_institution_details()
		self.__parse_campus()
		self.__parse_courses()

	def __parse_institution_details(self):    
		"""
		Realiza o parse de todos os dados da instituicao, mantenedora e as notas de conceito do MEC.
		"""
		
		URL = 'http://emec.mec.gov.br/emec/consulta-ies/index/d96957f455f6405d14c6542552b0f6eb/' + base64.b64encode(str(self.code_ies))

		try:
			response = requests.get(URL)
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
						
		# insere o codigo da ies
		self.data_ies['code_ies'] = self.code_ies
		
		# pega as notas de conceito do MEC
		table = soup.find(id='listar-ies-cadastro')		
		
		if table is not None and table.tbody is not None:	
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
		"""
		Realiza o parse de todos os campus referente a ies. 
		"""

		campus = []
		URL = 'http://emec.mec.gov.br/emec/consulta-ies/listar-endereco/d96957f455f6405d14c6542552b0f6eb/' + base64.b64encode(str(self.code_ies)) + '/list/1000'

		response = requests.get(URL)
		soup = BeautifulSoup(response.content, 'html.parser')
		table = soup.find(id='listar-ies-cadastro')
		
		if table is None or table.tbody is None:
			return
					
		rows = table.tbody.find_all('tr')
		if rows:
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
		
	def __parse_courses(self):
		"""
		Realiza o parse de todos os dados dos cursos.
		"""
		
		URL = 'http://emec.mec.gov.br/emec/consulta-ies/listar-curso-agrupado/d96957f455f6405d14c6542552b0f6eb/' + base64.b64encode(str(self.code_ies)) + '/list/1000?no_curso='
		
		try:	
			response = requests.get(URL)
		except Exception as e:
			print str(e)
			return False
		
		soup = BeautifulSoup(response.content, 'html.parser')
		table = soup.find(id='listar-ies-cadastro')
		
		if table is None or table.tbody is None:
			return
		
		courses = []
		rows = table.tbody.find_all('tr')
		
		if rows is None:
			return
		
		for r in rows: 
			if r.td.a:
				url_list = r.td.a['href'].split('/')
				code_course = url_list[len(url_list)-1]
				
				course_details = self.__parse_course_details(code_course)					
				if course_details:
					courses += course_details
				
		
		self.data_ies['courses'] = courses
		
		return courses

	def __parse_course_details(self, code_course):
		"""
		Realia o parse dos dados detalhados de cada curso.
		
		Args:
			code_course (int):		Codigo do curso na base de dados do MEC.
		"""
		
		URL = 'http://emec.mec.gov.br/emec/consulta-curso/listar-curso-desagrupado/9f1aa921d96ca1df24a34474cc171f61/'+ code_course + '/d96957f455f6405d14c6542552b0f6eb/' + base64.b64encode(str(self.code_ies))

		try:
			response = requests.get(URL)
		except Exception as e:
			print str(e)
			return False
		
		soup = BeautifulSoup(response.content, 'html.parser')
		table = soup.find(id='listar-ies-cadastro')
		
		if table is None or table.tbody is None:
			return 
		
		courses_details = []
		rows = table.tbody.find_all('tr')
		
		if rows is None:
			return
		
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
		"""
		Retorna os dados completos da instituicao.
		
		Returns:
			Objeto Json com todos os dados da instituicao.
		"""
		
		if len(self.data_ies):
			return self.data_ies

		return None

	def write_json(self, filename):
		"""
		Escreve o arquivo json no disco.
		
		Args:
			filename (string):		Nome com o caminho completo do arquivo.
		"""

		if len(self.data_ies):
			with open(filename, 'w') as outfile:
				json.dump(self.data_ies, outfile, indent=4)


				

		
		
		