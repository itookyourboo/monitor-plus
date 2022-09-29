import subprocess
import sys

from config import KEEP_RUNNING
from io_helper import rm_trash, mkdir_data, busy_loop
from runner import Runner

from informers import *


def main(args: list[str]) -> None:
    mkdir_data()
    process = subprocess.Popen(args)
    pid: int = process.pid

    try:
        print(f'PID запущенного процесса: {pid}')

        informers: list[Informer] = [
            ThreadsInformer(pid),
            LsofFilesInformer(pid),
            FatraceFilesInformer(pid),
            LsofConnectionsInformer(pid),
            NetstatConnectionsInformer(pid),
            MemoryMapInformer(pid),
            NetworkedDataInformer(pid),
            CPUFlameGraphInformer(pid),
            CPUGraphInformer(pid),
            IOGraphInformer(pid),
            NetworkGraphInformer(pid),
            ThreadStateInformer(pid)
        ]

        runner = Runner(informers)
        runner.run()

        print('Done')
        if KEEP_RUNNING:
            print('Keep running program')
            busy_loop()
    except KeyboardInterrupt:
        pass
    finally:
        process.kill()
        print(f'\nProcess {pid} killed')
        rm_trash()


if __name__ == '__main__':
    main(sys.argv[1:])
