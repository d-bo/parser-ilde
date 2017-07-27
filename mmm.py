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
DB = 'import18'
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



gl = MC[DB].global_links
all = gl.find()

i = 0
for obj in all:
    if obj['_id'] == ObjectId('5953be204a292b3ad0987987'):
        print(i)
        exit()
    gl.delete_one({'_id': ObjectId(obj['_id'])})
    i = i + 1
