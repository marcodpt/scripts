#!/usr/bin/env python
import json
import sys 
import os 
from datetime import datetime

x = {
    'dir': os.path.dirname(os.path.realpath(__file__))+'/config/',
    'source': 'filedump.json',
    'tmp': '/tmp/filedump/',
    'ext': '.tar.gz',
    'mode': sys.argv[1] if len(sys.argv) > 1 else "",
    'file': sys.argv[2] if len(sys.argv) > 2 else ""
}

def error(msg):
    print "Error: "+msg
    quit()

def loadConfig():
    path = x['dir']+x['source']
    
    with open(path) as filePtr:    
        obj = json.load(filePtr)

    return obj

print "***** filedump.py "+x['mode']+" ******"

if x['mode'] == "--dump":
    obj = loadConfig()

    os.system('rm -rf '+x['tmp']+obj['label'])
    os.system('mkdir -p '+x['tmp']+obj['label'])

    iso = str(datetime.now()).replace(" ", "T", 1)
    iso = iso[0:16].replace(':', '_')

    print iso

    for source in obj['sources']:
        if os.path.isfile(source):
            print "copying file "+source
            os.system('cp '+source+' '+x['tmp']+obj['label'])
        elif os.path.isdir(source):
            print "copying dir "+source
            os.system('cp -r '+source+' '+x['tmp']+obj['label'])
        else:
            print "unable to find "+source

    print "***** Compressing *****"
    os.chdir(x['tmp'])
    os.system('tar -zcf '+obj['label']+iso+x['ext']+' '+obj['label'])
    os.system('rm -rf '+obj['label'])

    print "****** Moving File ******"
    os.system('mv '+obj['label']+iso+x['ext']+' '+obj['target'])
    if obj['limit']:
        files = os.popen("ls "+obj['target']+'/'+obj['label']+'*').read().split("\n")
        files.pop()
        i = 0
        while i < len(files) - obj['limit']:
            os.system('rm '+files[i])
            i = i + 1

    print "Finish all routines!"

elif x['mode'] == "--restore":
    obj = loadConfig()
    
    files = os.popen("ls "+obj['target']+'/'+obj['label']+'*'+x['ext']).read().split("\n")
    files.pop()

    if not len(files):
         error("no files to restore!")
    
    i = 1
    for file in files:
        print str(i)+': restore '+file
        i = i + 1
    print "which file should restore: "
    option = raw_input()
    
    i = int(option)
    if not i or i < 1 or i > len(files):
        error("unknown choice!")

    file = files[i - 1]
    print "****** Extracting ******"
    os.system('rm -rf '+x['tmp'])
    os.system('mkdir -p '+x['tmp'])
    os.system('cp '+file+' '+x['tmp'])
    os.chdir(x['tmp'])
    os.system('tar -zxf '+file)
    os.system('rm -f '+os.path.basename(file))
    os.chdir(x['tmp']+obj['label'])

    for source in obj['sources']:
       name = os.path.basename(source)
       if os.path.isfile(name):
           print "Moving file <"+name+">"
           os.system("mv "+name+" "+source)
       elif os.path.isdir(name):
           print "Moving dir <"+name+">"
           os.system("rm -rf "+source)
           os.system("mv "+name+" "+source)
       else:
           print "Fail to find <"+name+"> inside backup"

    os.system('rm -rf '+x['tmp'])

    print "Finish all routines!"

elif x['mode'] == "--config":
    obj = {
        "limit": "integer: max number of backup files, 0 if unlimited",
        "target": "string: path/to/store/backup",
        "label": "string: backup label",
        "sources": [
            "string: /path/of/a/file/or/a/dir/to/backup",
            "string: /path/of/another/file/or/dir/to/backup"
        ]
    }

    file = x['dir']+x['source']
    if os.path.isfile(file):
        error("File <"+file+"> already exists!")

    os.system("mkdir -p "+x['dir'])
    with open(file, 'w') as filePtr:    
        print >> filePtr, json.dumps(obj, indent = 4)
        print "Please change for your needs the file <"+file+">!"

else:
    print "Script for dump files!"
    print "--dump: dump files"
    print "--restore: restore files"
    print "--config: configure script"
