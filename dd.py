#!/usr/bin/env python
import sys
import time
import signal
from subprocess import Popen, PIPE
import subprocess


def run_dd(cmd):
    dd = Popen(cmd.split(' '), stderr=PIPE)
    output = ""
    while dd.poll() is None:
        time.sleep(.3)
        dd.send_signal(signal.SIGUSR1)
        while 1:
            l = str(dd.stderr.readline())
            # print(l)
            output = output + "\n" + l.strip()
            # print(output)
            # if 'records in' in l:
            #print(l[:l.index('+')], 'records')
            if 'bytes' in l:
                # print(l.strip())
                # print('\r')
                break
    return output


def run_dd_2(cmd):
    #dd = Popen(cmd.split(' '), stderr=PIPE)
    p = subprocess.Popen(cmd.split(' '), stdout=subprocess.PIPE, stderr=subprocess.PIPE,text=True)
    out, err = p.communicate()      
    return err


cmd = "dd if=/dev/urandom bs=1m count=5 of=/tmp/n18e1xuz"
out = run_dd_2(cmd)
print("-----")
print(out)
print("-----")



