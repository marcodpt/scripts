#!/usr/bin/python2

import lib 
import json
import os 
import getpass
from datetime import datetime

x = {
    'source': 'mysqldump.json',
    'tmp': '/tmp/mysqldump',
    'algorithm': 'aes-256-cbc',
    'mode': lib.getArg(1),
    'file': lib.getArg(2)
}

def mysqlPass(host, user, password):
    fileStr = "[client]\n"
    fileStr += "user="+user+"\n"
    fileStr += "password="+password+"\n"
    fileStr += "host="+host

    filePath = "/tmp/.mysql"

    with open(filePath,'w') as f:
        f.write(fileStr)

    return filePath

lib.printInfo()

if x['mode'] == "--dump":
    dumps = lib.loadConfig(x['source'])['dump']

    os.system('rm -rf '+x['tmp'])
    os.system('mkdir -p '+x['tmp'])

    iso = str(datetime.now()).replace(" ", "T", 1)
    iso = iso[0:16].replace(':', '_')

    print iso

    for dump in dumps:
        print "Host: "+dump['label']

        file = dump['label']+iso
        path = x['tmp']+"/"+file
        os.system('mkdir -p '+path)
        secret = mysqlPass(dump['host'], dump['user'], dump['pass'])
        flags = '--defaults-extra-file='+secret

        for grant in dump['grants']:
            print "***** Dumping Grants *****"
            os.system("mysql "+flags+" -e 'show grants for "+grant+"' >> "+path+"/grants.sql")

        if os.path.isfile(path+"/grants.sql"):
            os.system("sed -i '/Grants for/d' "+path+"/grants.sql")
            os.system("sed -i 's|PASSWORD <secret>|\""+dump['pass']+"\"|' "+path+"/grants.sql")
            os.system("sed 's/$/;/' "+path+"/grants.sql > "+path+"/grants2.sql")
            os.system("mv -f "+path+"/grants2.sql "+path+"/grants.sql")
        
        flags += ' --force'
        flags += ' --opt'
        flags += ' --databases'
        flags += ' --routines'
        flags += ' --set-gtid-purged=OFF'
        flags += ' --max_allowed_packet=512M'

        for db in dump['databases']:
            print "***** Dumping "+db+" *****"
            os.system('mysqldump '+flags+' '+db+' > '+path+"/"+db+'.sql')

        os.system('rm '+secret)

        print "***** Compressing *****"
        os.chdir(x['tmp'])
        os.system('tar -zcf '+file+'.tar.gz '+file)
        os.system('rm -rf '+file)
        file += '.tar.gz'

        if dump['encrypt']:
            print "***** Encrypting *****"
            os.system('openssl '+x['algorithm']+' -salt -in '+file+' -out '+file+'.enc -k '+dump['pass'])
            os.system('rm -rf '+file)
            file += '.enc'

        print "****** Moving File ******"
        for folder in dump['folders']:
            if not os.path.isdir(folder['path']):
                print "<"+folder['path']+"> does not exists, skipping!"
                continue
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

    dumps = lib.loadConfig(x['source'])['dump']

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
                password = dump['pass']
            
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
        lib.error("You must pass a directory as argument!")
    if not os.path.isdir(x['file']):
        lib.error("Directory <"+x['file']+"> not found!")

    restore = lib.loadConfig(x['source'])['restore']
    os.system('mkdir -p '+x['tmp'])
    secret = mysqlPass(restore['host'], restore['user'], restore['pass'])
    flags = '--defaults-extra-file='+secret

    db = os.popen("mysql "+flags+" -BNe 'SHOW DATABASES'").read()
    db = db[0:len(db) - 1]
    D = db.split("\n")

    os.chdir(x['file'])
    ext = ".sql"
    grants = False
    files = os.popen("ls *"+ext).read().split("\n")
    files.pop()
    for file in files:
        db = file[0:len(file) - len(ext)]
        if db == "grants":
            grants = True
        else:
            try:
                D.index(db)
                print db+": Already exists, skipping!"
            except ValueError:
                print "***** Restoring "+db+" *****"
                os.system("mysql "+flags+" -BNe 'CREATE DATABASE "+db+"'")
                os.system("mysql "+flags+" "+db+" < "+file)

    if grants:
        print "***** Restoring Grants *****"
        os.system("mysql "+flags+" "+db+" < grants.sql")

    os.system('rm '+secret)

elif x['mode'] == "--config":
    obj = {
        "restore": {
            "host": "string: host ip address for restore dump",
            "user": "string: user name",
            "pass": "string: user password",
        },
        "dump": [
            {
                "label": "string: dump label",
                "host": "string: host ip address",
                "user": "string: user name",
                "pass": "string: user password",
                "grants": [
                    "string: user name",
                    "string: 'user'@'host'"
                ], 
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
    }
    lib.storeConfig(x['source'], obj)

else:
    print "Script for mysql backup and encrypt!"
    print "Install"
    print "mysql for dumps and restore"
    print "openssl for encrypt"
    print ""
    print "Usage"
    print "$ ./mysqldump.py --config: create file <"+x['source']+"> with your dump config"
    print "$ ./mysqldump.py --dump: dump databases"
    print "$ ./mysqldump.py --extract <filename>: extract backup file"
    print "$ ./mysqldump.py --restore <foldername>: restore .sql files"
