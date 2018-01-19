# -*- coding: utf-8 -*-

import ssl
import json
import socket
import syslog
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

        url = 'https://iledebeaute.ru/brands/'
        syslog.syslog("Start step1 ...")

        try:
            page = urllib2.urlopen(url, timeout=200).read()
        except urllib2.HTTPError as err:
            print(err)
            syslog.syslog(err)
        except urllib2.URLError as err:
            print("step1: urllib2.URLError: ")
            syslog.syslog(err)
        except httplib.BadStatusLine as err:
            print("step1: httplib.BadStatusLine: ")
            syslog.syslog(err)
        except socket.timeout as err:
            print 'step1: X SOCKET TIMEOUT ' + str(err)
            syslog.syslog(err)
        except ssl.SSLError as err:
            print 'step1: SSLError: ' + str(err)
            syslog.syslog(err)

        soup = BeautifulSoup(page, 'html.parser')

        # find img preview link
        select = soup.find('select', {'id': 'headerSelectBrand'})

        inserted_global_new = 0
        inserted_global_double = 0

        inserted_today_new = 0
        inserted_today_double = 0

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
                value = {'val': contents, 'source': 'ilde'}
                double = coll_all.find_one(value)
                if double is None:
                    coll_all.insert_one({'val': contents, 'source': 'ilde'})
                    inserted_global_new = inserted_global_new + 1
                else:
                    inserted_global_double = inserted_global_double + 1

                # today brands double check
                value = {'name': str(val)}
                double = coll.find_one(value)
                if double is None:
                    coll.insert_one({'name': str(val)})
                    inserted_today_new = inserted_today_new + 1
                else:
                    inserted_today_double = inserted_today_double + 1

        syslog.syslog("Step1 Global: new "+str(inserted_global_new)+", double "+str(inserted_global_double)
            +"; today: new "+str(inserted_today_new)+", double "+str(inserted_today_double))