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
			sql = 'SELECT repo_url, initialCount,finalCount FROM growthDelta WHERE actor='+'"'+user[0]+'"'
			impactRows = executeSQL(con,sql)
			impactVector = []
			deltas = []
			for row in impactRows:
				
				deltas.append(row[2]-row[1])
			std = np.std(deltas)	
			sdArray.append(std)		
		print sdArray
		result.std = np.std(sdArray)
		result.mean = np.std(sdArray) 	
		result.min = np.amin(sdArray)			
		return result
	except Exception as e:
		print 'Error in line:'+str(sys.exc_traceback.tb_lineno)
		print e
		pass
		
	finally:

		if con:
			con.close()	

#print "Top 10 impacted repos "+str(getTop10PercentUpcoming())
result = sdLowerBound()
print "Mean and sd of all sds"+str(result.std)+" "+str(result.mean)+" "+str(result.min)