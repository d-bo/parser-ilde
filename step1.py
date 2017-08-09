# -*- coding: utf-8 -*-

import os
import json
import socket
import urllib2
import configparser
from bs4 import BeautifulSoup
from datetime import datetime
from pymongo import MongoClient

from lib.utils import Utils



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



urls = []



coll = cpool['collection_ilde_brands']
print(coll)
Utils._logfile('step1: '+str(coll))

url = 'https://iledebeaute.ru/brands/'

try:
    page = urllib2.urlopen(url, timeout=100).read()
except urllib2.HTTPError as err:
    print(err)
    Utils._logfile('step1: '+str(err))
except socket.timeout as err:
    print 'X SOCKET TIMEOUT ' + str(err)
    Utils._logfile('step1: '+'X SOCKET TIMEOUT ' + str(err))

soup = BeautifulSoup(page, 'html.parser')

# find img preview link
select = soup.find('select', {'id': 'headerSelectBrand'})

for o in select.find_all('option'):
    val = o['value'].strip('/')
    val = str(val)
    if val is not "":
        coll.insert_one({'name': str(val)})
    print(val)
    Utils._logfile('step1: '+str(val))

print("Script exec time: " + str(datetime.now() - startTime))
Utils._logfile('step1: '+"Script exec time: " + str(datetime.now() - startTime))
