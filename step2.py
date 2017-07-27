# -*- coding: utf-8 -*-

import os
import json
import socket
import urllib2
import configparser
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



# brands are in a file
f = open('brands.json', 'r')
a = f.read()
brands = json.loads(a)

collection = cpool['collection_pagination']
print(collection)
# iterate brands
for a in brands:
    for i in range(1,10):
        url = 'http://iledebeaute.ru/brands/' + a + '/catalog/page' + str(i) + '/?perpage=72'
        try:
            response = urllib2.urlopen(url, timeout=10)
        except urllib2.HTTPError as err:
            print 'X ['+url+']'
        except socket.timeout as err:
            print 'X SOCKET TIMEOUT ' + str(err)
        else:
            value = {'val': url}
            double = collection.find_one(value)
            if double is None:
                _id = collection.insert_one(value).inserted_id
                print "Inserted: " + str(_id)
            print '+ ['+url+']'

print("Script exec time: " + str(datetime.now() - startTime))
