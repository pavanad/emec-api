# -*- conding: utf-8 -*-

import asyncio
import base64
import json
from unicodedata import normalize

import aiohttp
from bs4 import BeautifulSoup

from .utils import normalize_key


class Institution:
    """
    Classe responsavel pela coleta de todos os daddos da instituicao no site do e-MEC.
    Realiza o scraping em busca de dados detalhados da IE e dos cursos de cada campus.
    """

    BASE_URL = "https://emec.mec.gov.br/emec"

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

    def parse(self):
        """Realiza o parse completo de todos os dados da ies."""
        if self.code_ies is None or self.code_ies == 0:
            print("informe o codigo da ies")
            return

        asyncio.run(self.__parse())

    async def __parse(self):
        async with aiohttp.ClientSession() as session:
            await asyncio.gather(
                self.__parse_campus(session),
                self.__parse_institution_details(session),
                self.__parse_courses(session),
            )

    async def __parse_institution_details(self, session) -> dict:
        """
        Realiza o parse de todos os dados da instituicao,
        mantenedora e as notas de conceito do MEC.

        Returns:
            dict: dados detalhados da instituicao.
        """
        url = self.__get_url_ies()
        async with session.get(url) as resp:
            response = await resp.text()

        soup = BeautifulSoup(response, "html.parser")

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
                self.data_ies["conceito"] = {
                    "ci": index[1].get_text(strip=True),
                    "year_ci": index[2].get_text(strip=True),
                    "igc": index[4].get_text(strip=True),
                    "year_igc": index[5].get_text(strip=True),
                    "igcc": index[7].get_text(strip=True),
                    "year_igcc": index[8].get_text(strip=True),
                }

        return self.data_ies

    async def __parse_campus(self, session):
        """
        Realiza o parse de todos os campus referente a ies.
        """

        campus = []
        url = self.__get_url_campus()
        async with session.get(url) as resp:
            response = await resp.text()

        soup = BeautifulSoup(response, "html.parser")
        table = soup.find(id="listar-ies-cadastro")

        if table is None or table.tbody is None:
            return

        rows = table.find_all("tr", "corDetalhe2")
        for r in rows:
            cells = r.find_all("td")
            if len(cells) > 1:
                campus.append(
                    {
                        "code": cells[0].get_text(strip=True),
                        "city": cells[4].get_text(strip=True),
                        "uf": cells[5].get_text(strip=True),
                    }
                )

        self.data_ies["campus"] = campus

    async def __parse_courses(self, session) -> list:
        """
        Realiza o parse de todos os dados dos cursos.

        Returns:
            list: lista com dados do cursos em json.
        """

        url = self.__get_url_courses()
        async with session.get(url) as resp:
            response = await resp.text()

        soup = BeautifulSoup(response, "html.parser")
        table = soup.find(id="listar-ies-cadastro")

        if table is None or table.tbody is None:
            return

        courses = []
        rows = table.tbody.find_all("tr")

        if rows is None:
            return

        tasks = []
        for r in rows:
            if r.td.a:
                url_list = r.td.a["href"].split("/")
                course_code = url_list[len(url_list) - 1]
                tasks.append(self.__parse_course_details(course_code, session))
        courses = await asyncio.gather(*tasks)

        self.data_ies["courses"] = courses
        return courses

    async def __parse_course_details(self, course_code: int, session) -> list:
        """
        Realia o parse dos dados detalhados de cada curso.

        Args:
            code_course (int):	Codigo do curso na base de dados do MEC.

        Returns:
            list: lista com dados detalhados de cada curso em json.
        """
        url = self.__get_url_course_details(course_code)
        async with session.get(url) as resp:
            response = await resp.text()

        soup = BeautifulSoup(response, "html.parser")
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
                courses_details.append(
                    {
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
                )
        return courses_details

    def __get_url_ies(self) -> str:
        return (
            f"{self.BASE_URL}/consulta-ies/index"
            f"/d96957f455f6405d14c6542552b0f6eb/{self.__get_code_ies_b64()}"
        )

    def __get_url_campus(self) -> str:
        return (
            f"{self.BASE_URL}/consulta-ies/listar-endereco/"
            f"d96957f455f6405d14c6542552b0f6eb/{self.__get_code_ies_b64()}/list/1000"
        )

    def __get_url_courses(self) -> str:
        return (
            f"{self.BASE_URL}/consulta-ies/listar-curso-agrupado/"
            f"d96957f455f6405d14c6542552b0f6eb/{self.__get_code_ies_b64()}/"
            f"list/1000?no_curso="
        )

    def __get_url_course_details(self, course_code: int) -> str:
        # decodifica o code_course(recebido pela pagina) que esta em iso
        course_code_iso = base64.b64decode(course_code).decode("iso-8859-1")

        # transforma a string retornada em bits like object para conversao
        course_code_utf8 = str(course_code_iso).encode("utf-8")
        course_code = base64.b64encode(course_code_utf8).decode("utf-8")

        return (
            f"{self.BASE_URL}/consulta-curso/listar-curso-desagrupado/"
            f"9f1aa921d96ca1df24a34474cc171f61/0/d96957f455f6405d14c6542552b0f6eb/"
            f"{self.__get_code_ies_b64()}/c1b85ea4d704f246bcced664fdaeddb6/"
            f"{course_code}/list/1000"
        )

    def __get_code_ies_b64(self) -> str:
        """Retorna o codigo da ies em base64.

        Returns:
            str: string do codigo da ies em base64.
        """
        ies_code = str(self.code_ies).encode("utf-8")
        return base64.b64encode(ies_code).decode("utf-8")

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
