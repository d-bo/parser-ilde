# -*- coding: utf-8 -*-

import os
import ssl
import json
import socket
import urllib2
from datetime import datetime
from pymongo import MongoClient

from lib.utils import Utils



class Step2:

    """ ergerg """

    def __init__(self, cpool, config = None):

        urls = []

        # get brands
        coll = cpool['collection_ilde_brands']
        brands = coll.find()
        brands = list(brands)

        collection = cpool['collection_pagination']

        # iterate brands
        for a in brands:
            for i in range(1,10):
                url = 'http://iledebeaute.ru/brands/' + a['name'] + '/catalog/page' + str(i) + '/?perpage=72'
                try:
                    response = urllib2.urlopen(url, timeout=200)
                except urllib2.HTTPError as err:
                    print 'X ['+url+']'
                    Utils._logfile('step2: '+'X ['+url+']')
                except socket.timeout as err:
                    print 'X SOCKET TIMEOUT ' + str(err)
                    Utils._logfile('step2: '+'X SOCKET TIMEOUT ' + str(err))
                except ssl.SSLError as err:
                    print 'SSLError: ' + str(err)
                else:
                    value = {'val': url, 'brand': a['name']}
                    double = collection.find_one(value)
                    if double is None:
                        _id = collection.insert_one(value).inserted_id
                        print "Inserted: " + str(_id)
                        Utils._logfile('step2: '+"Inserted: " + str(_id))
                    print '+ ['+url+']'
                    Utils._logfile('step2: '+'+ ['+url+']')
