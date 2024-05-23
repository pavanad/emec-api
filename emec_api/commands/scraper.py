import os
import time
from pprint import pprint
from tqdm import tqdm

import pandas as pd
from cleo import Command

from emec_api.api.client import Institution


class ScraperCommand(Command):
    """
    This command is used to scraper institutions data from emec.

    scraper
        {category=inst : Data category to scraping (inst, campus or courses)}
        {--ies=? : Institution code to scraping}
        {--file=? : File exported from EMEC containing a list of institutions}
        {--output=? : File output name.}
        {--format=json : File output format only to ies (json or csv only in --ies)}
    """

    MAX_RETRIES = 10

    def handle(self):
        code_ies = self.option("ies")
        if code_ies:
            self.__scrape_insitution_data(code_ies)

        filename = self.option("file")
        if filename:
            self.__scrape_list_institutions(filename)

    def __scrape_insitution_data(self, code_ies: str):
        try:
            code_ies = int(code_ies)
            self.line(
                f"\n> <comment>Scraping data for institution  {code_ies}</comment>"
            )
            ies = Institution(code_ies)
            ies.parse()
        except ValueError:
            self.line(
                "\n> <error>The institution's code needs to be " "an integer.</error>\n"
            )
            return
        except Exception as error:
            self.line(f"> <error>{error}</error>\n")
            return

        self.line("> <info>Data collected successfully.</info>")

        output = self.option("output")
        if output:
            export = {"json": ies.to_json, "csv": ies.to_csv}
            export[self.option("format")](output)
            self.line(f"> <info>File {output} saved successfully</info>")

        show = self.confirm(
            "\nWould you like to print the result in JSON to the terminal?", False
        )
        self.line("")
        if show:
            pprint(ies.get_full_json())

    def __scrape_list_institutions(self, filename: str):
        if not os.path.exists(filename):
            self.line(f"> <error>File {filename} does not exist.</error>\n")
            return

        df = pd.read_csv(filename)
        df.drop_duplicates(subset=["Código da IES"], inplace=True)

        df_consolidate = pd.DataFrame()
        code_ies = df["Código da IES"].tolist()

        ies_failed = []
        self.line(f"\n> Parsing list of institutions")

        category = self.argument("category")

        for code in tqdm(code_ies):
            retries = 0
            success = False
            error_message = ""
            while retries < self.MAX_RETRIES and not success:
                try:
                    ies = Institution(code)
                    ies.parse()
                    category_method = {
                        "inst": ies.get_institution_dataframe,
                        "campus": ies.get_campus_dataframe,
                        "courses": ies.get_courses_dataframe,
                    }
                    df_scraping = category_method[category]()
                    df_consolidate = pd.concat(
                        [df_consolidate, df_scraping], ignore_index=True
                    )
                    success = True
                except Exception as error:
                    if retries == 0:
                        error_message = str(error)

                    retries += 1
                    time.sleep(2)

            if not success:
                ies_failed.append({"code": code, "error": error_message})

        self.line("\n> <info>Data collected successfully.</info>\n")

        if ies_failed:
            self.line("> <error>Failed to parse the following institutions:</error>\n")
            table = self.table()
            table.set_header_row(["Code", "Error"])
            errors = [[str(item["code"]), item["error"]] for item in ies_failed]
            table.set_rows(errors)
            table.render(self.io)

        output = (
            self.option("output")
            if self.option("output")
            else "scraped_institutions.csv"
        )
        df_consolidate.to_csv(output, index=False)
