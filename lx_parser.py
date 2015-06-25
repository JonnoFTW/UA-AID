'''
Created on 2 Mar 2015

@author: mack0242
'''

import pymongo
import json
import re
from connection import mongo_uri
import os
from node_import import nodeImport
def signal():
    return {'intersections':[],'links':set()}
from collections import defaultdict
def toDict(i):
    return {j[0]:j[1] for j in map(lambda x: x.split("="),filter(None,i.replace('\n','').split('!')))}
def parseFile(f):
    with open(f) as lx_file:
        s = lx_file.read()
        out = defaultdict(signal)
        chunks = s.split('\n\n')
        for i in chunks:
            pieces = toDict(i)
            if 'S#' in pieces and pieces['S#'] != '0' and pieces['INT'] !='0':
                out[pieces['S#']]['intersections'].append(pieces['INT'])
        for i in chunks:
            pieces = toDict(i)
            if 'SS' in pieces:
                for j,k in filter(lambda x: x[0].startswith('LP'),pieces.items()):
                    if k!='0':
                        out[pieces['SS']]['links'].add(re.split(r'[A-Z]',k)[1])
        return out
class SetEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o,set):
            return list(o)
        json.JSONEncoder.default(self, o)
nodeImport()
os.chdir("D:\\lx_files")
with pymongo.MongoClient(mongo_uri) as client:
        db = client.mack0242
        locations = db['locations']
        for i in os.listdir("."):
            print(i)
            d = parseFile(i)
          #  print json.dumps(d,indent=4,cls=SetEncoder)
            print("-"*30)
            for j,k in d.items():
                int_len= len(k['intersections'])
                out_len = len(k['links'])
                
                if int_len==0 or int_len > 1 or out_len >1:
                    print(j,":",k)
                for m in k['intersections']:
                    for link in k['links']:
                        locations.update(
                                  {'intersection_number':m},
                                  {'$push':{'turns':{'to':link}}},True)
    
