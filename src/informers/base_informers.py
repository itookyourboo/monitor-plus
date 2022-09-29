import abc
from typing import Optional, Any

from processes import Process, ProcessManager


class Informer(abc.ABC):
    TITLE = ''
    BASE_COMMAND = ''
    TIMEOUT = 10

    def __init__(self, pid: int) -> None:
        self.pid = pid
        self.command: str = self.BASE_COMMAND.replace('{pid}', str(self.pid))
        self.__process: Optional[Process] = None

    @abc.abstractmethod
    def get_info(self) -> Any:
        pass

    @abc.abstractmethod
    def print_info(self, info: Any) -> None:
        pass

    def run_process(self) -> Process:
        self.__process = ProcessManager.open_process(self.command, self.TIMEOUT)
        return self.__process

    def get_output(self) -> str:
        return ProcessManager.get_output(self.__process)

    def get_and_print_info(self) -> None:
        self.print_info(self.get_info())


class OutputInformer(Informer):
    def get_info(self) -> str:
        return self.get_output()

    def print_info(self, output: str) -> None:
        print(output)


class RepeatedInformer(Informer, abc.ABC):
    INTERVAL = 1
    TIMES = 60
    SEPARATOR = "======"

    SUBCOMMAND = ''

    def __new__(cls, *args, **kwargs):
        cls.TIMEOUT = cls.INTERVAL * cls.TIMES + 2
        cls.BASE_COMMAND = (
            f'for i in {{1..{cls.TIMES}}}; '
            f'do {cls.SUBCOMMAND}; '
            f'sleep {cls.INTERVAL}; '
            f'echo "{cls.SEPARATOR}"; '
            f'done'
        )
        return super().__new__(cls)

    def _split_data(self, output) -> list[str]:
        return output.split(self.SEPARATOR)[:self.TIMES]

    def _get_x(self) -> list[float]:
        return [self.INTERVAL * i for i in range(self.TIMES)]
