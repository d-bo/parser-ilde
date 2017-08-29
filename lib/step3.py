# -*- coding: utf-8 -*-

import os
import ssl
import json
import socket
import execjs
import httplib
import urllib2
from bs4 import BeautifulSoup
from datetime import datetime

from lib.utils import Utils



class Step3:

    """ ergerg """

    def __init__(self, cpool, config = None):

        collection = cpool['collection_ilde']
        collection_final = cpool['collection_ilde_final']
        global_links = cpool['collection_global_links']
        failed_links = cpool['collection_failed_links']

        cursor = global_links.find({'val': { '$exists': True }})

        i = 0
        total = 0

        for u in cursor:

            url = u['val']

            try:
                page = urllib2.urlopen(url, timeout=200).read()
            except urllib2.HTTPError as err:
                failed_id = failed_links.insert_one({"val": url}).inserted_id
                print(err)
                Utils._logfile('step3: '+str(err))
            except urllib2.URLError as err:
                print("step3: urllib2.URLError: ")
                continue
            except httplib.BadStatusLine as err:
                print("step3: httplib.BadStatusLine: ")
                continue
            except socket.timeout as err:
                print 'step3: X SOCKET TIMEOUT ' + str(err)
                Utils._logfile('step3: '+'X SOCKET TIMEOUT ' + str(err))
            except ssl.SSLError as err:
                print 'step3: SSLError: ' + str(err)

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
                        print('step3: whooops! no json')
                        Utils._logfile('step3: '+'whooops! no json')

                    print(url)
                    Utils._logfile('step3: '+url)

                    Utils.insertProductItems(_json, cpool, preview_img_link)
                    global_links.replace_one({'last': { '$exists': True }}, {'last': url})

            i = i + 1
