from cleo import Command
from pyfiglet import Figlet


class AboutCommand(Command):
    name = "about"
    description = "Shows information about emec api"

    def handle(self):
        custom_fig = Figlet(font="big")
        title = custom_fig.renderText("emec api")
        self.line(
            f"{title}\n<info>This tool was developed to facilitate"
            f" the use of the e-MEC API app.</info>\n"
        )
