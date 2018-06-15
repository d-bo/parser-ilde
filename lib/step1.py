# -*- coding: utf-8 -*-

import re
import ssl
import json
import socket
import syslog
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
from pymongo import MongoClient

from lib.utils import Utils



class Step1:

    """ parser step1 """

    def __init__(self, cpool, config = None):

        urls = []
        inserted_global_new = 0
        inserted_global_double = 0
        inserted_today_new = 0
        inserted_today_double = 0
        coll_all = cpool['all_brands']
        coll = cpool['collection_ilde_brands']

        print(coll)

        url = 'https://iledebeaute.ru/brands/'
        syslog.syslog("Start step1 ...")
        print("Start step1 ...")

        try:
            page = urllib.request.urlopen(url, timeout=10).read()
        except:
            print("step1 urllib2 error")
            syslog.syslog("step1 urllib2 error")

        soup = BeautifulSoup(page, 'html.parser')

        # find img preview link
        select = soup.find('select', {'id': 'headerSelectBrand'})
        select_li = soup.findAll('li', {'class': False})
        for item in select_li:
            for subitem in item.findAll('a', {'target': '_blank', 'style': False, 'href': re.compile("brands")}):
                url = subitem.get('href').strip()
                brand_name = subitem.get_text().strip()

                value = {'val': brand_name, 'source': 'ilde'}
                double = coll_all.find_one(value)
                if double is None:
                    status = "NEW"
                    coll_all.insert_one({'val': brand_name, 'source': 'ilde'})
                    inserted_global_new = inserted_global_new + 1
                else:
                    status = "DOUBLE"
                    inserted_global_double = inserted_global_double + 1

                # today brands double check
                value = {'name': str(brand_name)}
                double = coll.find_one(value)
                if double is None:
                    today_status = "NEW"
                    coll.insert_one({'name': str(brand_name)})
                    inserted_today_new = inserted_today_new + 1
                else:
                    today_status = "DOUBLE"
                    inserted_today_double = inserted_today_double + 1

                print (status, today_status, url, brand_name)

            syslog.syslog("Step1 Global: new "+str(inserted_global_new)+", double "+str(inserted_global_double)
            +"; today: new "+str(inserted_today_new)+", double "+str(inserted_today_double))

            """
            length = len(item.get_text())
            if length < 40 and length is not 0:
                print (item.get_text())
            """

        """


        for o in select.find_all('option'):
            contents = ''.join(o.contents)
            contents = contents.encode('utf-8')
            contents = contents.strip('*'.encode())
            contents = contents.strip()
            print(contents)
            syslog.syslog("ILDE brand: "+str(contents))
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
        """
        print("End step1")