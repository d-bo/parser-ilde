## Install

```bash
cd parser_ilde
virtualenv ilde
source ilde/bin/activate
pip install -r requirements.txt
python tcp-server.py
```

## Cron

```bash
crontab -e
```

```bash
# everyday at 11:00

00 11 * * * echo -n "start"|netcat 127.0.0.1 8801
```

## Jenkins
### General > Build > Execute shell

```bash
#!/bin/bash

virtualenv ilde
source $WORKSPACE/ilde/bin/activate
pip install -r requirements.txt
# img static collect dir
echo '/home/administrator/static/img' > ILDE_IMG_PATH
deactivate
```
