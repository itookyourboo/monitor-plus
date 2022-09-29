from typing import TypeAlias

from matplotlib import pyplot as plt

from informers import RepeatedInformer, OutputInformer, Informer
from io_helper import diff, save


class LsofFilesInformer(OutputInformer):
    TITLE = '(lsof) СПИСОК ФАЙЛОВ, С КОТОРЫМИ РАБОТАЕТ ПРОГРАММА'
    BASE_COMMAND = 'lsof -n -p {pid}'


EventType: TypeAlias = str
Path: TypeAlias = str
FatraceFile: TypeAlias = tuple[EventType, Path]
FatraceFileInfo: TypeAlias = dict[Path, set[EventType]]
FatraceFilesInformerContract: TypeAlias = tuple[str, FatraceFileInfo]


class FatraceFilesInformer(Informer):
    SECONDS = 10

    # https://manpages.ubuntu.com/manpages/bionic/man1/fatrace.1.html
    TITLE = '(fatrace) СПИСОК ФАЙЛОВ, С КОТОРЫМИ РАБОТАЕТ ПРОГРАММА'
    BASE_COMMAND = f"fatrace -s {SECONDS} | grep '({{pid}})'"

    def get_info(self) -> FatraceFilesInformerContract:
        def get_file(row: str) -> FatraceFile:
            _, event_type, path = row.split()
            return event_type, path

        output: str = self.get_output()
        files: list[FatraceFile] = list(map(get_file, output.splitlines()))
        path_to_event_types: dict[Path, set[EventType]] = {}
        for event_type, path in files:
            path_to_event_types.setdefault(path, set()).add(event_type)

        return output, path_to_event_types

    def print_info(self, info: FatraceFilesInformerContract) -> None:
        def format_header(col1_title: str, col2_title: str, offset: int):
            return f'{col1_title:^{offset}}\t{col2_title}'

        def format_row(path: Path, event_types: set[EventType], offset: int):
            joined_event_types: str = ', '.join(sorted(event_types))
            return f'{path:<{offset}}\t{joined_event_types}'

        output, path_to_event_types = info
        max_path_len: int = len(max(path_to_event_types, key=len))

        print(format_header('file', 'event_types', max_path_len))
        print(*[
            format_row(path, event_types, max_path_len)
            for path, event_types in path_to_event_types.items()
        ], sep='\n')


class MemoryMapInformer(OutputInformer):
    # https://linux.die.net/man/1/pmap
    TITLE = '(pmap) КАРТА ПАМЯТИ ПРОЦЕССА'
    BASE_COMMAND = 'pmap -d {pid}'


IOGraphInformerContact: TypeAlias = tuple[
    list[float], list[tuple[int, int]], list[tuple[int, int]]
]


class IOGraphInformer(RepeatedInformer):
    TITLE = '(proc/io) ГРАФИК НАГРУЗКИ НА ПОДСИСТЕМУ ВВОДА-ВЫВОДА'
    SUBCOMMAND = 'cat /proc/{pid}/io'

    OUTPUT = 'io.png'

    def get_info(self) -> IOGraphInformerContact:
        def get_value(row: str) -> int:
            return int(row.split(': ')[1])

        output: str = self.get_output()
        data: list[str] = self._split_data(output)
        char_load: list[tuple[int, int]] = []
        byte_load: list[tuple[int, int]] = []
        for check in data:
            check = list(filter(bool, check.splitlines()))
            rchar, wchar = check[:2]
            char_load.append((get_value(rchar), get_value(wchar)))
            rbytes, wbytes = check[4:6]
            byte_load.append((get_value(rbytes), get_value(wbytes)))
        return self._get_x(), char_load, byte_load

    def print_info(self, info: IOGraphInformerContact) -> None:
        x, char_load, byte_load = info

        fig, axs = plt.subplots(2)
        fig.suptitle(self.TITLE)
        fig.subplots_adjust(bottom=0.1, wspace=0.2, hspace=0.5)

        for i, (name, arr_load) in enumerate((
                ('char', char_load),
                ('byte', byte_load)
        )):
            rload, wload = map(lambda x: diff(x, self.INTERVAL),
                               tuple(zip(*arr_load)))
            axs[i].plot(x[1:-1], rload, label=f'read {name}')
            axs[i].plot(x[1:-1], wload, label=f'write {name}')

            axs[i].set_xlabel('Период времени, с')
            axs[i].set_ylabel(f'Нагрузка, {name}/с')
            axs[i].legend()

        save(self.OUTPUT)
