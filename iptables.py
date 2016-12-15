#!/usr/bin/env python

import lib
import os

x = {
    'source': 'config/iptables',
    'mode': lib.getArg(1)
}

lib.printInfo()
if os.environ['USER'] != 'root':
    lib.error("you must run this script as root")

if x['mode'] == "--lan":
    lib.which(['iptables-restore', 'iptables-save'])
    os.system('iptables-save > '+x['source'])
    if not os.popen('cat '+x['source']).read():
        lib.error("Fail to backup iptables")
    else:
        print "backup iptable rules <"+x['source']+">"

    os.system('iptables -P INPUT DROP')
    os.system('iptables -P FORWARD DROP')
    os.system('iptables -P OUTPUT DROP')
    os.system('iptables -A INPUT -s localhost -j ACCEPT')
    os.system('iptables -A OUTPUT -s localhost -j ACCEPT')
    os.system('iptables -A INPUT -s 192.168.0.0/24 -j ACCEPT')
    os.system('iptables -A OUTPUT -s 192.168.0.0/24 -j ACCEPT')
    os.system('iptables-save > /etc/iptables/rules.v4')

elif x['mode'] == "--restore":
    lib.which(['iptables-restore', 'iptables-save'])
    if not os.path.isfile(x['source']):
        lib.error("Unable to find iptables rules <"+x['source']+">")

    os.system('iptables-restore < '+x['source'])
    os.system('iptables-save > /etc/iptables/rules.v4')

else:
    print "Script for iptables rules"
    print ""
    print "Install"
    print "# apt-get install iptables-persistent";
    print ""
    print "Usage"
    print "# ./iptables.py --lan: enable only lan access"
    print "# ./iptables.py --restore: restore iptable rules"
