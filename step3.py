# -*- coding: utf-8 -*-

import os
import json
import socket
import execjs
import urllib2
import configparser
from bs4 import BeautifulSoup
from datetime import datetime

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

collection = cpool['collection_ilde']
global_links = cpool['collection_global_links']
failed_links = cpool['collection_failed_links']

cursor = global_links.find({'val': { '$exists': True }})

i = 0
total = 0

for u in cursor:

    url = u['val']

    try:
        page = urllib2.urlopen(url, timeout=10).read()
    except urllib2.HTTPError as err:
        failed_id = failed_links.insert_one({"val": url}).inserted_id
        print(err)
    except socket.timeout as err:
        print 'X SOCKET TIMEOUT ' + str(err)

    soup = BeautifulSoup(page, 'html.parser')

    # find img preview link
    preview_img_link = soup.find('a', {'class': 'preview'})
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

            print(url)

            Utils.insertProductItems(_json, collection, preview_img_link)
            global_links.replace_one({'last': { '$exists': True }}, {'last': url})

    i = i + 1

print("Script exec time: " + str(datetime.now() - startTime))
