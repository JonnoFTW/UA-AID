__author__ = 'mack0242'
import numpy as np
import pymongo
from connection import mongo_uri

import matplotlib.pyplot as plt

with pymongo.MongoClient(mongo_uri) as client:
            db = client.mack0242
            collection = db['crashes']
            readings = list(collection.find({}, {'datetime': 1}))
            dmin = min(readings, key=lambda x: x['datetime'])['datetime'].date()
            dmax = max(readings, key=lambda x: x['datetime'])['datetime'].date()
            hour_list = [t['datetime'].hour for t in readings]
            numbers = np.arange(25)-.5

            plt.xlim(0, 24)
            plt.title("Crashes Per Hour in period: {} - {}\nTotal: {}".format(dmin, dmax, len(readings)))
            plt.ylabel("Count")
            plt.xlabel("Time")
            h = plt.hist(hour_list, bins=numbers)
            plt.xticks(range(24))
            plt.xlim([-1, 24])
            #xticks_pos = [0.65*patch.get_width() + patch.get_xy()[0] for patch in h]
            #plt.xticks(xticks_pos, numbers,  ha='right', rotation=45)
            plt.show()