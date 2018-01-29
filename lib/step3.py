# -*- coding: utf-8 -*-

import os
import re
import ssl
import sys
import json
import socket
import syslog
import execjs
import httplib
import urllib2
from bs4 import BeautifulSoup
from bs4 import NavigableString, Tag
from datetime import datetime

from lib.utils import Utils



class Step3:

    """ ergerg """

    def __init__(self, cpool, config = None):

        syslog.syslog("Start step3 ...")

        collection = cpool['collection_ilde']
        collection_final = cpool['collection_ilde_final']
        global_links = cpool['collection_global_links']
        failed_links = cpool['collection_failed_links']

        cursor = global_links.find({'val': { '$exists': True }})

        i = 0
        total = 0

        # Extracted from non-script html tags
        scraped = {}
        cycflag = False

        for u in cursor:

            url = u['val']

            if cycflag is False:
                if url != "http://iledebeaute.ru/shop/care/face/lips/zaschitnyiy_balzam_dlya_gub;2qma/":
                    continue
                else:
                    cycflag = True

            syslog.syslog(url)

            try:
                page = urllib2.urlopen(url, timeout=10).read()
            except:
                syslog.syslog("Step3 urllib2 error")
                print "Step3 urllib2 error"

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
                        syslog.syslog('step3: whooops! no json')
                        print('step3: whooops! no json')
                        continue

                    scraped['url'] = url

                    syslog.syslog(url)

                    # Extract descriptions
                    descs = []
                    desc = soup.find_all('div', {'class': 'b-tab__text'})
                    for de in desc:
                        paragraphs = de.find_all('p')
                        for pa in paragraphs:
                            if not isinstance(pa.contents[0], Tag):
                                descs.append(pa.contents[0])
                    if len(descs) > 0:
                        scraped['desc'] = " ".join(descs)

                    # Big pic
                    scraped['big_pic'] = None
                    bigpic = soup.find_all('span', {'class': 'preview'})
                    for bp in bigpic:
                        scraped['big_pic'] = bp['data-href']

                    # Breadcrumbs
                    crumbs = []
                    scraped['Navi'] = None
                    brcr = soup.find_all('span', {'itemprop': 'title'})
                    for brc in brcr:
                        if isinstance(brc, NavigableString):
                            continue
                        if isinstance(brc, Tag):
                            crumbs.append(unicode(brc.string))
                    if len(crumbs) > 0:
                        scraped['Navi'] = ";".join(crumbs)
                        print "NAVI: "+scraped['Navi']

                    # Volume
                    scraped['volume'] = None
                    volume = soup.find_all('b', text=re.compile('Объём'))
                    for vol in volume:
                        print "VOL"+vol.string
                        scraped['vol'] = vol.string

                    # VIP price
                    scraped['vip_price'] = None
                    vip = soup.find_all('dd', {'class': 'b-product-price__card b-product-price__card--vip'})
                    for vi in vip:
                        vip_price = vi.string.encode('utf-8')
                        vip_price = vip_price.replace("руб.", "")
                        vip_price = vip_price.strip()
                        scraped['vip_price'] = vip_price

                    Utils.insertProductItems(_json, cpool, scraped, preview_img_link)
                    global_links.replace_one({'last': { '$exists': True }}, {'last': url})

            i = i + 1

        syslog.syslog("End step3")
