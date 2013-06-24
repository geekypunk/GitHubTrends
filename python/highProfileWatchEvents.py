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

#Quadratic for curve fitting
def func(x, a, b, c):
    return a*x**b + c

#Return the predicted values obtained by curve_fit function in scipy
def growthCurveByRepoURL(event):

	con = mdb.connect('localhost', 'root', 'root', 'github')
	try:
		cur = con.cursor()	
		sql = 'SELECT repo_watchers,timeStamp from AllEvents WHERE repo_url="'+event.repo_url+'" ORDER BY repo_watchers'
		cur.execute(sql)
		innerRows = cur.fetchall()
		innerX = []
		innerY = []
		allObjsList = []
		for row in innerRows:
			innerY.append(row[0])
			innerX.append(getFloatTime(getParsedTime(row[1])))
			
		try:
			popt, pcov = curve_fit(func, innerX, innerY,maxfev=10000)
			yAdjusted = func(innerX,popt[0],popt[1],popt[2])
			class Object(object):
				pass
			a = Object()
			a.X = innerX
			a.AdjY = yAdjusted
			a.Y = innerY
			return a
		except Exception, e:
			print e
			print sys.exc_traceback.tb_lineno 	
			pass
		finally:
			pass
	except Exception as e:
		
		print e
		print sys.exc_traceback.tb_lineno 
		pass
		
	finally:
	
		if con:
			con.close()


#Calculates the delta between the predicted and actual number of watchers till 1 hour after a high profile user has started watching
def getGrowthDelta(growthCurve,timeStamp):
	actualY = growthCurve.Y
	predictedY = growthCurve.AdjY
	actualX = growthCurve.X
	effect = 0;
	for x, y ,z in zip(actualY, predictedY,actualX):
		if z > timeStamp and z < timeStamp + 3600:
			if effect == 0:
				growthCurve.startTime = z		
			#print "adding "+str(x-y)
			effect += x - y;
		
	return effect




try:
	
	con = mdb.connect('localhost', 'root', 'root', 'github')
	cur = con.cursor()	
	#Selecting top 100 users for data pruning	
	cur.execute("SELECT followedUser_login from FollowEvents GROUP BY followedUser_login ORDER BY followedUser_followers DESC")
	rows = cur.fetchall()
	objList = []
	for row in rows:
		sql = 'SELECT repo_url,timeStamp,repo_watchers,actor from AllEvents WHERE actor="'+row[0]+'" AND eventType = "WatchEvent" GROUP BY repo_url'
		cur.execute(sql)
		innerRows = cur.fetchall()	
		intialWatchCount=0
		finalWatchCount=0
		actor=""
		for iRow in innerRows:
			
			class Object(object):
				pass
			a = Object()
			a.repo_url = iRow[0]
			a.timeStamp = getParsedTime(iRow[1])
			a.repo_watchers = iRow[2]
			a.actor = iRow[3]
			objList.append(a)		
			growthCurve = growthCurveByRepoURL(a)
			if growthCurve is not None:
				growthFactor = getGrowthDelta(growthCurve,getFloatTime(a.timeStamp))
				if abs(growthFactor) > 10:
					plt.plot(growthCurve.X,growthCurve.Y)
					plt.plot(growthCurve.X,growthCurve.AdjY)
					plt.xlabel(a.actor+' --> '+a.repo_url, fontsize=10)
					plt.axvline(growthCurve.startTime, color='r', linestyle='dashed', linewidth=1)
					plt.legend(['Actual', 'Predicted','impactRegion'], loc='upper left')
					plb.savefig('plotImages/'+a.repo_url[a.repo_url.rfind('/')+1:]+'.png')
					plt.close()

except Exception as e:
	print e
	print sys.exc_traceback.tb_lineno 
	pass
		
finally:
	
	if con:
		con.close()
