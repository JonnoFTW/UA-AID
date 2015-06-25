
__author__ = 'mack0242'

import pymongo
from connection import mongo_uri
from sklearn.cluster import DBSCAN
from sklearn import metrics
import matplotlib.pyplot as plt
from matplotlib import ticker
import matplotlib.dates as md

from sklearn.metrics.pairwise import euclidean_distances
from sklearn.preprocessing import scale
import datetime as dt
import numpy as np
#import pyopencl.array as cla

def getNearbyAccidents(point_time, site):
    with pymongo.MongoClient(mongo_uri) as client:
        db = client.mack0242
        location = db['locations'].find_one({'intersection_number': 'TS'+site})
        crash_collection = db['crashes']
        delta = dt.timedelta(minutes=30)
        crashes = crash_collection.find({
            'datetime': {
                '$gte': point_time - delta,
                '$lte': point_time + delta
            },
            'loc': {
                '$nearSphere': {
                    '$geometry': location['loc'], '$maxDistance': 200
                },

            }
        })
    return crashes

def secondsAfterMidnight(x):
    return x.hour*60*60 + x.minute*60 + x.second
def getData():
    print("Fetching Data")
    site_ids = ['3004']
    site = {'intersection_number': {'$in': ['TS'+i for i in site_ids]}}
    locations = {}
    with pymongo.MongoClient(mongo_uri) as client:

            db = client.mack0242
            collection = db['ACC_201306_20130819113933']
            readings = collection.find(
                {
                    'readings': {
                        '$elemMatch': {'vehicle_count': {'$lt': 2000}}
                    },
                    'site_no': {'$in': site_ids},
               #  'datetime':{}
               '$where': 'this.datetime.getUTCDay()>2 && this.datetime.getUTCDay()<6'
                 })
            locs = db['locations']
            location = locs.find(site)
            for i in location:
                locations[i['description'].split()[0][2:]] = i

    #readings_array = np.empty(readings.count(True), dtype=cla.vec.float2)#2+len(readings[0]['readings'])])
    readings_array = np.empty([readings.count(True), 2], dtype=np.float)
    #  turn readings into an np array
    # of samples x features
    readings = list(readings)
    for c, i in enumerate(readings):
        # readings_array[c][0] = locations[i['site_no']]['loc']['coordinates'][0]
        # readings_array[c][1] = locations[i['site_no']]['loc']['coordinates'][1]
        readings_array[c][1] = int(sum([j['vehicle_count'] for j in i['readings'] if j['vehicle_count'] < 2000]))

        #readings_array[c][0] = int(i['datetime'].strftime("%s"))
        readings_array[c][0] = secondsAfterMidnight(i['datetime'])
        # for j,k in enumerate(i['readings']):
        #     readings_array[c][2+j] = k['vehicle_count']
    print("readings:", len(readings_array))
    # np.set_printoptions(threshold='nan')
    # print readings_array
    return readings_array, locations, readings

def cluster(x):
    dbscan = DBSCAN(eps=x[0], min_samples=x[1], metric='precomputed').fit(x[2])
    count = len(set(dbscan.labels_))
   # print "eps={},min_samples={},labels={}".format(x[0], x[1], count)
    return x[0], x[1], dbscan.labels_, count, dbscan.core_sample_indices_

if __name__ == "__main__":
    #p = Pool(8)
    readings_array, locations, readings = getData()

    scaled_readings = scale(readings_array, copy=True)

    distances = euclidean_distances(scaled_readings, scaled_readings)
    print("Clustering")
    #result = p.map(cluster, [(eps, ms, distances) for eps in xrange(20, 500) for ms in xrange(3, 200)])

    eps, j, labels, label_count, indices = cluster((0.2, 7, distances))

    unique_labels = set(labels)
    print("eps=", eps)
    print("min_samples=", j)
    core_samples_mask = np.zeros_like(labels, dtype=bool)
    core_samples_mask[indices] = True
    print('Clusters:', len([i for i in unique_labels if i >= 0]))
    noise = 0
    for i in labels:
        if i == -1:
            noise += 1
    print(labels)
    cluster_count = label_count
    if noise != 0:
        cluster_count -= 1
    colors = plt.cm.Spectral(np.linspace(0, 1, len(unique_labels)))
    for k, col in zip(unique_labels, colors):
        if k==-1:
            col = 'k'
        class_member_mask = (labels == k)
        xy = readings_array[class_member_mask & core_samples_mask]
        plt.plot(xy[:,0],xy[:,1], 'o', markerfacecolor=col, markeredgecolor='k')
        xy = readings_array[class_member_mask & ~core_samples_mask]
        plt.plot(xy[:,0],xy[:,1], 'o', markerfacecolor=col, markeredgecolor='k')
    plt.title('Clusters: {},points:{}, noise: {},eps: {}, minpts: {}'.format(cluster_count, len(readings_array), noise, eps, j))
    outliers = np.where(labels == -1)
    print("Noise at indexes:", outliers[0])
    for i in outliers[0]:
        print("Outlier at:", readings[i]['datetime'])
        # find the nearby accidents at these times
        print("Nearby crashes:")
        for crash in getNearbyAccidents(readings[i]['datetime'], readings[i]['site_no']):
            print(crash)
    ax = plt.gca()

    dates = [dt.datetime.fromtimestamp(ts[0]) for ts in readings_array]
    ticks = ax.get_xticks().tolist()
    ax.grid(True)
    ax.xaxis.set_ticks(np.arange(0, 24*3600+1, 3600))
    ax.get_xaxis().set_major_formatter(ticker.FuncFormatter(lambda x, y: int(int(x)/(60*60))))
    plt.ylabel("Total Traffic Volume")
    plt.xlabel("Time (hours)")
    plt.show()
