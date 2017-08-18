# -*- coding: utf-8 -*-

import os
import sys
import socket
from lib.step1 import Step1
from lib.step2 import Step2
from lib.step25 import Step25
from lib.step3 import Step3
import configparser
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
server_address = ("", 8801)
print >>sys.stderr, 'starting up on %s port %s' % server_address
sock.bind(server_address)

sock.listen(1)

while True:
    connection, client_address = sock.accept()
    try:
        print >>sys.stderr, 'connection from', client_address
        while True:
            data = connection.recv(16)
            print(data)
            if data == 'step1':
                print("Call step1 ...")
                Step1(cpool, config)
            if data == 'step2':
                print("Call step2 ...")
                Step2(cpool, config)
            if data == 'step25':
                print("Call step25 ...")
                Step25(cpool, config, script_dir)
            if data == 'step3':
                print("Call step3 ...")
                Step3(cpool, config)
            if data == 'start':
                coll = cpool['collection_ilde_brands']
                res = coll.find().count()
                if res < 1:
                    print("Start ILDE parser ...")
                    Step1(cpool, config)
                    Step2(cpool, config)
                    Step25(cpool, config, script_dir)
                    Step3(cpool, config)
                else:
                    print("Allready started")
            if data:
                connection.sendall(data)
            else:
                break
    finally:
        # Clean up the connection
        connection.close()
