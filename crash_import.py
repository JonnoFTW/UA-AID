__author__ = 'mack0242'

import csv
import pymongo
from connection import mongo_uri
from pyproj import Proj, transform
import datetime


def trim_leading(x):
    try:
        if len(x) > 1:
            return int(x.lstrip("0"))
        return int(x)
    except:
        return -1


def parse_float(x):
    try:
        return float(x)
    except:
        return float(-1)

converters = {
    'Date': lambda x: datetime.datetime.strptime(x, "%d/%m/%Y").date(),
    'Time': lambda x: datetime.datetime.strptime(x, "%I:%M %p").time(),
    'Involves_4WD': lambda x: x.lower() == 'y',
    'Area_Speed': trim_leading,
    'RRD': parse_float,
    'Total_Damage': trim_leading,
    'Total_Vehicles_Involved': trim_leading
}

def do_import():
    with pymongo.MongoClient(mongo_uri) as client:
        db = client.mack0242
        locations = db['crashes']
        locations.remove({})
#        locations.ensure_index({'loc': "2dsphere"})
   #     locations.ensure_index({'datetime': pymongo.ASCENDING})

        p1 = Proj(init='epsg:3107')
        p2 = Proj(init='epsg:4326')

        path = "../scats_data/crash_data/exported_csv.csv"
      #  out_path = "..\\scats_data\\crash_data\\adelaide_reported_crash_data_2006to2014_converted.csv"

        with open(path) as f: #, open(out_path, 'w') as fout:
            r = 0
            reader = csv.DictReader(f)
            print(reader.fieldnames)
            # writer = csv.DictWriter(fout, fieldnames=reader.fieldnames, lineterminator='\n')

            for row in reader:
                if row['ACCLOC_X']:
                    try:
                        x, y = transform(p1, p2, float(row['ACCLOC_X']), float(row['ACCLOC_Y']))
                    except:
                        print(row)
                        exit(1)
                    row['loc'] = {'type': 'Point', 'coordinates': [x, y]}
                    for i, j in converters.items():
                        row[i] = j(row[i])
                    row['datetime'] = datetime.datetime.combine(row['Date'], row['Time'])
                    del row['ACCLOC_X']
                    del row['ACCLOC_Y']
                    del row['Date']
                    del row['Time']
                    del row['Year']
                    del row['DayName']
                    try:
                        locations.insert(row)
                        r += 1
                    except Exception as e:
                        print(e)
                        print (row)
                        exit(1)

            print("Rows inserted:", r)

if __name__ == "__main__":
    import time
    start = time.clock()
    do_import()
    print("Took: ", time.clock() - start, "s")
