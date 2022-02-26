# -*- conding: utf-8 -*-

import base64
import json
from unicodedata import normalize

import requests
from bs4 import BeautifulSoup

from .utils import normalize_key


class Institution:
    """
    Classe responsavel pela coleta de todos os daddos da instituicao no site do e-MEC.
    Realiza o scraping em busca de dados detalhados da instituicao e dos cursos de cada campus.
    """

    def __init__(self, code_ies: int):
        """Construtor da classe.

        Args:
            code_ies (int): Codigo da instituicao de ensino na base de dados do MEC.
        """
        self.data_ies = {}
        self.code_ies = code_ies

    def set_code_ies(self, code_ies: int):
        """Informa o codigo da ies.

        Args:
            code_ies (int): Codigo da instituicao de ensino na base de dados do MEC
        """
        self.data_ies = {}
        self.code_ies = code_ies

    def parse(self) -> None:
        """Realiza o parse completo de todos os dados da ies."""
        if self.code_ies == None or self.code_ies == 0:
            print("informe o codigo da ies")
            return

        self.__parse_institution_details()
        self.__parse_campus()
        self.__parse_courses()

    def __parse_institution_details(self) -> dict:
        """
        Realiza o parse de todos os dados da instituicao,
        mantenedora e as notas de conceito do MEC.

        Returns:
            dict: dados detalhados da instituicao.
        """
        ies_code = str(self.code_ies).encode("utf-8")
        ies_b64 = base64.b64encode(ies_code).decode("utf-8")
        URL = f"https://emec.mec.gov.br/emec/consulta-ies/index/d96957f455f6405d14c6542552b0f6eb/{ies_b64}"

        try:
            response = requests.get(URL)
        except Exception as error:
            print(f"{error}")
            return

        soup = BeautifulSoup(response.content, "html.parser")

        fields_ies = soup.find_all("tr", "avalLinhaCampos")
        for fields in fields_ies:
            key = ""
            for f in fields.find_all("td"):
                aux = f.get_text(strip=True)
                if not aux:
                    continue
                if "tituloCampos" in f["class"]:
                    key = normalize_key(aux).decode("UTF-8")
                    continue
                self.data_ies[key] = aux

        # insere o codigo da ies
        self.data_ies["code_ies"] = self.code_ies

        # pega as notas de conceito do MEC
        table = soup.find(id="listar-ies-cadastro")

        if table is not None and table.tbody is not None:
            index = table.tbody.find_all("td")
            if len(index) == 9:
                item = {
                    "ci": index[1].get_text(strip=True),
                    "year_ci": index[2].get_text(strip=True),
                    "igc": index[4].get_text(strip=True),
                    "year_igc": index[5].get_text(strip=True),
                    "igcc": index[7].get_text(strip=True),
                    "year_igcc": index[8].get_text(strip=True),
                }
                self.data_ies["conceito"] = item

        return self.data_ies

    def __parse_campus(self):
        """
        Realiza o parse de todos os campus referente a ies.
        """

        campus = []
        ies_code = str(self.code_ies).encode("utf-8")
        ies_b64 = base64.b64encode(ies_code).decode("utf-8")
        URL = (
            f"http://emec.mec.gov.br/emec/consulta-ies/listar-endereco/"
            f"d96957f455f6405d14c6542552b0f6eb/{ies_b64}/list/1000"
        )

        response = requests.get(URL)
        soup = BeautifulSoup(response.content, "html.parser")
        table = soup.find(id="listar-ies-cadastro")

        if table is None or table.tbody is None:
            return

        rows = table.find_all("tr", "corDetalhe2")
        for r in rows:
            cells = r.find_all("td")
            if len(cells) > 1:
                item = {
                    "code": cells[0].get_text(strip=True),
                    "city": cells[4].get_text(strip=True),
                    "uf": cells[5].get_text(strip=True),
                }
                campus.append(item)

        self.data_ies["campus"] = campus

    def __parse_courses(self) -> list:
        """
        Realiza o parse de todos os dados dos cursos.

        Returns:
            list: lista com dados do cursos em json.
        """

        ies_code = str(self.code_ies).encode("utf-8")
        ies_b64 = base64.b64encode(ies_code).decode("utf-8")
        URL = (
            f"http://emec.mec.gov.br/emec/consulta-ies/listar-curso-agrupado/"
            f"d96957f455f6405d14c6542552b0f6eb/{ies_b64}/list/1000?no_curso="
        )

        try:
            response = requests.get(URL)
        except Exception as error:
            print(f"{error}")
            return False

        soup = BeautifulSoup(response.content, "html.parser")
        table = soup.find(id="listar-ies-cadastro")

        if table is None or table.tbody is None:
            return

        courses = []
        rows = table.tbody.find_all("tr")

        if rows is None:
            return

        for r in rows:
            if r.td.a:
                url_list = r.td.a["href"].split("/")
                code_course = url_list[len(url_list) - 1]

                course_details = self.__parse_course_details(code_course)
                if course_details:
                    courses += course_details

        self.data_ies["courses"] = courses
        return courses

    def __parse_course_details(self, code_course: int) -> list:
        """
        Realia o parse dos dados detalhados de cada curso.

        Args:
            code_course (int):	Codigo do curso na base de dados do MEC.

        Returns:
            list: lista com dados detalhados de cada curso em json.
        """
        ies_code = str(self.code_ies).encode("utf-8")
        ies_b64 = base64.b64encode(ies_code).decode("utf-8")

        # decodifica o code_course(recebido pela pagina) que esta em iso
        decode_course = base64.b64decode(code_course).decode("iso-8859-1")

        # transforma a string retornada em bits like object para conversao
        course_obj = str(decode_course).encode("utf-8")
        course_code = base64.b64encode(course_obj).decode("utf-8")

        URL = (
            f"https://emec.mec.gov.br/emec/consulta-curso/listar-curso-desagrupado/"
            f"9f1aa921d96ca1df24a34474cc171f61/0/d96957f455f6405d14c6542552b0f6eb/"
            f"{ies_b64}/c1b85ea4d704f246bcced664fdaeddb6/{course_code}/list/1000"
        )

        try:
            response = requests.get(URL)
        except Exception as error:
            print(f"{error}")
            return False

        soup = BeautifulSoup(response.content, "html.parser")
        table = soup.find(id="listar-ies-cadastro")

        if table is None or table.tbody is None:
            return

        courses_details = []
        rows = table.tbody.find_all("tr")

        if rows is None:
            return

        for r in rows:
            cells = r.find_all("td")

            if len(cells) >= 9:
                # print(cells[3].get_text(strip=True).encode("utf-8").capitalize())
                item = {
                    "codigo": cells[0].get_text(strip=True),
                    "modalidade": cells[1].get_text(strip=True),
                    "grau": cells[2].get_text(strip=True),
                    "curso": normalize(
                        "NFKD", cells[3].get_text(strip=True)
                    ).capitalize(),
                    "uf": cells[4].get_text(strip=True),
                    "municipio": cells[5].get_text(strip=True),
                    "enade": cells[6].get_text(strip=True),
                    "cpc": cells[7].get_text(strip=True),
                    "cc": cells[8].get_text(strip=True),
                }
                courses_details.append(item)
        return courses_details

    def get_full_data(self) -> dict:
        """
        Retorna os dados completos da instituicao.

        Returns:
            dict: objeto Json com todos os dados da instituicao.
        """
        return self.data_ies

    def write_json(self, filename: str):
        """Escreve o arquivo json no disco.

        Args:
            filename (str): nome com o caminho completo do arquivo.
        """
        with open(filename, "a", encoding="utf-8") as outfile:
            json.dump(self.data_ies, outfile, indent=4, ensure_ascii=False)
