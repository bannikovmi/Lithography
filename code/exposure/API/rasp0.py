# standard library imports
import os
from paramiko import AutoAddPolicy, SSHClient

# third-party imports
# PyQt-related imports
from PyQt5.QtCore import pyqtSignal, QObject, QRunnable, QThreadPool

# local imports
from backend.resources.resource import QResource

class RunnerSignals(QObject):

    finished = pyqtSignal()

class ExposureRunner(QRunnable):

    def __init__(self, rasp0, name, exposure_time):

        super().__init__()

        self.rasp0 = rasp0
        self.name = name
        self.exposure_time = exposure_time

        self.signals = RunnerSignals()

    def run(self):

        # Run expose_remote in current thread (separate_thread is False by default)
        self.rasp0.expose_remote(self.name, self.exposure_time) 
        self.signals.finished.emit()

class QRaspZero(QResource):

    exposure_finished = pyqtSignal()
    upload_finished = pyqtSignal()

    def connect(self, separate_thread=False):

        self.ssh = SSHClient()
        self.ssh.set_missing_host_key_policy(AutoAddPolicy())
        self.ssh.connect(**self.config)
        self.invoke_shell()
        self.start_loop()

    def disconnect(self):

        self.channel.close()
        self.ssh.close()

    def init_projector(self):

        self.send("python /media/init.py")

    def stop_projector(self):

        self.send("python /media/stop.py")

    def exec_command(self, command):

        stdin, stdout, stderr = self.ssh.exec_command(command)

        result = stdout.read().decode('utf-8')
        error = stderr.read().decode('utf-8')

        return result, error

    def expose_remote(self, name, exposure_time=2000, separate_thread=False):
        
        if separate_thread:
            exposure_runner = ExposureRunner(self, name, exposure_time)
            exposure_runner.signals.finished.connect(self.exposure_finished)
            self.thread_pool.start(exposure_runner)
        else:
            return self.exec_command(
                f"python /media/expose.py {name} {exposure_time}")

    def list_pics(self):

        files_string = self.exec_command("ls /media/pics")[0]
        return files_string.split()

    def get_file(self, remote_path, local_path):
        
        with self.ssh.open_sftp() as sftp:
            sftp.get(remote_path, local_path)

    def put_file(self, local_path, remote_path):

        with self.ssh.open_sftp() as sftp:
            sftp.put(local_path, remote_path)

    def upload_pic(self, local_path):

        remote_path = os.path.join("/media", "pics", os.path.basename(local_path))
        self.put_file(local_path, remote_path)

    #####################################################################################
    ### Shell-related commands
    #####################################################################################
    def invoke_shell(self):
        
        self.channel = self.ssh.invoke_shell()

    def query(self, msg):
        
        self.send(msg)
        return self.recv(1024)

    def send(self, msg):

        self.channel.send(f"{msg}\n")

    def recv(self):

        # wait for channel receive and return message
        while not self.channel.recv_ready():
            time.sleep(0.1)
        
        return self.channel.recv(1024).decode('utf-8')

    def start_loop(self):

        self.send(f"python /media/loop.py")

    def end_loop(self):

        self.send("STP")

    def set_pixels(self, x1, y1, x2, y2, i):

        self.send(f"PIX {x1} {y1} {x2} {y2} {i}")

    def start_exposure(self, name, t_delay):

        self.send(f"PIC {name} {t_delay}")
