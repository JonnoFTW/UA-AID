#!/usr/bin/python
# # SCATS Data mongo import script
# # @author Jonathan Mackenzie
# # @email jonathan.mackenzie@flinders.edu.au
# #
# # This script will import SCATS traffic data
# # into mongodb using the following format for each 
# # document:
# # 

{
    "datetime": "2013-06-01T00:00:00Z", 
    "site_no": "3060", 
    "readings": [
        {
            "vehicle_count": 2, 
            "sensor": "8"
        }, 
        {
            "vehicle_count": 0, 
            "sensor": "16"
        }, 
        #....
    ]
}
import csv
import time
import datetime
import json
from bson import json_util
import pymongo
from connection import mongo_uri

time_format = "%H:%M:%S"
date_format = "%Y-%m-%d"
converters = {'site_no': str ,
              'rec_date': lambda x: datetime.datetime.strptime(x[1:-1], date_format).date(),
              'rec_time': lambda x: datetime.datetime.strptime(x[1:-1], time_format).time(),
              'flow_period': int,
              'vehicle_count': int,
              'detector':str,
              'data_owner':str
              }
paths = ["volumeStore.RURAL_201001_20130902115456.csv"]
# path = "D:\\volumeStore.ACC_201306_20130819113933.updated.csv"
i = 0
r = 0
client = pymongo.MongoClient(mongo_uri)
db = client.trafficdata
# readings = db[path.split('.')[1]]
readings = db['readings']
start = time.clock()
readings.remove({})
readings.ensure_index({'site_no': pymongo.ASCENDING})
readings.ensure_index({'datetime': pymongo.ASCENDING})
readings.ensure_index({'site_no': pymongo.ASCENDING, 'datetime': pymongo.ASCENDING})

for path in paths:
    with open(path) as csvfile:
        document = {'datetime': None, 'site_no': None}
        reader = csv.DictReader(csvfile)
        for row in reader:
            row = {k: converters[k](v) for k, v in row.items()}
            dt = datetime.datetime.combine(row['rec_date'], row['rec_time'])
            reading = {
                'sensor': row['detector'],
                'vehicle_count': row['vehicle_count']
            }
            if dt != document['datetime'] or row['site_no'] != document['site_no']:
                # we are at a new time or site reading, insert the old and make a new one
                if document['site_no'] is not None:
                    #  print json.dumps(document,indent=4,default=json_util.default)
                    readings.insert_one(document, w=0)
                    # don't wait for the insert to complete
                    r += 1
                document = {
                    'datetime': dt,
                    'site_no':  row['site_no'],
                    'readings': [reading]
                }
            elif document['datetime'] is not None:
                document['readings'].append(reading)
            i += 1
            if i % 100000 == 0:
                print("rows:", "{:,}".format(i))

print("Took: {:,} seconds\nProcessed {:,} rows\nInserted {:,} documents".format(time.clock() - start, i, r))

