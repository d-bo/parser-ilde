# -*- coding: utf-8 -*-

import os
import csv
import json
import pipes
import subprocess
import pandas as pd
from datetime import datetime
from bson.objectid import ObjectId
from flask_compress import Compress
from werkzeug.utils import secure_filename
from pymongo import MongoClient, ReturnDocument
from flask_debugtoolbar import DebugToolbarExtension
from flask import Flask, flash, render_template, request, redirect

from lib.filters import Filters
from lib.utils import Utils



# current script dir
script_dir = os.path.dirname(os.path.abspath(__file__))



# COLLECTIONS
# work db
DB = 'import17'
# client
MC = MongoClient('mongodb://localhost:27017/')
# gestery_m global
collection = MC[DB].gestery_m
# parsed excel sheets
collection_sheets = MC[DB].sheets
# supplier collection
collection_supplier = MC[DB].supplier_test
# sheet rules
collection_sheets_rules = MC[DB].sheets_rules
# history / logs
collection_history = MC[DB].history
# suppliers
collection_supplier_info = MC[DB].supplier_info



letu = MC[DB].letu_products_17_07
gest = MC[DB].gestery_m1
all = letu.find()

# letu match
i = 0
m = 0
for obj in all:
    g = gest.find_one({"Artic": obj['articul']})
    if g is not None:
        print(g['Name_e']+" ; "+obj['name'])
        m = m + 1
    i = i + 1

print("Total: "+str(i))
print("Match: "+str(m))

# ilde match
ilde = MC[DB].products
all = ilde.find()

"""
i = 0
m = 0
for obj in all:
    g = gest.find_one({"Artic": obj['articul']})
    if g is not None:
        print(g['Name_e']+" ; "+obj['pn'])
        m = m + 1
    i = i + 1
"""

#print("Total: "+str(i))
#print("Match: "+str(m))
