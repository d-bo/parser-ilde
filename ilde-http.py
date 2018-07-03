# -*- coding: utf-8 -*-

import os
import sys
import socket
import syslog
import configparser
from flask import Flask
from lib.step1 import Step1
from lib.step2 import Step2
from lib.step3 import Step3
from lib.utils import Utils
from datetime import datetime



app = Flask(__name__)
# current script dir
script_dir = os.path.dirname(os.path.abspath(__file__))
# global config (config.ini)
config = configparser.ConfigParser()
config.read(script_dir+'/config.ini')
# work database: linux environment or pd.py.ini ??
dbprefix = Utils.getDbprefix()
cpool = Utils.getCollectionPool(config, dbprefix)

@app.route("/")
def index():
    return "GA"

@app.route("/v1/ping")
def heartbeat():
    return "PONG"

@app.route("/start")
def start():

    syslog.syslog('ILDE start ...')
    print('ILDE start ...')

    coll = cpool['collection_ilde_brands']
    syslog.syslog("ILDE: "+str(coll))
    print((str(coll)))

    res = coll.find().count()
    print(("COUNT RES: "+str(res)))
    print((Utils.getDbprefix()))

    if res < 1:
        Step1(cpool, config)
        Step2(cpool, config)
        Step3(cpool, config)
    else:
        print("ILDE allready started")
        syslog.syslog("ILDE allready started")
        return 'ILDE allready started: '+str(Utils.getDbprefix())

    syslog.syslog('ILDE end')
    print("ILDE end")
    return '@app.route("/start")'

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8801)