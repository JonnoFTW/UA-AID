import csv
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from collections import Counter
import numpy as np

site_counter = {'46':Counter(),'332':Counter()}

path = "volumeStore.RURAL_201001_20130902115456.csv"
with open(path) as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        row['rec_date'] = row['rec_date'][1:-1]        
        site_counter[row['site_no']][row['rec_time'][1:3]] += int(row['vehicle_count'])



fig = plt.figure()
cols = {'46':'green','332':'blue'}
for i in site_counter:
    counts = sorted(site_counter[i].items())
    labels,values = zip(*counts)
    indexes = np.arange(len(labels))
    plt.bar(indexes,values,width=1,color=cols[i])
plt.xlabel('Time')
plt.xlim(len(counts))
plt.ylabel('Volume')
plt.title('Road Traffic Volume/hr')
plt.xticks(indexes,labels,rotation="vertical")
plt.show()
