'''
Created on 3 Mar 2015

@author: mack0242
'''
from __future__ import division
from pycel.excelutil import *
from pycel.excellib import *
import os
from pycel.excelcompiler import ExcelCompiler
from os.path import normpath,abspath

if __name__ == '__main__':
    
    fname = normpath(abspath("D:\\gis_files\\redfearn.xls"))
    
    print "Loading %s..." % fname
    
    # load  & compile the file to a graph, starting from D1
    c = ExcelCompiler(filename=fname)
    
    sheet_name = 'E,N Zne to Latitude & Longitude'
    print "Compiling..., starting from B3"
    sp = c.gen_graph('B3',sheet=sheet_name)
    
  
    
    print "Setting E3 to 54"
    print sp
    sp.set_value(sheet_name+'!E3',54)
      # test evaluation
    print "LAT,LNG is %s,%s" % (sp.evaluate(sheet_name+'!F43'),
                                sp.evaluate(sheet_name+'!P43'))
    