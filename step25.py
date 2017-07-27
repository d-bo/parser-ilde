# -*- coding: utf-8 -*-

import os
import json
import socket
import urllib2
import configparser
from datetime import datetime
from bs4 import BeautifulSoup
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



collection = cpool['collection_ilde']
pagination = cpool['collection_pagination']
global_links = cpool['collection_global_links']

cursor = pagination.find({'val': { '$exists': True }})
last = pagination.find_one({'last': { '$exists': True }})
last_global = global_links.find_one({'last': { '$exists': True }})

# pagination last url
if last:
    if 'last' in last:
        last_url = last['last']

if 'last_url' in locals():
    if last_url == '':
        del last_url

# global_links collection last url
if last_global:
    if 'last' in last_global:
        last_url_global = last_global['last']
        if last_url_global == '':
            del last_url_global



# iterate
for item in cursor:
    zurl = item['val']

    # restore point
    if 'last_url' in locals():
        if last_url == zurl:
            del last_url
        else:
            continue

    try:
        response = urllib2.urlopen(zurl, timeout=10)
        pagination.replace_one({'last': { '$exists': True }}, {'last': zurl})
    except urllib2.HTTPError as err:
        print 'X ['+item+']' + err
    except socket.timeout as err:
        print 'X SOCKET TIMEOUT ' + str(err)
    else:
        soup = BeautifulSoup(response, 'html.parser')
        script = soup.find_all('script')
        for t in script:
            _str = unicode(t.string)
            # looking for TMPCounter var in <script>
            if _str.find("var TMPCounter") != -1:
                _str = _str.replace('var TMPCounter = ', '')
                _str = _str.replace('//<!--', '')
                _str = _str.replace('//-->', '')
                _str = _str.replace('|| {};', '')

                try:
                    _json = json.loads(_str)
                    _json_str = json.dumps(_json['basket'])
                except:
                    print('whooops! no json')

                Utils.insertProductItems(_json, collection)

                # extract image & save to folder
                img_dir = script_dir+"/img/"
                Utils.extractImg(_json['basket'], img_dir)

        # continue

        # extract single product page
        # save
        hrefs = soup.find_all("a", class_="b-showcase__item__img")

        for h in hrefs:
            if h['href'] != '':
                url = 'http://iledebeaute.ru' + str(h['href'])
                value = {'val': url}
                double = global_links.find_one(value)
                if double is None:
                    _id = global_links.insert_one(value).inserted_id
                    print "Page link inserted: " + str(_id)
                #global_links.replace_one({'last': { '$exists': True }}, {'last': url})



# must be completed
pagination.replace_one({'last': { '$exists': True }}, {'last': ''})

print("Script exec time: " + str(datetime.now() - startTime))
