#!/usr/bin/python2.7

import csv
import pymongo
from connection import mongo_uri
def doImport():
    with pymongo.MongoClient(mongo_uri) as client:
        db = client.mack0242
        locations = db['locations']
        locations.remove({})
       
        path = "..\\scats_data\\Adelaide Intersections V2.csv"
        with open(path) as f:
            r=0
            reader = csv.DictReader(f)
            for row in reader:
                doc = {
                    'loc':{'type':'Point','coordinates':[
                               float(row['Longitude']),
                               float(row['Latitude'])
                                ]}
                }
                for i in ['Intersection_Number','Type','Description','TG_Number','Type_Acc']:
                    if row[i].strip():
                        doc[i.lower()] = row[i]
                locations.insert(doc)
                r+=1
            print("Rows inserted:",r)
        
if __name__=="__main__":
    doImport()