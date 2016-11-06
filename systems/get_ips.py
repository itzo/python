#!/usr/bin/env python
# get all ip's and networks in environment
# ./get_ips.py hosts

# TODO: switch to paramiko and make multithreaded
# TODO: collect more information, check for duplicate IP's, wrong configurations, gateways, routing, etc..
# TODO: add usage, input validation

import subprocess
import sys

with open(sys.argv[1], 'r') as hostlist:
    for host in hostlist:
        host = host.strip()

        iface = subprocess.Popen("ssh -o ConnectTimeout=3 root@" + host +
                " 'ip -4 addr | grep inet | grep -v 127.0.0.1 | cut -d\" \" -f6'",
                stdout=subprocess.PIPE, shell=True).communicate()[0].split()

        for i in iface:
            print ("%-17s %s" % (i.split('/')[0].rsplit('.',1)[0]+'.0/'+i.split('/')[1], i))
