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
import math
from scipy import polyval, polyfit
from scipy.interpolate import interp1d
from scipy.interpolate import spline
import operator

def getDBConnection():
	user = "root"
	password = "root"
	databaseName = "github"
	con = mdb.connect('localhost', user, password, databaseName)
	return con
	
def executeSQL(con,sql):
	cursor = con.cursor()
	cursor.execute(sql)	
	return cursor.fetchall()

#Gives top 10 upcoming repos, impacted my high profile watch events
def getTop10PercentUpcoming():
	con = mdb.connect('localhost', 'root', 'root', 'github')
	try:
		cur = con.cursor()
		sql = 'SELECT DISTINCT repo_url FROM growthDelta ORDER BY finalCount - initialCount DESC'
		cur.execute(sql)
		rows = cur.fetchall()
		count = int(len(rows)*0.01)
		print count
		top10 = []
		for i in range(0,count-1):
			top10.append(rows[i])
		print top10	
	except Exception, e:
		print 'Error in line:'+str(sys.exc_traceback.tb_lineno)
		print e
		pass
	finally:
		if con:
			con.close()
		pass
#Gives standard deviation and mean of all the user impactVectors		
def sdLowerBound():
	con = getDBConnection()
	try:
		sql = 'SELECT DISTINCT actor from growthDelta'
		class Object(object):
				pass
		result = Object()
		users = executeSQL(con,sql)
		sdArray = []
		for user in users:
			sql = 'SELECT repo_url, initialCount,finalCount FROM growthDelta WHERE actor='+'"'+user[0]+'" GROUP BY actor,repo_url'
			impactRows = executeSQL(con,sql)
			impactVector = []
			deltas = []

			for row in impactRows:
				url = row[0]
				deltas.append(row[2]-row[1])
			class Object(object):
				pass
			sd = Object()
			sd.actor = user[0]
			sd.url = url
			sd.array = deltas
			std = np.std(deltas)
			sd.std = std
			if std > 0.0:	
				sdArray.append(sd)		
		sdArray.sort(key=operator.attrgetter("std"), reverse=False)
		for obj in sdArray:
			print obj.actor
			print obj.url
			print obj.std
			print obj.array
			print "---------------------------------"
	except Exception as e:
		print 'Error in line:'+str(sys.exc_traceback.tb_lineno)
		print e
		pass
		
	finally:

		if con:
			con.close()	

#print "Top 10 impacted repos "+str(getTop10PercentUpcoming())
result = sdLowerBound()
#print "Mean and sd of all sds"+str(result.std)+" "+str(result.mean)+" "+str(result.min)