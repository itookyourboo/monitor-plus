import os
from typing import TypeAlias

from matplotlib import pyplot as plt

from config import DATA_DIR, BASE_DIR
from informers import OutputInformer, RepeatedInformer, Informer
from io_helper import save


ThreadsInformerContract: TypeAlias = tuple[list[int], str]


class ThreadsInformer(Informer):
    # https://man7.org/linux/man-pages/man1/ps.1.html
    TITLE = '(ps) КОЛИЧЕСТВО ПОТОКОВ, СОЗДАВАЕМОЕ ПРОГРАММОЙ'
    BASE_COMMAND = 'ps -p {pid} -T -o pid,tid,psr,pcpu'

    def get_info(self) -> ThreadsInformerContract:
        def get_tid(row: str) -> int:
            return int(row.split()[1])

        output: str = self.get_output()
        tids: list[int] = list(map(get_tid, output.splitlines()[1:]))
        return tids, output

    def print_info(self, info: ThreadsInformerContract) -> None:
        tids, output = info
        print(f'Количество потоков: {len(tids)}')
        print('ID потоков:', *tids)
        print(output)


class CPUFlameGraphInformer(OutputInformer):
    SECONDS = 30
    TIMEOUT = SECONDS + 5

    PERF_DATA = f'{DATA_DIR}/perf.data'
    PERF_SVG = f'{DATA_DIR}/perf.svg'

    TITLE = '(perf) ГРАФИК ПОТРЕБЛЕНИЯ ПРОГРАММОЙ CPU'
    BASE_COMMAND = (
        f'perf record -o {PERF_DATA} -p {{pid}} -F 99 -a -g -- sleep {SECONDS}; '
        f'perf script -i {PERF_DATA} | '
        f'{BASE_DIR}/FlameGraph/stackcollapse-perf.pl | '
        f'{BASE_DIR}/FlameGraph/flamegraph.pl > {PERF_SVG}'
    )

    def print_info(self, output: str) -> None:
        super().print_info(output)
        print(self.PERF_DATA)
        print(self.PERF_SVG)


CPUGraphInformerContract: TypeAlias = tuple[
    list[float], list[list[tuple[str, float]]]
]


class CPUGraphInformer(RepeatedInformer):
    TITLE = '(ps) ГРАФИК ПОТРЕБЛЕНИЯ ПРОГРАММОЙ CPU'
    SUBCOMMAND = 'ps -mo %cpu,psr -p {pid} --no-header'

    OUTPUT = 'cpu.png'
    PRINT = False

    def get_info(self) -> CPUGraphInformerContract:
        output: str = self.get_output()
        data: list[str] = self._split_data(output)
        y: list[list[tuple[str, float]]] = []
        for check in data:
            psr: dict[str, float] = {
                str(i): 0.0 for i in range(os.cpu_count())
            }
            for line in check.splitlines():
                if not line.strip():
                    continue
                cpu, core = line.split()
                psr[core] = psr.get(core, 0) + float(cpu)
            items: list[tuple[str, float]] = list(map(tuple, psr.items()))
            items.sort()
            y.append(items)
        return self._get_x(), y

    def print_info(self, info: CPUGraphInformerContract) -> None:
        x, y = info
        cpus: list[tuple[tuple[str, float]]] = list(zip(*y))
        for cpu in cpus:
            legend: tuple[str]
            ys: tuple[float]
            legend, ys = zip(*cpu)
            plt.plot(x, ys, label=legend[0])
            if self.PRINT:
                print(
                    f'{legend[0]}: ',
                    *map(lambda i: f'{i:^4.0f}', ys)
                )
        plt.title(self.TITLE)
        plt.xlabel('Период времени, с')
        plt.ylabel('Нагрузка CPU, %')
        plt.legend()

        save(self.OUTPUT)


ThreadStateInformerContract: TypeAlias = tuple[
    list[float], list[int]
]


class ThreadStateInformer(RepeatedInformer):
    INTERVAL = 0.5
    TIMES = 120

    TITLE = '(ps) ГРАФИК СМЕНЫ СОСТОЯНИЯ ИСПОЛНЕНИЯ ПОТОКОВ'
    SUBCOMMAND = (
        'ps -p {pid} -T -o state | grep -c R'
    )

    OUTPUT = 'state.png'

    def get_info(self) -> ThreadStateInformerContract:
        output: str = self.get_output()
        data: list[str] = self._split_data(output)
        running_num: list[int] = list(map(lambda x: int(x.strip()), data))

        return self._get_x(), running_num

    def print_info(self, info: ThreadStateInformerContract) -> None:
        x, running_num = info

        plt.title(self.TITLE)
        plt.plot(x, running_num)
        plt.xlabel('Период времени, с')
        plt.ylabel('Кол-во R потоков')
        plt.yticks(range(max(running_num) + 1))

        save(self.OUTPUT)
