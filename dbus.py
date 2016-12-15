#!/usr/bin/env python

import lib
import os

lib.printInfo()

os.system('touch $HOME/.Xdbus')
os.system('chmod 600 $HOME/.Xdbus')
os.system('env | grep DBUS_SESSION_BUS_ADDRESS > $HOME/.Xdbus')
os.system('echo "export DBUS_SESSION_BUS_ADDRESS" >> $HOME/.Xdbus')

print "dbus enviroment variables stored"
print "$ source ~/.Xdbus"
