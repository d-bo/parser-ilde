# -*- coding: utf-8 -*-

import os
import sys
import ssl
import json
import syslog
import socket
import httplib
import urllib2
from bs4 import BeautifulSoup
from datetime import datetime
from pymongo import MongoClient

from lib.utils import Utils

"""
Iterate brands
"""

class Step2:

    """ ergerg """

    def __init__(self, cpool, config = None):

        urls = []

        # get brands
        coll = cpool['collection_ilde_brands']
        brands = coll.find()
        brands = list(brands)

        collection = cpool['collection_pagination']

        syslog.syslog("Start step2 ...")

        _n = 0 # count new
        _d = 0 # count double

        # iterate brands
        for a in brands:
            for i in range(1,10):
                # TODO stop i + 1 first empty page
                url = 'http://iledebeaute.ru/brands/' + a['name'] + '/catalog/page' + str(i) + '/?perpage=72'
                syslog.syslog(url)
                print url
                try:
                    response = urllib2.urlopen(url, timeout=3)  # 2 seconds
                except:
                    print "Exception urllib2.urlopen"
                    syslog.syslog("Exception urllib2.urlopen")
                    continue

                value = {'val': url, 'brand': a['name']}

                if self.checkEmptyPage(response, a['name'], cpool) > 0:
                    double = collection.find_one(value)
                    if double is None:
                        _id = collection.insert_one(value).inserted_id
                        _n = _n + 1
                    else:
                        _d = _d + 1

                else:
                    break

        syslog.syslog("Step2 new "+str(_n)+", double "+str(_d))

    """
    Empty products list check
    """
    def checkEmptyPage(self, response, brand, cpool):
        # Parse html
        c = 0
        soup = BeautifulSoup(response, 'html.parser')
        divs = soup.find('div', {'class': 'b-showcase b-showcase_sheet'})
        if divs is not None:
            allready_extracted = 0
            for i in divs.find_all('div', {'class': 'b-showcase__item'}):
                hrefs = i.find_all("a", class_="b-showcase__item__img")
                if hrefs is not None:
                    for h in hrefs:
                        if h['href'] != '':
                            purl = 'http://iledebeaute.ru' + str(h['href'])
                            value = {'val': purl, 'brand': brand}
                            global_links = cpool['collection_global_links']
                            double = global_links.find_one(value)
                            if double is None:
                                _id = global_links.insert_one(value).inserted_id
                                print "Extracted: "+str(purl)
                            else:
                                allready_extracted = allready_extracted + 1
                                
        if c > 0: return count
