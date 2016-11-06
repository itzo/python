#!/usr/bin/env python

import subprocess
import sys

d = {}

for host in sys.stdin:
    host = host.strip()
    iface = subprocess.Popen("ssh root@" +host+ " 'ip -4 addr | grep inet | grep -v 127.0.0.1 | cut -d\" \" -f6'", stdout=subprocess.PIPE, shell=True).communicate()[0].split()

    # logic to get only the lowest ip in each subnet
    for i in range(len(iface)-1):
        try:
            t = iface[i+1]
        except IndexError:
            continue
        a = iface[i].split('/')
        b = iface[i+1].split('/')
        temp_a = a[0].split('.')
        temp_b = b[0].split('.')
        # compare elements and delete the larger from the list
        if str(temp_a[0]+temp_a[1]+temp_a[2]) == str(temp_b[0]+temp_b[1]+temp_b[2]):
            if temp_a[3] < temp_b[3]:
                del iface[i+1]
            else:
                del iface[i]

    for i in iface:
        d[i] = i[:-3]

# print out our IP's
# sorry once again for ugliness below. noticed I wasn't printing the output correctly
# with about 10 minutes left...
for key in d:
    print ( key.split('/')[0].split('.')[0] + '.' +
            key.split('/')[0].split('.')[1] + '.' +
            key.split('/')[0].split('.')[2] + '.' +
            "0/" + key.split('/')[1] + " - " + d[key])
