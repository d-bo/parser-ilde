# -*- coding: utf-8 -*-

import ssl
import json
import socket
import httplib
import urllib2
from bs4 import BeautifulSoup
from pymongo import MongoClient

from lib.utils import Utils



class Step1:

    """ parser step1 """

    def __init__(self, cpool, config = None):
        urls = []
        coll_all = cpool['all_brands']
        coll = cpool['collection_ilde_brands']
        print(coll)
        Utils._logfile('step1: '+str(coll))

        url = 'https://iledebeaute.ru/brands/'

        try:
            page = urllib2.urlopen(url, timeout=200).read()
        except urllib2.HTTPError as err:
            print(err)
            Utils._logfile('step1: '+str(err))
        except urllib2.URLError as err:
            print("step1: urllib2.URLError: ")
        except httplib.BadStatusLine as err:
            print("step1: httplib.BadStatusLine: ")
        except socket.timeout as err:
            print 'step1: X SOCKET TIMEOUT ' + str(err)
            Utils._logfile('step1: '+'X SOCKET TIMEOUT ' + str(err))
        except ssl.SSLError as err:
            print 'step1: SSLError: ' + str(err)

        soup = BeautifulSoup(page, 'html.parser')

        # find img preview link
        select = soup.find('select', {'id': 'headerSelectBrand'})

        for o in select.find_all('option'):
            contents = ''.join(o.contents)
            contents = contents.encode('utf-8')
            contents = contents.strip('*')
            contents = contents.strip()
            print(contents)
            val = o['value'].strip('/')
            val = str(val)
            if val is not "":

                # brands global pool double check
                value = {'val': contents}
                double = coll_all.find_one(value)
                if double is None:
                    coll_all.insert_one({'val': contents, 'name': 'ilde'})
                    print("GLOBAL INSERT")
                else:
                    print("GLOBAL DOUBLE")

                # today brands double check
                value = {'name': str(val)}
                double = coll.find_one(value)
                if double is None:
                    coll.insert_one({'name': str(val)})
                    print("TODAY INSERT\r\n")
                else:
                    print("TODAY DOUBLE\r\n")
            Utils._logfile('step1: '+str(val))
