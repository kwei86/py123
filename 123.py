#!/usr/bin/python
# -*- coding:utf-8 -*-

import sys
import os
import pexpect
import traceback
import getpass
import re
import struct
import fcntl
import termios
import signal
import resource

resource.setrlimit(resource.RLIMIT_NOFILE, (1024, 1024))


def ssh_command(user, host, password):
    ssh_newkey = 'Are you sure you want to continue connecting'
    # child = pexpect.spawn('ssh -q -o StrictHostKeyChecking=no -p 22 -l %s %s '%(user,host))
    child = pexpect.spawn(
        'ssh -i /home/wwlocal/wwlops/id_rsa -q -o StrictHostKeyChecking=no -p 22 -l %s %s ' % (user, host))
    # i = child.expect([pexpect.EOF,ssh_newkey,"password: ","Password: ","Welcome to","Version",pexpect.TIMEOUT],timeout=5)
    i = child.expect([pexpect.EOF, ssh_newkey, "password: ", "Password: ", "Welcome to", "Version", pexpect.TIMEOUT],
                     timeout=1)
    if (i == 0) or (i == 4) or (i == 7):
        print
        'SSH could not login. Here is what SSH said:'
        print
        child.before, child.after
        return False
    elif i == 1:
        child.sendline("yes")
    elif (i == 2) or (i == 3):
        child.sendline(password)
        # print child.before

    return child


def main():
    if len(sys.argv) == 1:
        print
        'You must specify one host!'
        return False

    host = sys.argv[1]

    user = "root"
    password = "no password"

    global child
    child = ssh_command(user, host, password)

    def sigwinch_passthrough(sig, data):
        s = struct.pack("HHHH", 0, 0, 0, 0)
        a = struct.unpack('hhhh', fcntl.ioctl(sys.stdout.fileno(), termios.TIOCGWINSZ, s))

        global child
        child.setwinsize(a[0], a[1])

    signal.signal(signal.SIGWINCH, sigwinch_passthrough)
    # child.setwinsize(41, 100)
    sigwinch_passthrough(None, None)
    child.interact()
    child.expect(pexpect.EOF)
    print
    child.before


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print
        "exit"
        sys.exit(0)
    except EOFError:
        print
        "exit"
        sys.exit(0)
    except OSError:
        print
        "exit"
        sys.exit(0)
    except Exception, e:
        print
        "ERROR: %s" % e