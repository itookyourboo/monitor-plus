import os

from matplotlib import pyplot as plt

from config import DATA_DIR, BASE_DIR


def mkdir_data():
    if not os.path.exists(DATA_DIR):
        os.mkdir(DATA_DIR)


def rm_trash():
    def is_trash(filename: str):
        return os.path.isfile(filename) and '.' not in filename

    filenames: list[str] = os.listdir(BASE_DIR)
    for filename in filter(is_trash, filenames):
        os.remove(os.path.join(BASE_DIR, filename))


def print_line():
    print('=' * 50)


def busy_loop():
    while True:
        pass


def save(output: str):
    path: str = os.path.join(DATA_DIR, output)
    plt.savefig(path)
    plt.clf()
    plt.cla()
    plt.close()
    print(path)


def diff(array: list[int], interval: float) -> list[float]:
    return [
        (array[i + 1] - array[i]) / interval
        for i in range(1, len(array) - 1)
    ]


