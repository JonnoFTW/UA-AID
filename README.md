Introduction
============

All the files I've written for my PhD. Currently uses DBSCAN from sklearn to perform outlier detection; outliers
are then used to cross check for nearby incidents to identify if outliers do indeed indicate an incident. 
 
I've included all my data import scripts in the top folder. These should probably be more organised to separate data
import from the data analysis. All my raw data is not stored here for obvious reasons.
 
Work To Do
===========
I need to:

* Implement a stream mining algorithm such as d-stream
* Write a server that takes data in from mongodb and then spits out in regular intervals so that it can be fed into a 
client that performs AID.
* Have the data mining be performed on a GPU.
* Perform a literature review of other UA-AID
* Write my thesis