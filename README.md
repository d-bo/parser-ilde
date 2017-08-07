## Dependencies

https://nodejs.org/en/

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

## Images

```bash
# img collector dir (CDN ?)
# jenkins
# ! no end slash
# default to <PROJECT_DIR>/img/all
export ILDE_IMG_DIR=/home/administrator/img
```
