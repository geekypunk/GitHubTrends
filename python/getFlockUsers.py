#!/usr/bin/python

import os
import MySQLdb as mdb
import datetime
import sys, os
import time
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import scipy as sy
import numpy as np  
import pylab as plb  
import shutil
from scipy import polyval, polyfit
from scipy.interpolate import interp1d
from scipy.interpolate import spline
from collections import defaultdict
import itertools as it
import re
import operator
 
#Two formats of timestamp present in the data
def getParsedTime(rawTime):
	try:
		timeStamp = datetime.datetime.strptime(rawTime[:rawTime.rfind('-')],'%Y-%m-%dT%H:%M:%S')
		return timeStamp
	except Exception as e:
		timeStamp = datetime.datetime.strptime(rawTime[:rawTime.rfind(' ')],'%Y/%m/%d %H:%M:%S')
		return timeStamp
		pass

#Get float time 
def getFloatTime(timeStamp):
		t1 = timeStamp.timetuple()
		return time.mktime(t1)


def getCascadeUsers(impactEvent):
	con = mdb.connect('localhost', 'root', 'root', 'github')
	try:
		cur = con.cursor()	
		sql = 'SELECT actor,timeStamp from AllEvents WHERE repo_url="'+impactEvent.repo_url+'"'
		cur.execute(sql)
		innerRows = cur.fetchall()
		innerX = []
		innerY = []
		allObjsList = []
		startTime = impactEvent.timeStamp
		for row in innerRows:
			currentTimeStamp = getFloatTime(getParsedTime(row[1]))
			if(currentTimeStamp> startTime+(24*3600)):
				break
			class Object(object):
				pass
			a = Object()
			a.actor = row[0]
			a.timeStamp = currentTimeStamp
			allObjsList.append(a)
		#Sort objects by timestamp	
		allObjsList.sort(key = lambda a: a.timeStamp)
		userArray = []	
		for obj in allObjsList:

			userArray.append(obj.actor)

		return userArray
		
	except Exception as e:
		
		print 'Error in line:'+str(sys.exc_traceback.tb_lineno)
		print e
		pass
		
	finally:
	
		if con:
			con.close()

#Find the most "socially" close set of users, n indicates the size of the set 
#Here we maintain a map of all possible permutaions of all high profle users, everytime we find a 
#already seen premutation, we increment the count
def getUsersFlockN(commonUsersArray,n):

	try:
		
		combinationMap = defaultdict(int)

		for line in commonUsersArray:
			for pair in it.permutations(set(line), n):
        			combinationMap[tuple(pair)] += 1
        	sortedMap = [(k, combinationMap[k]) for k in sorted(combinationMap, key=combinationMap.get, reverse=True)]	
        	
		return sortedMap
	except Exception as e:
		print 'Error in line:'+str(sys.exc_traceback.tb_lineno)
		print e
		pass
	
#Throws exception if iterator size < n
def printNIterator(list,val):

	n=0
	try:
		for (i,row) in enumerate(list):
			if i > val-1:
				break
			print row
	except Exception as e:
		print 'Error in line:'+str(sys.exc_traceback.tb_lineno)
		print e
		pass		


#Entry Point		
try:
	userFlockSize = int(sys.argv[1])
	recordsTofetch = int(sys.argv[2])
	print "userFlockSize:"+str(userFlockSize)
	print "recordsTofetch:"+str(recordsTofetch)
	con = mdb.connect('localhost', 'root', 'root', 'github')
	cur = con.cursor()	
	#Selecting top 100 users for data pruning	
	cur.execute("SELECT followedUser_login from FollowEvents GROUP BY followedUser_login ORDER BY followedUser_followers DESC ")
	rows = cur.fetchall()
	objList = []
	commonUsersArray = []
	
	for (i,row) in enumerate(rows):
		actor = row[0]
		sql = 'SELECT repo_url,timeStamp,repo_watchers,actor from AllEvents WHERE actor="'+actor+'" AND eventType = "WatchEvent" GROUP BY repo_url'
		cur.execute(sql)
		innerRows = cur.fetchall()	

		for iRow in innerRows:
			class Object(object):
				pass
			impactEvent = Object()
			impactEvent.repo_url = iRow[0]
			impactEvent.timeStamp = getFloatTime(getParsedTime(iRow[1]))
			impactEvent.repo_watchers = iRow[2]
			impactEvent.actor = iRow[3]
			impactStartTime = getFloatTime(getParsedTime(iRow[1]))	
			commonUsersArray.append(getCascadeUsers(impactEvent))
			if i%20 == 0:
				print "Most together users till now"
				iterator = getUsersFlockN(commonUsersArray,userFlockSize)
				printNIterator(iterator,recordsTofetch)
				
	print "Final Map"
	iterator = getUsersFlockN(commonUsersArray,userFlockSize)
	printNIterator(iterator,recordsTofetch)

except Exception as e:
	print 'Error in line:'+str(sys.exc_traceback.tb_lineno)
	print e
	pass
		
finally:
	
	if con:
		con.close()
