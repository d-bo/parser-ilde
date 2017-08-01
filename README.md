## Dependencies

https://nodejs.org/en/

## Install

```bash
npm install
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
# 00 11 * * 1 source <PROJECT_PATH>/start-ilde.sh <PROJECT_PATH>

00 11 * * * /bin/bash /home/administrator/parser_ilde/start-ilde.sh /home/administrator/parser_ilde
```
