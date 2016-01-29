#!/usr/bin/env python

import os
import tempfile
import random
import string
import sys
import signal, psutil
from subprocess import Popen,check_output


def get_who_use_it(path):
    try:
        pid_list = check_output('lsof +D -t %s' % path, shell=True)
        return [int(i) for i in pid_list]
    except Exception as e:
        print(e)
        return []

def random_string(size=5, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


class Session(object):
    def __init__(self, uri):
        base_temp_dir = tempfile.gettempdir()
        self.temp_dir = os.path.join(base_temp_dir, 'redit-%s' % random_string(5))
        self.uri = uri
        self.mounted = True

    def __enter__(self):
        os.mkdir(self.temp_dir)
        if os.system("sshfs '%s' '%s'" % (self.uri, self.temp_dir)) == 0:
            self.mounted = True
        return self.get_tempdir()

    def __exit__(self, type, value, traceback):
        os.system('sync')

        for i in get_who_use_it(self.temp_dir):
            os.kill(i)

        while self.mounted:
            self.mounted = os.system("fusermount -u '%s'" % self.temp_dir) != 0
        print('unmount successed')
        if self.temp_dir and not self.mounted:
            os.rmdir(self.temp_dir)

    def get_tempdir(self):
        return self.temp_dir

def main():
    path = sys.argv[1]
    with Session(path) as path:
        os.system('vim %s' % path)

if __name__ == '__main__':
    main()
