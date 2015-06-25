
import matplotlib.pyplot as plt

from connection import mongo_uri
from pymongo.mongo_client import MongoClient

client = MongoClient(mongo_uri)
db = client.mack0242
collection = db['locations']
cursor = collection.find({'intersection_number':{'$regex':r'TS3\d\d\d'}}) #{'turns':{'$exists':True}}
locations = {i['intersection_number']:i for i in cursor if 'loc' in i}

x,y = zip(*[j['loc']['coordinates'] for i,j in locations.items()])
fig = plt.figure()
ax = fig.add_subplot(111,axisbg='#EEEEEE')

crashes = list(db['crashes'].find({'loc': {
    '$geoWithin': {
        '$box': [
            [138.586, -34.9405],
            [138.616, -34.896]
        ]
     }}}))

print("Crashes", len(crashes))

cx, cy = zip(*[i['loc']['coordinates'] for i in crashes])
plt.scatter(cx, cy, marker='x', c='red')
plt.scatter(x, y)



# for i,j in locations.items():
#     toNode = j['loc']['coordinates']
#     for k in j['neighbours']:
#         fromNode = locations[k]['loc']['coordinates']
#         ax.plot([toNode[0],fromNode[0]],[toNode[1],fromNode[1]])
for i,j in locations.items():
    pos=list((j['loc']['coordinates']))
    plt.annotate(i,xy=pos)
ax.grid(color='white',linestyle='solid')
plt.gca().get_xaxis().get_major_formatter().set_useOffset(False)
plt.gca().get_yaxis().get_major_formatter().set_useOffset(False)
plt.xlabel('X')
plt.ylabel('Y')
print("Showing")
plt.show()
