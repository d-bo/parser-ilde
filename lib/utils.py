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
                #new_dir = img_dir+str(item['brand'])+"/"
                new_dir = img_dir + "all" + "/"
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
    def insertProductItems(basket, collection, preview_img_link = None):

        """ mongodb insert """

        for item in basket['basket']:
            # is allready in collection ?
            double = collection.find_one({"articul": item['articul']})
            if double is None:
                # insert img link to document
                if preview_img_link is not None:
                    item['image'] = preview_img_link['href']
                print("\n\n img -> mongo document: "+str(item)+"\np_ids: "+str(basket['p_ids'])+"\n")
                _id = collection.insert_one(item).inserted_id
            else:
                print "Double: articul "+item['articul']



    @staticmethod
    def getDbprefix():
        return datetime.strftime(datetime.now(),"%d-%m-%Y")



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
                'collection_letu': MC[db][config['coll']['letu']],
                'collection_global_links': MC[db][config['coll']['global_links']],
                'collection_failed_links': MC[db][config['coll']['failed_links']],
                'collection_pagination': MC[db][config['coll']['pagination']]
            }
        else:
            return {
                'collection_gestori': MC[db][dbprefix+"_"+config['coll']['gestori']],
                'collection_sheets': MC[db][dbprefix+"_"+config['coll']['sheets']],
                'collection_supplier': MC[db][dbprefix+"_"+config['coll']['supplier']],
                'collection_supplier_info': MC[db][dbprefix+"_"+config['coll']['supplier_info']],
                'collection_sheets_rules': MC[db][dbprefix+"_"+config['coll']['sheets_rules']],
                'collection_history': MC[db][dbprefix+"_"+config['coll']['history']],
                'collection_ilde': MC[db][dbprefix+"_"+config['coll']['ilde']],
                'collection_letu': MC[db][dbprefix+"_"+config['coll']['letu']],
                'collection_global_links': MC[db][dbprefix+"_"+config['coll']['global_links']],
                'collection_failed_links': MC[db][dbprefix+"_"+config['coll']['failed_links']],
                'collection_pagination': MC[db][dbprefix+"_"+config['coll']['pagination']]
            }
