#!/usr/bin/env python

import lib
import os

x = {
    'source': 'ssh.json',
    'host': lib.getArg(1),
    'cache': []
}

def arp(mac):
    lib.which(['arp', 'grep', 'cut'])
    return os.popen("arp -n | grep "+mac+" | cut -d ' ' -f 1").read().split("\n")[0]

def ip(host):
    if host['ip'].find("-") == -1:
        return host['ip']
    
    ipAddress = arp(host['mac'])

    if not ipAddress:
        try:
            x['cache'].index(host['ip'])
        except ValueError:
            lib.which(['nmap'])
            x['cache'].append(host['ip'])
            print "***** mapping "+host['ip']+" *****"
            os.popen("nmap -sP --send-ip "+host['ip'])
            ipAddress =  arp(host['mac'])

    return ipAddress

lib.printInfo()

if x['host'] == "--list":
    hosts = lib.loadConfig(x['source'])

    for host in hosts:
        ipAddress = ip(host)
        if ipAddress == "":
            ipAddress = 'down'
        print host['label']+": "+ipAddress

elif x['host'] == "--config":
    hosts = [
        {
            "label": "string: host label",
            "user": "string: username",
            "port": "string: port number usually 22",
            "mac": "string: mac address format xx:xx:xx:xx:xx:xx",
            "ip": "string: ip address format xxx.xxx.xxx.xxx for dynamic ip use range like xxx.xxx.xxx.xxx-xxx"
        }
    ]
    lib.storeConfig(x['source'], hosts)

elif x['host']:
    hosts = lib.loadConfig(x['source'])

    host = False
    for h in hosts:
        if h['label'] == x['host']:
            host = h
            break

    if not host:
        lib.error("Unknown host <"+x['host']+">")

    ipAddress = ip(host)
    if not ipAddress:
        lib.error("<"+x['host']+"> is down")

    flags = ''
    if host['ip'].find("-") != -1:
        flags = ' -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null'

    os.system("ssh "+host['user']+"@"+ipAddress+" -p "+host['port']+flags)

else:
    print "Script for ssh connection"
    print ""
    print "Install on your machine"
    print "# apt-get install nmap"
    print "Install on target machine"
    print "# apt-get install openssh-server"
    print ""
    print "Usage"
    print "$ ./ssh.py --config: generate <"+x['source']+">"
    print "$ ./ssh.py --list: list availble hosts"
    print "$ ./ssh.py <host>: ssh connect to host"
