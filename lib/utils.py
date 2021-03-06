# -*- coding: utf-8 -*-

import os
import ssl
import csv
import socket
import http.client
import urllib.request, urllib.error, urllib.parse
from PIL import Image
import urllib.request, urllib.parse, urllib.error, io
from datetime import datetime
from pymongo import MongoClient

class Utils:

    """ Class Utils """

    # products count
    count_new = 0
    count_double = 0

    # product images count
    img_new = 0
    img_double = 0

    # price
    price_double = 0      # daily double price

    # collection pool
    cpool = None

    @staticmethod
    def parseSheetsCSV(csv_path):

        """ parse csv sheets """

        is_file = True
        count = 0
        sheets = []
        while is_file:
            filename = csv_path+'.'+str(count)
            is_file = os.path.isfile(filename)
            if is_file:
                sheets.append(Utils.extractSheet(filename))
            count = count + 1

        return sheets



    @staticmethod
    def extractSheet(path):

        """ extract csv data """

        out = []
        with open(path, 'rb') as csv_file:
            reader = csv.reader(csv_file, delimiter=',')
            for row in reader:
                extended_row = {}
                extended_row['data'] = row
                extended_row['len'] = len(row)
                out.append(extended_row)

        return out



    @staticmethod
    def _log(cpool, event_type, desc):

        """	log event """

        cpool['collection_history'].insert_one({
            'type': event_type,
            'desc': desc
        })



    @staticmethod
    def _logfile(msg):

        """ log to msg dir """

        fname = Utils.getDbprefix()['daily']
        path = "./log/"+fname+"_Log"
        try:
            os.mkdir("./log")
        except OSError as err:
            pass

        f = open(path, "a+")
        f.write(str(msg)+"\n")
        f.close()



    @staticmethod
    def Log(cpool, subj, act, val):

        """ Mongo log event """

        cpool['collection_log'].insert_one({
            'subject': subj,
            'action': act,
            'val': val,
            'date': Utils.getDbprefix()['daily']
        })



    @staticmethod
    def extractImg(doc, img_dir):

        """ json extract image -> save in img_dir """

        for item in doc:
            if 'image' in item:
                url = "http://static.iledebeaute.ru"+item['image']
                url = url.replace('156', '500')
                url = url.replace('257', '500')
                try:
                    file = io.StringIO(urllib.request.urlopen(url, timeout=200).read())
                except:
                    print("Cannot open image url")
                    continue

                img = Image.open(file)
                new_dir = img_dir + "/"
                if not os.path.exists(new_dir):
                    os.makedirs(new_dir)
                new_file = new_dir+str(item['articul'])+".jpg"
                if os.path.isfile(new_file) is not True:
                    #print(("Image saved url: "+url))
                    img.save(new_file)
                    Utils.img_new = Utils.img_new + 1
                else:
                    #print(("Image allready exists: "+new_file))
                    Utils.img_double = Utils.img_double + 1



    @staticmethod
    def insertProductItems(basket, cpool, scraped, preview_img_link = None):

        cod_good = False

        """ mongodb insert """
        collection = cpool['collection_ilde']
        collection_final = cpool['collection_ilde_final']
        brand_coll = cpool['collection_ilde_brands']

        for item in basket['basket']:
            #print(item)
            #print(scraped)

            item['brand'] = item['brand'].upper()

            # New brand ??
            double = brand_coll.find_one({'source': 'ilde', 'val': item['brand']})
            if double is None:
                brand_id = brand_coll.insert_one({
                        'source': 'ilde',
                        'val': item['brand']
                    }).inserted_id
            else:
                print("BRAND DOUBLE")

            # is allready in final collection ?
            double = collection_final.find_one({"articul": item['articul']})

            # document into price collection
            price_doc = {
                'articul': item['articul'],
                'p_price': item['p_price'],
                'p_original_price': item['p_original_price'],
                'brand': item['brand'],
                'product_id': item['product_id'],
                'date': Utils.getDbprefix()['daily']
            }
            # gestori match by articul check
            gestori = cpool['collection_gestori']
            match_articul = gestori.find_one({'Artic': item['articul']})

            if match_articul is not None:
                #print(("Match articul: ", item['articul']))
                cod_good = match_articul['Cod_good']
                print("GESTORI FOUND")
                #print("Match articul: ", item['articul'], list(match_articul))

            if double is None:
                if 'cod_good' in locals():
                    item['gestori'] = cod_good
                # insert img link to document
                if preview_img_link is not None:
                    item['image'] = preview_img_link['href']
                #print(("\n\n img -> mongo document: "+str(item)+"\np_ids: "+str(basket['p_ids'])+"\n"))

                # insert price
                Utils.insertPrice(cpool, price_doc)

                # final collection
                del item['p_price']
                del item['p_original_price']
                # Insert time
                item['LastUpdate'] = Utils.getDbprefix()['daily']
                _id = collection_final.insert_one(item).inserted_id
                Utils.count_new = Utils.count_new + 1
                Utils.Log(cpool, 'ilde', 'new_articul', item['articul'])
                print("NEW:", item)
            else:
                # update final
                #if 'cod_good' in locals():

                # Update anyway
                res = collection_final.update({'articul': item['articul']},
                {
                    '$set': {
                        'brand': item['brand'],
                        'gestori': cod_good,
                        'listingprice': item['p_price'],
                        'p_original_price': item['p_original_price'],
                        'Navi': scraped['Navi'],
                        'big_pic': scraped['big_pic'],
                        'desc': scraped['desc'],
                        'vol': scraped['volume'],
                        'url': scraped['url'],
                        'vip_price': scraped['vip_price'],
                        'LastUpdate': Utils.getDbprefix()['daily']
                    }
                }, multi=True)

                print("RES", res)

                # insert price
                Utils.insertPrice(cpool, price_doc)

                #print("Double: articul "+item['articul'])
                Utils.count_double = Utils.count_double + 1
                print("UPDATED", item, scraped)



    @staticmethod
    def insertPrice(cpool, price_doc):

        """
        insert price | check for daily double
        TODO: upsert, create index on `articul`, `date`
        """

        collection = cpool['collection_ilde']

        double = collection.find_one({
            "articul": price_doc['articul'],
            "date": Utils.getDbprefix()['daily']
        })
        if double is None:
            return collection.insert_one(price_doc).inserted_id
        else:
            #print('DOUBLE PRICE')
            return False



    @staticmethod
    def getDbprefix():
        return {
            'monthly': datetime.strftime(datetime.now(), "%m-%Y"),
            'daily': datetime.strftime(datetime.now(), "%d-%m-%Y")
        }



    @staticmethod
    def getCollectionPool(config, dbprefix = None):

        """ collections pool """

        if 'ILDE_MONGO_DB' in os.environ:
            db = os.environ['ILDE_MONGO_DB']
        else:
            db = config['mongodb']['workdb']

        MC = MongoClient(config['mongodb']['conn'])
        print(MC)
        if dbprefix is None:
            return {
                'all_brands': MC[db]['all_brands'],
                'collection_gestori': MC[db][config['coll']['gestori']],
                'collection_sheets': MC[db][config['coll']['sheets']],
                'collection_supplier': MC[db][config['coll']['supplier']],
                'collection_supplier_info': MC[db][config['coll']['supplier_info']],
                'collection_sheets_rules': MC[db][config['coll']['sheets_rules']],
                'collection_history': MC[db][config['coll']['history']],
                'collection_ilde': MC[db][config['coll']['ilde']],
                'collection_ilde_final': MC[db][config['coll']['ilde_final']],
                'collection_letu': MC[db][config['coll']['letu']],
                'collection_global_links': MC[db][config['coll']['global_links']],
                'collection_failed_links': MC[db][config['coll']['failed_links']],
                'collection_pagination': MC[db][config['coll']['pagination']],
                'collection_ilde_brands': MC[db][config['coll']['ilde_brands']],
                'collection_log': MC[db][config['coll']['log']]
            }
        else:
            return {
                'all_brands': MC[db]['all_brands'],
                'collection_gestori': MC[db][config['coll']['gestori']],
                'collection_sheets': MC[db][dbprefix['daily']+"_"+config['coll']['sheets']],
                'collection_supplier': MC[db][dbprefix['daily']+"_"+config['coll']['supplier']],
                'collection_supplier_info': MC[db][dbprefix['daily']+"_"+config['coll']['supplier_info']],
                'collection_sheets_rules': MC[db][dbprefix['daily']+"_"+config['coll']['sheets_rules']],
                'collection_history': MC[db][dbprefix['daily']+"_"+config['coll']['history']],
                'collection_ilde': MC[db][dbprefix['monthly']+"_"+config['coll']['ilde']],
                'collection_ilde_final': MC[db][config['coll']['ilde_final']],
                'collection_letu': MC[db][dbprefix['monthly']+"_"+config['coll']['letu']],
                'collection_global_links': MC[db][dbprefix['daily']+"_"+config['coll']['global_links']],
                'collection_failed_links': MC[db][dbprefix['daily']+"_"+config['coll']['failed_links']],
                'collection_pagination': MC[db][dbprefix['daily']+"_"+config['coll']['pagination']],
                'collection_ilde_brands': MC[db][dbprefix['daily']+"_"+config['coll']['ilde_brands']],
                'collection_log': MC[db][config['coll']['log']]
            }
