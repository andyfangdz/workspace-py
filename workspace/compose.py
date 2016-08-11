import subprocess
import os
import socket
import yaml
import tempfile
import random
import string

HOME_DIR = '/Users/andy/trap'


def random_word(length):
    return ''.join(random.choice(string.lowercase) for i in range(length))


def pick_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('localhost', 0))
    address, port = s.getsockname()
    s.close()
    return port


def call_compose(path, command, env=None):
    my_env = os.environ.copy()
    my_env.update(env)
    subprocess.Popen(['docker-compose', '-f', path] + command, env=my_env)


class Workspace:

    def __init__(self, name, username, compose_file_path, public_key=None):
        self.name = name
        self.username = username
        self.home_dir = os.path.join(HOME_DIR, username)
        try:
            os.mkdir(self.home_dir)
        except OSError:
            pass
        self.compose_path = os.path.abspath(compose_file_path)
        self.path = ""
        self.base_name = ""
        self.copy_compose_files()
        self.ssh_port = pick_port()
        self.web_port = pick_port()
        self.root_password = random_word(6)
        self.env = {
            "SSH_PORT": str(self.ssh_port),
            "WEB_PORT": str(self.web_port),
            "SSH_PASSWORD": self.root_password,
            "HOME_DIR": self.home_dir
        }
        self.public_key = public_key
        self.compose = yaml.load(open(compose_file_path).read())
        self.services = []
        self.load_services()

    def copy_compose_files(self):
        dir_name = os.path.dirname(self.compose_path)
        self.path = tempfile.mkdtemp(prefix=self.name)
        self.base_name = os.path.basename(self.path).lower()
        self.path = os.path.join(
            self.path,
            self.base_name
        )
        os.symlink(dir_name, self.path)
        self.path = os.path.join(self.path, os.path.basename(self.compose_path))

    def load_services(self):
        self.services = self.compose.keys()

    def get_container(self, service):
        return "{}_{}_1".format(self.base_name, service)

    def build(self):
        call_compose(self.path, ['build'], env=self.env)

    def up(self):
        call_compose(self.path, ['up'], env=self.env)

    def down(self):
        call_compose(self.path, ['down'], env=self.env)

