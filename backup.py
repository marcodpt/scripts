#!/usr/bin/env python
import json
import sys 
import os 
from datetime import datetime

x = {
    'dir': os.path.dirname(os.path.realpath(__file__))+'/config/',
    'source': 'backup.json',
    'ext': '.cnf',
    'tmp': '/tmp/script_backup',
    'algorithm': 'aes-256-cbc',
    'mode': sys.argv[1] if len(sys.argv) > 1 else "",
    'file': sys.argv[2] if len(sys.argv) > 2 else ""
}

def error(msg):
    print "Error: "+msg
    quit()

def loadConfig():
    path = x['dir']+x['source']
    
    with open(path) as filePtr:    
        dumps = json.load(filePtr)

    for dump in dumps:
        path = x['dir']+dump['label']+x['ext']
        with open(path) as filePtr:    
            lines = filePtr.readlines()
        for line in lines:
            data = line.split("=")
            if len(data) == 2 and data[0] == "password":
                dump["password"] = data[1]
        
    return dumps

print "***** backup "+x['mode']+" ******"

if x['mode'] == "--dump":
    dumps = loadConfig()

    os.system('rm -rf '+x['tmp'])
    os.system('mkdir -p '+x['tmp'])

    iso = str(datetime.now()).replace(" ", "T", 1)
    iso = iso[0:16].replace(':', '_')

    print iso

    for dump in dumps:
        file = dump['label']+iso
        path = x['tmp']+"/"+file
        
        flags = '--defaults-extra-file='+x['dir']+dump['label']+x['ext']

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
        error("You must pass a file as argument!")
    if not os.path.isfile(x['file']):
        error("File <"+x['file']+"> not found!")

    dumps = loadConfig()

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
    if not x['file']:
        error("You must pass a directory as argument!")
    if not os.path.isdir(x['file']):
        error("Directory <"+x['file']+"> not found!")

    dumps = loadConfig()

    flags = '--defaults-extra-file='+x['dir']+'restore'+x['ext']

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

else:
    print "Script for mysql backup and encrypt!"
    print "--dump: dump databases"
    print "--extract <filename>: extract backup file"
    print "--restore <foldername>: restore .sql files"
