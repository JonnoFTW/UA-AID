__author__ = 'mack0242'

import matplotlib.pyplot as plt
from dbfread import DBF
from time import time
t0 = time()
locations = {}
links = []
topDir = "..\\scats_data\\"
nodes = DBF(topDir+"AMHWY00A_Base.S_2011_nodes.dbf")
out = ['Zone Centroid Connector','Walk Link']
print "Loading nodes"
for record in nodes:
    nodeId = int(record['N'])
    if (1400 <= nodeId <= 4999) or nodeId > 11000:
        locations[record['N']] = {'x':float(record['X']),
                              'y':float(record['Y']),
                              'descr':record['NODE_DESC']
        }
print len(locations)
print "Loading links"
connectors = DBF(topDir+"AMHWY00A_Base.S_2011_links.dbf")
for record in connectors:
    a = record['A']
    b = record['B']
    d = record['LINK_DESC']
    if int(record['LINK_TYPE']) < 9 and all(map(lambda x: 1400 <= int(x)<=4999,[a,b])):
        links.append((a, b, d))
print "Plotting"
x,y = zip(*[(j['x'], j['y']) for i, j in locations.iteritems()])
print "Total:", time()-t0
fig = plt.figure()
ax = fig.add_subplot(111,axisbg='#EEEEEE')
plt.scatter(x,y)

for i in links:
    fromNode = locations[i[0]]
    toNode   = locations[i[1]]
    ax.plot([toNode['x'], fromNode['x']], [toNode['y'], fromNode['y']])
for i, j in locations.iteritems():
    if j['descr'].startswith('TS'):
        pos = (j['x'], j['y'])
        plt.annotate(i, xy=pos)
ax.grid(color='white', linestyle='solid')
plt.xlabel('X')
plt.ylabel('Y')
print("Showing")
plt.show()
