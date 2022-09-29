from colorama import Fore, Style

from informers.base_informers import Informer
from io_helper import print_line


class Runner:
    def __init__(self, informers: list[Informer]):
        self.informers = informers

    def run(self):
        self.informers.sort(key=lambda x: x.TIMEOUT, reverse=True)
        for informer in self.informers:
            informer.run_process()

        for informer in self.informers:
            self.print_informer_result(informer)

    @staticmethod
    def print_informer_result(informer: Informer):
        print()
        print(f'{Fore.BLUE}{informer.TITLE}{Style.RESET_ALL}')
        print(f'{Fore.GREEN}{informer.command}{Style.RESET_ALL}')
        informer.get_and_print_info()
        print_line()
