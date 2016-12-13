# Script for mysql backup

```
$ mkdir config/
$ cd config/
$ touch backup.json
$ touch restore.cnf
$ touch <label>.cnf
$ ./backup.py
```

### backup.json
```json
[
    {
        "grants": "boolean: dump grants?", 
        "encrypt": "boolean: encrypt with same password?", 
        "databases": [
            "string: database name to dump"
        ], 
        "folders": [{
            "path": "string: folder path to store backup",
            "limit": "integer: limit of backup files in this folder, 0 no limit"
        }],
        "exec": [
           "string: execute after file is ready use: $file to refer to backup file" 
        ], 
        "label": "string: label that will be used in file name and in .cnf file",
    }
]
```

### mysql .cnf file
 - Use the same label of backup.json
 
```
[client]
user=xxxxx
password=xxxxxx
host=xxx.xxx.xxx.xxx
```
