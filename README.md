## Install

```bash
virtualenv ilde
source ilde/bin/activate
pip install -r requirements.txt
```

## Cron

```bash
crontab -e
```

```bash
# everyday at 11:00
# 00 11 * * * source <PROJECT_PATH>/start-ilde.sh <PROJECT_PATH>

00 11 * * * /bin/bash /home/administrator/parser_ilde/start-ilde.sh /home/administrator/parser_ilde
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
