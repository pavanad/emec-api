from cleo import Command

from emec.api.client import Institution
from pprint import pprint


class ScraperCommand(Command):
    """
    This command is used to scraper institutions data from emec.

    scraper
        {--ies=? : Institution code to scraping}
        {--output=? : File output name.}
        {--format=json : File output format (json or csv)}
    """

    def handle(self):
        code_ies = self.option("ies")
        if code_ies:
            try:
                code_ies = int(code_ies)
            except ValueError:
                self.line(
                    "\n> <error>The institution's code needs to be "
                    "an integer.</error>\n"
                )
            else:
                self.__scrape_insitution_data(code_ies)

    def __scrape_insitution_data(self, code_ies: int):
        self.line(f"\n> <comment>Scraping data for institution  {code_ies}</comment>")

        try:
            ies = Institution(code_ies)
            ies.parse()
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
