import os 
import sys
import json 

x = {
    'config': os.path.dirname(os.path.realpath(__file__))+'/config/'
}

def error(msg):
    print "Error: "+msg
    quit()

def which(cmds):
    for cmd in cmds:
        if not os.popen("which "+cmd).read():
            error("command <"+cmd+"> not found!")

def getArg(i):
    return sys.argv[i] if len(sys.argv) > i else ""

def printInfo():
    output = '***** '
    for arg in sys.argv:
        output = output + arg + ' '
    output = output + '*****'
    print output

def loadConfig(name):
    path = x['config']+name

    if not os.path.isfile(path):
        error("Unable to locate file <"+path+">")
    
    with open(path) as filePtr:    
        obj = json.load(filePtr)

    return obj

def storeConfig(name, obj):
    path = x['config']+name

    if os.path.isfile(path):
        error("File <"+path+"> already exists")
        
    os.system("mkdir -p "+x['config'])

    with open(path, 'w') as filePtr:    
        print >> filePtr, json.dumps(obj, indent = 4)
        print "Please change for your needs the file <"+name+">!"
