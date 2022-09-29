import subprocess


class Process(subprocess.Popen):
    def __init__(self, command: str, timeout: int):
        super().__init__(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True
        )
        self.timeout = timeout


class ProcessManager:
    @staticmethod
    def open_process(command: str, timeout: int) -> Process:
        process = Process(command, timeout)
        return process

    @staticmethod
    def get_output(process: Process) -> str:
        try:
            stdout, stderr = process.communicate(timeout=process.timeout)
        except subprocess.TimeoutExpired:
            process.kill()
            stdout, stderr = process.communicate()
        if not stdout.decode().strip():
            return stderr.decode()
        return stdout.decode()
