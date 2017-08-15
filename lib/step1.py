# -*- coding: utf-8 -*-

import json
import socket
import urllib2
from bs4 import BeautifulSoup
from pymongo import MongoClient

from lib.utils import Utils



class Step1:

    """ parser step1 """

    def __init__(self, cpool, config = None):
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
        except ssl.SSLError as err:
            print 'SSLError: ' + str(err)

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
