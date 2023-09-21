# -*- conding: utf-8 -*-

import asyncio
import base64
import json
import os
from unicodedata import normalize

import aiohttp
import pandas as pd
from bs4 import BeautifulSoup

from .utils import normalize_key


class Institution:
    """
    Class responsible for collecting all the institution's data on the e-MEC website.
    Performs scraping in search of detailed data from the IE and the courses of each
    campus.
    """

    BASE_URL = "https://emec.mec.gov.br/emec"

    def __init__(self, code_ies: int):
        """Class constructor.

        Args:
            code_ies (int): Code of the educational institution in the MEC database.
        """
        self.set_code_ies(code_ies=code_ies)

    def set_code_ies(self, code_ies: int):
        """Defines the code of the ies.

        Args:
            code_ies (int): Code of the educational institution in the MEC database.
        """
        self.data_ies = {}
        self.code_ies = code_ies

    def parse(self):
        """Perform a full parse of all IES data."""
        if self.code_ies is None or self.code_ies == 0:
            print("inform the code of the ies")
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
        Performs the parse of all data from the institution,
        maintainer and the MEC concept notes.

        Returns:
            dict: details of the institution.
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

        # insert the ies code
        self.data_ies["code_ies"] = self.code_ies

        # get the MEC concept notes
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
        Parses all campuses referring to ies.
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
        Parses all course data.

        Returns:
            list: list of course data in json.
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
        response_tasks = await asyncio.gather(*tasks)

        for item in response_tasks:
            courses.extend(item)

        self.data_ies["courses"] = courses
        return courses

    async def __parse_course_details(self, course_code: int, session) -> list:
        """
        It parses the detailed data of each course.

        Args:
            code_course (int):	Course code in the MEC database.

        Returns:
            list: list with detailed data of each course in json.
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
        # decodes the code_course (received by the page) that is in ISO
        course_code_iso = base64.b64decode(course_code).decode("iso-8859-1")

        # transforms the returned string into object-like bits for conversion
        course_code_utf8 = str(course_code_iso).encode("utf-8")
        course_code = base64.b64encode(course_code_utf8).decode("utf-8")

        return (
            f"{self.BASE_URL}/consulta-curso/listar-curso-desagrupado/"
            f"9f1aa921d96ca1df24a34474cc171f61/0/d96957f455f6405d14c6542552b0f6eb/"
            f"{self.__get_code_ies_b64()}/c1b85ea4d704f246bcced664fdaeddb6/"
            f"{course_code}/list/1000"
        )

    def __get_code_ies_b64(self) -> str:
        """Returns the ies code in base64.

        Returns:
            str: ies code string in base64.
        """
        ies_code = str(self.code_ies).encode("utf-8")
        return base64.b64encode(ies_code).decode("utf-8")

    def __get_col_dataframe(self, col: str) -> pd.DataFrame:
        """Returns the dataframe of a specific column.

        Args:
            col (str): name of the column.

        Returns:
            pd.DataFrame: Pandas dataframe with the column's data.
        """
        if col not in self.data_ies:
            return pd.DataFrame()
        df = pd.json_normalize(self.data_ies[col])
        df["code_ies"] = self.data_ies["code_ies"]
        df["nome_da_ies"] = self.data_ies["nome_da_ies"]
        df["mantenedora"] = self.data_ies["mantenedora"]
        return df

    def get_full_json(self) -> dict:
        """
        Returns the complete data of the institution.

        Returns:
            dict: Json object with all the institution's data.
        """
        return self.data_ies

    def get_institution_dataframe(self) -> pd.DataFrame:
        """
        Returns only institution data in a pandas dataframe.

        Returns:
            pd.DataFrame: Pandas dataframe with only the institution's data.
        """
        df_inst = pd.json_normalize(self.data_ies)
        df_inst = df_inst[df_inst.columns.difference(["campus", "courses"])]
        return df_inst

    def get_campus_dataframe(self) -> pd.DataFrame:
        """
        Returns only campus data in a pandas dataframe.

        Returns:
            pd.DataFrame: Pandas dataframe with only the campus's data.
        """
        return self.__get_col_dataframe("campus")

    def get_courses_dataframe(self) -> pd.DataFrame:
        """
        Returns only courses data in a pandas dataframe.

        Returns:
            pd.DataFrame: Pandas dataframe with only the courses's data.
        """
        return self.__get_col_dataframe("courses")

    def to_json(self, filename: str):
        """Writes the json file to disk.

        Args:
            filename (str): name with the full path of the file.
        """
        with open(filename, "w", encoding="utf-8") as outfile:
            json.dump(self.data_ies, outfile, indent=4, ensure_ascii=False)

    def to_csv(self, filename: str):
        """Writes the csv file to disk.

        Args:
            filename (str): name with the full path of the file.
        """
        columns = ["campus", "courses"]
        name, extension = os.path.splitext(filename)

        # save institution data
        df_inst = self.get_institution_dataframe()
        df_inst.to_csv(filename)

        # save campus and courses
        for col in columns:
            if col not in self.data_ies:
                continue
            df = self.__get_col_dataframe(col)
            df.to_csv(f"{name}_{col}{extension}")
