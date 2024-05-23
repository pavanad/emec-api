from cleo import Application as BaseApplication

from .commands.about import AboutCommand
from .commands.scraper import ScraperCommand


try:
    from emec_api.__version__ import __version__
except ImportError:
    from __version__ import __version__


class Application(BaseApplication):
    def __init__(self):
        super(Application, self).__init__("emec", __version__)

        for command in self.get_default_commands():
            self.add(command)

    def get_default_commands(self) -> list:
        commands = [AboutCommand(), ScraperCommand()]
        return commands
