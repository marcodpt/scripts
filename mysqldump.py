#!/usr/bin/env python

import lib 
import json
import os 
import getpass
from datetime import datetime

x = {
    'source': 'mysqldump.json',
    'dump': '.dump/',
    'restore': '.restore',
    'tmp': '/tmp/mysqldump',
    'algorithm': 'aes-256-cbc',
    'mode': lib.getArg(1),
    'file': lib.getArg(2)
}

def load():
    dumps = lib.loadConfig(x['source'])

    for dump in dumps:
        path = x['dump']+dump['label']

        if not os.path.isfile(path):
            lib.error("Unable to locate file <"+path+">, please run:\n./mysqldump.py --config-dump")
    
        with open(path) as filePtr:    
            lines = filePtr.readlines()
        for line in lines:
            data = line.split("=")
            if len(data) == 2 and data[0] == "password":
                dump["password"] = data[1]
        
    return dumps

lib.printInfo()

if x['mode'] == "--dump":
    dumps = load()

    os.system('rm -rf '+x['tmp'])
    os.system('mkdir -p '+x['tmp'])

    iso = str(datetime.now()).replace(" ", "T", 1)
    iso = iso[0:16].replace(':', '_')

    print iso

    for dump in dumps:
        file = dump['label']+iso
        path = x['tmp']+"/"+file
        
        flags = '--defaults-extra-file='+x['dump']+dump['label']

        print "Host: "+dump['label']
        os.system('mkdir -p '+path)

        if dump['grants']:
            print "***** Dumping Grants *****"
            str = "mysql "+flags+" -BNe"
            str += " \"select concat('\\'',user,'\\'@\\'',host,'\\'') from mysql.user where user != 'root'\""
            str += " | while read uh;"
            str += " do mysql "+flags+" -BNe"
            str += " \"show grants for $uh\""
            str += " | sed 's/$/;/; s/\\\\\\\\/\\\\/g';"
            str += " done > "+path+"/grants.sql"

            os.system(str)
        
        flags += ' --force'
        flags += ' --opt'
        flags += ' --databases'

        for db in dump['databases']:
            print "***** Dumping "+db+" *****"
            os.system('mysqldump '+flags+' '+db+' > '+path+"/"+db+'.sql')

        print "***** Compressing *****"
        os.chdir(x['tmp'])
        os.system('tar -zcf '+file+'.tar.gz '+file)
        os.system('rm -rf '+file)
        file += '.tar.gz'

        if dump['encrypt']:
            print "***** Encrypting *****"
            os.system('openssl '+x['algorithm']+' -salt -in '+file+' -out '+file+'.enc -k '+dump['password'])
            os.system('rm -rf '+file)
            file += '.enc'
        

        print "****** Moving File ******"
        for folder in dump['folders']:
            os.system('mkdir -p '+folder['path'])
            os.system('cp '+x['tmp']+'/'+file+' '+folder['path'])
            if folder['limit']:
                files = os.popen("ls "+folder['path']+'/'+dump['label']+'*').read().split("\n")
                files.pop()
                i = 0
                while i < len(files) - folder['limit']:
                    os.system('rm '+files[i])
                    i = i + 1

        for exe in dump['exec']:
            os.system(exe.replace('$file', x['tmp']+'/'+file))
    
    os.system('rm -rf '+x['tmp'])
    print "Finish all routines!"

elif x['mode'] == "--extract":
    if not x['file']:
        lib.error("You must pass a file as argument!")
    if not os.path.isfile(x['file']):
        lib.error("File <"+x['file']+"> not found!")

    dumps = load()

    os.system('rm -rf '+x['tmp'])
    os.system('mkdir -p '+x['tmp'])
    os.system('cp '+x['file']+' '+x['tmp'])
    os.chdir(x['tmp'])

    file = x['file'][x['file'].rfind("/") + 1:]
    ext = ".enc"
    if (file[len(file) - len(ext):] == ext):
        file = file[0:len(file) - len(ext)]
        
        password = ""
        n = 0
        for dump in dumps:
            l = len(dump['label'])
            if dump['label'] == file[0:l] and l > n:
                n = l
                password = dump['password']
            
        print "****** Decrypting ******"
        os.system('openssl '+x['algorithm']+' -salt -d -in '+file+ext+' -out '+file+' -k '+password)
        os.system('rm -f '+file+ext)

    ext = ".tar.gz"
    if file[len(file) - len(ext):] == ext:
        file = file[0:len(file) - len(ext)]
        print "****** Extracting ******"
        os.system('tar -zxf '+file+ext)
        os.system('rm -f '+file+ext)

    print "Please checkout "+x['tmp']+"/"+file

elif x['mode'] == "--restore":
    if not os.path.isfile(x['restore']):
        lib.error("No restore information!Please run:\n./mysqldump.py --config-restore")
    if not x['file']:
        lib.error("You must pass a directory as argument!")
    if not os.path.isdir(x['file']):
        lib.error("Directory <"+x['file']+"> not found!")

    flags = '--defaults-extra-file='+os.path.dirname(os.path.realpath(__file__))+'/'+x['restore']

    db = os.popen("mysql "+flags+" -BNe 'SHOW DATABASES'").read()
    db = db[0:len(db) - 1]
    D = db.split("\n")

    os.chdir(x['file'])
    ext = ".sql"
    files = os.popen("ls *"+ext).read().split("\n")
    files.pop()
    for file in files:
        db = file[0:len(file) - len(ext)]
        if db == "grants":
            print "grants: Should be restore manualy!"
        else:
            try:
                D.index(db)
                print db+": Already exists, skipping!"
            except ValueError:
                print "***** Restoring "+db+" *****"
                os.system("mysql "+flags+" -BNe 'CREATE DATABASE "+db+"'")
                os.system("mysql "+flags+" "+db+" < "+file)

elif x['mode'] == "--config":
    obj = [
        {
            "label": "string: dump label",
            "host": "string: host ip address",
            "user": "string: user name",
            "grants": "boolean: dump grants?", 
            "encrypt": "boolean: encrypt with same password?", 
            "databases": [
                "string: database name to dump"
            ], 
            "folders": [
                {
                    "path": "string: path to save dump",
                    "limit": "integer: max number of dump files in this folder, 0 for unlimited"
                }
            ],
            "exec": [
                "string: bash command to execute after dump use $file to refer to dump file" 
            ]
        }
    ]
    lib.storeConfig(x['source'], obj)
    print "After edit <"+x['source']+">, please run: "
    print "$ ./mysqldump.py --config-dump"

elif x['mode'] == "--config-dump":
    dumps = lib.loadConfig(x['source'])

    os.system('rm -rf '+x['dump'])
    os.system('mkdir '+x['dump'])

    for dump in dumps:
        path = x['dump']+dump['label']
        os.system('touch '+path)
        os.system('chmod go-rw '+path)
        
        password = getpass.getpass("password for <"+dump['label']+">: ") 

        with open(path, 'w') as filePtr:    
            print >> filePtr, "[client]"
            print >> filePtr, "user="+dump['user']
            print >> filePtr, "password="+password
            print >> filePtr, "host="+dump['host']

elif x['mode'] == "--config-restore":
    os.system('rm -f '+x['restore'])
    os.system('touch '+x['restore'])
    os.system('chmod go-rw '+x['restore'])

    host = raw_input("Host: ")
    user = raw_input("User: ")
    password = getpass.getpass("Password: ") 
        
    with open(x['restore'], 'w') as filePtr:    
        print >> filePtr, "[client]"
        print >> filePtr, "user="+user
        print >> filePtr, "password="+password
        print >> filePtr, "host="+host

else:
    print "Script for mysql backup and encrypt!"
    print "Install"
    print "mysql for dumps and restore"
    print "openssl for encrypt"
    print ""
    print "Usage"
    print "$ ./mysqldump.py --config: create file <"+x['source']+">"
    print "$ ./mysqldump.py --config-dump: save db passwords"
    print "$ ./mysqldump.py --config-restore: save restore password"
    print "$ ./mysqldump.py --dump: dump databases"
    print "$ ./mysqldump.py --extract <filename>: extract backup file"
    print "$ ./mysqldump.py --restore <foldername>: restore .sql files"
