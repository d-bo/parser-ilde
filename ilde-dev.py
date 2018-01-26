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

print("Start ILDE parser ...")
syslog.syslog("Start ILDE parser ...")
#Step1(cpool, config)
#Step2(cpool, config)
#Step25(cpool, config, script_dir)
Step3(cpool, config)
syslog.syslog("End ILDE parser")
