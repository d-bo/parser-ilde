# -*- coding: utf-8 -*-

import os
import sys
import socket
import syslog
import configparser
from lib.step1 import Step1
from lib.step2 import Step2
from lib.step3 import Step3
from lib.utils import Utils
from datetime import datetime



# script exec time
startTime = datetime.now()
# current script dir
script_dir = os.path.dirname(os.path.abspath(__file__))
# global config (config.ini)
config = configparser.ConfigParser()
config.read(script_dir+'/config.ini')
# work database: linux environment or pd.py.ini ??
dbprefix = Utils.getDbprefix()
cpool = Utils.getCollectionPool(config, dbprefix)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ("0.0.0.0", 8801)
print('starting up on %s port %s' % server_address, file=sys.stderr)
sock.bind(server_address)

sock.listen(1)

while True:
    connection, client_address = sock.accept()
    try:
        print('connection from', client_address, file=sys.stderr)
        syslog.syslog("Connection from: "+str(client_address))
        while True:
            data = connection.recv(16)
            print(data)
            if data == 'step1':
                print("Call step1 ...")
                Step1(cpool, config)
            if data == 'step2':
                print("Call step2 ...")
                Step2(cpool, config)
            if data == 'step3':
                print("Call step3 ...")
                Step3(cpool, config)
            if data == 'start':
                coll = cpool['collection_ilde_brands']
                res = coll.find().count()
                if res < 1:
                    print("Start ILDE parser ...")
                    syslog.syslog("Start ILDE parser ...")
                    Step1(cpool, config)
                    Step2(cpool, config)
                    Step3(cpool, config)
                else:
                    print("Allready started")
                    syslog.syslog("ILDE allready started")
            if data:
                connection.sendall(data)
            else:
                break
    except:
        syslog.syslog("ILDE allready started")
        print("sock.accept() exception")
    finally:
        # Clean up the connection
        connection.close()
