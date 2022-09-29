from typing import TypeAlias

from matplotlib import pyplot as plt

from informers import RepeatedInformer, OutputInformer
from io_helper import diff, save


class LsofConnectionsInformer(OutputInformer):
    # https://linux.die.net/man/8/lsof
    TITLE = '(lsof) СПИСОК СЕТЕВЫХ СОЕДИНЕНИЙ, С КОТОРЫМИ РАБОТАЕТ ПРОГРАММА'
    BASE_COMMAND = 'lsof -i -a -p {pid}'


class NetstatConnectionsInformer(OutputInformer):
    # https://linux.die.net/man/8/netstat
    TITLE = '(netstat) СПИСОК СЕТЕВЫХ СОЕДИНЕНИЙ, С КОТОРЫМИ РАБОТАЕТ ПРОГРАММА'
    BASE_COMMAND = 'netstat -nlp | grep {pid}'


class NetworkedDataInformer(OutputInformer):
    TIMEOUT = 30

    # https://man7.org/linux/man-pages/man1/strace.1.html
    # https://www.ibm.com/docs/en/zos/2.4.0?topic=sockets-using-sendto-recvfrom-calls
    TITLE = '(strace) СОДЕРЖИМОЕ ПЕРЕДАВАЕМЫХ ПО СЕТИ ДАННЫХ'
    BASE_COMMAND = 'strace -p {pid} -f -e trace=sendto,recvfrom -s 10000'

    """
    # Получаем порты
    $ sudo netstat -pan | grep {pid} | grep -Po '(?<=:)\d{4}'
    # Трафик
    $ sudo tcpdump -A -i any | grep -e {port1} -e {port2} -e {port3}
    """


NetworkGraphInformerContract: TypeAlias = tuple[
    list[float], list[int], list[int]
]


class NetworkGraphInformer(RepeatedInformer):
    TITLE = '(proc/net) ГРАФИК НАГРУЗКИ НА СЕТЕВУЮ ПОДСИСТЕМУ'
    SUBCOMMAND = "cat /proc/{pid}/net/dev | awk 'NR>2 {print $2,$10}'"

    OUTPUT = 'network.png'

    def get_info(self) -> NetworkGraphInformerContract:
        output: str = self.get_output()
        data: list[str] = self._split_data(output)
        recv_arr: list[int] = []
        send_arr: list[int] = []
        for check in data:
            lines: list[list[str]] = list(filter(bool, map(str.split, check.splitlines())))
            recv, send = zip(*lines)
            recv_sum: int = sum(map(int, recv))
            recv_arr.append(recv_sum)
            send_sum: int = sum(map(int, send))
            send_arr.append(send_sum)

        return self._get_x(), recv_arr, send_arr

    def print_info(self, info: NetworkGraphInformerContract) -> None:
        x, recv_load, send_load = info
        recv_load, send_load = map(lambda x: diff(x, self.INTERVAL),
                                   (recv_load, send_load))
        x = x[1:-1]

        plt.title(self.TITLE)
        plt.plot(x, recv_load, label=f'recv')
        plt.plot(x, send_load, label=f'send')

        plt.xlabel('Период времени, с')
        plt.ylabel(f'Нагрузка, байт/с')
        plt.legend()

        save(self.OUTPUT)
