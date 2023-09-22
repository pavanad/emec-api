from cleo import Command


class ScraperCommand(Command):
    name = "scraper"
    description = "Shows information about emec api"

    def handle(self):
        self.line("<info>teste</info>")
