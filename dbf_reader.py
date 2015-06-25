from dbfread import DBF
import pymongo
from connection import mongo_uri
import sys
import re
sys.setrecursionlimit(5000)
from gda94towgs84 import gda94Towgs84
allNodes = {}
def findIntersectionNeighbours(root,current):
    root['seen'].add(current)
    for i in allNodes[current]['neighbours']:
        if i not in root['seen']:
            if 'name' in allNodes[i]:
                root['seen'].add(i)
                root['intersection_neighbours'].add(i)
            else:
                findIntersectionNeighbours(root,i)

topDir = "..\\scats_data\\"
print "Loading nodes"
nodes = DBF(topDir+"AMHWY00A_Base.S_2011_nodes.dbf")
def roadNode(x):
    return True #(1400 <= x <= 4999) or x > 11000
for record in nodes:
    descr = record['NODE_DESC']
    nodeId = int(record['N'])
    if roadNode(nodeId):
        coord = gda94Towgs84(54,float(record['X']),float(record['Y']))
        node = {
            'description':descr,
            'loc':{'type':'Point',
                 'coordinates':[
                   coord.dNum2,
                   coord.dNum1
                   ]},
            'neighbours':set(),
            # 'seen':set(),
            # 'intersection_neighbours':set()
        }
        allNodes[record['N']] = node
print "Loading links"
links = DBF(topDir+"AMHWY00A_Base.S_2011_links.dbf")
for record in links:
    a = int(record['A'])
    b = int(record['B'])
    if roadNode(a) and roadNode(b):
        allNodes[record['A']]['neighbours'].add(record['B'])

#print("Linking nodes and links")
#intersections = filter(lambda x: 'name' in x[1],allNodes.items())
#for i,j in intersections:
#    findIntersectionNeighbours(j,i)
print("Inserting")
with pymongo.MongoClient(mongo_uri) as client:
        db = client.mack0242
        locations = db['locations']
        locations.remove({})
        for i,j in allNodes.iteritems():
            locations.insert({
                'node':i,
                'loc':j['loc'],
                'neighbours':list(j['neighbours']),
                'description':j['description']
            })

        print "Added", len(allNodes), "rows"