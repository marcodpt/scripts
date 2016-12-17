#!/usr/bin/env python

from random import randint
import lib

x = {
    'len': lib.getArg(1),
    'type': lib.getArg(2)
}

upper = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
lower = 'abcdefghijklmnopqrstuvwxyz'
number = '0123456789'
special = '_!@#$%&*+-/='

def randomChar(source):
    r = randint(0, len(source))
    return source[r:r+1]

lib.printInfo()

if x['len']:
    x['type'] = x['type'] if x['type'] else 'nlu'

    source = ''
    if x['type'].find('n') != -1:
        source = source + number
    if x['type'].find('l') != -1:
        source = source + lower
    if x['type'].find('u') != -1:
        source = source + upper
    if x['type'].find('s') != -1:
        source = source + special

    if not len(source):
        lib.error("Unable to understand charset")

    password = ''
    for i in range(int(x['len'])):
        password += randomChar(source) 

    print password

else:
    print "Script for random password generatore"
    print ""
    print "Usage"
    print "$ ./pass.py <len> <mode>: generate password with len characters in mode"
    print ""
    print "Mode"
    print "u: Uppercase characters"
    print "l: Lowercase characters"
    print "n: Numbers"
    print "s: Special characters"
    print ""
    print "Example"
    print "$ ./pass.py 12 usn: generate 12 length password with uppercase, special, numbers"
    print "$ ./pass.py 8: generate 8 length password with uppercase, lowercase, numbers"
