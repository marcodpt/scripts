#!/usr/bin/env python

import lib
import os

x = {
    'source': 'git.json',
    'mode': lib.getArg(1)
}

lib.printInfo()

if x['mode'] == "--sync":
    lib.which(['git'])
    repos = lib.loadConfig(x['source'])

    for repo in repos:
        print '*** '+repo['dir']+": "+repo['url']+' ***'
        if not os.path.exists(repo['dir']):
            os.system('git clone '+repo['url']+' '+repo['dir'])
        elif (not os.path.isdir(repo['dir'])) or (not os.path.isdir(os.path.join(repo['dir'], '.git'))):
            lib.warning(repo['dir']+': is not a git repo! skiping!')
        else:
            os.system('cd '+repo['dir']+' && git pull && git push')

elif x['mode'] == "--config":
    repos = [
        {
            'dir': '/absolute/path/to/first/repo',
            'url': 'git@{host}.com:{user}/{repo}.git'
        },{
            'dir': '/absolute/path/to/second/repo',
            'url': 'https://{host}.com/{user}/{repo}'
        }
    ]
    
    lib.storeConfig(x['source'], repos)

else:
    print "Script for import and update your git repos"
    print ""
    print "Install on your machine"
    print "# apt-get install git"
    print ""
    print "Usage"
    print "$ ./git.py --config: generate <"+x['source']+">"
    print "$ ./git.py --sync: pull and push or clone git repos as defined in <"+x['source']+">"
