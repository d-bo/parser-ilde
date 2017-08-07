# -*- coding: utf-8 -*-

import os
import csv
import socket
import urllib2
from PIL import Image
import urllib, cStringIO
from datetime import datetime
from pymongo import MongoClient

class Utils:

    """ Class Utils """



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
    def extractImg(doc, img_dir):

        """ json extract image -> save in img_dir """

        for item in doc:
            if 'image' in item:
                url = "http://static.iledebeaute.ru"+item['image']
                url = url.replace('156', '500')
                url = url.replace('257', '500')
                try:
                    file = cStringIO.StringIO(urllib2.urlopen(url, timeout=20).read())
                except urllib2.HTTPError as err:
                    print("Cannot open image url")
                    continue
                except socket.timeout as err:
                    print 'X SOCKET TIMEOUT ' + str(err)
                    continue

                img = Image.open(file)
                new_dir = img_dir + "/"
                if not os.path.exists(new_dir):
                    os.makedirs(new_dir)
                new_file = new_dir+str(item['articul'])+".jpg"
                if os.path.isfile(new_file) is not True:
                    print("Image saved url: "+url)
                    img.save(new_file)
                else:
                    print("Image allready exists: "+new_file)

            else:
                print("\nNO IMAGE IN BASKET")



    @staticmethod
    def insertProductItems(basket, cpool, preview_img_link = None):

        """ mongodb insert """
        collection = cpool['collection_ilde']
        collection_final = cpool['collection_ilde_final']

        for item in basket['basket']:
            # is allready in final collection ?
            double = collection_final.find_one({"articul": item['articul']})
            # document into price collection
            price_doc = {
                'articul': item['articul'],
                'p_price': item['p_price'],
                'p_original_price': item['p_original_price'],
                'brand': item['brand'],
                'product_id': item['product_id']
            }
            # gestori match by articul check
            gestori = cpool['collection_gestori']
            match_articul = gestori.find_one({'Artic': item['articul']})

            if match_articul is not None:
                print("Match articul: ", item['articul'])
                cod_good = match_articul['Cod_good']
                #print("Match articul: ", item['articul'], list(match_articul))

            if double is None:
                if 'cod_good' in locals():
                    item['gestori'] = cod_good
                # insert img link to document
                if preview_img_link is not None:
                    item['image'] = preview_img_link['href']
                print("\n\n img -> mongo document: "+str(item)+"\np_ids: "+str(basket['p_ids'])+"\n")

                # insert price
                price_id = collection.insert_one(price_doc).inserted_id

                # final collection
                del item['p_price']
                del item['p_original_price']
                _id = collection_final.insert_one(item).inserted_id
            else:
                # update final
                if 'cod_good' in locals():
                    collection_final.find_one_and_update({'articul': item['articul']}, {'$set': {'gestori': cod_good}})
                price_id = collection.insert_one(price_doc).inserted_id
                print "Double: articul "+item['articul']



    @staticmethod
    def getDbprefix():
        return {
            'monthly': datetime.strftime(datetime.now(),"%m-%Y"),
            'daily': datetime.strftime(datetime.now(),"%d-%m-%Y")
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
                'collection_ilde_brands': MC[db][config['coll']['ilde_brands']]
            }
        else:
            return {
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
                'collection_ilde_brands': MC[db][dbprefix['daily']+"_"+config['coll']['ilde_brands']]
            }
