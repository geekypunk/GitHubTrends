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

def getParsedTime(rawTime):
	try:
		timeStamp = datetime.datetime.strptime(rawTime[:rawTime.rfind('-')],'%Y-%m-%dT%H:%M:%S')
		return timeStamp
	except Exception as e:
		timeStamp = datetime.datetime.strptime(rawTime[:rawTime.rfind(' ')],'%Y/%m/%d %H:%M:%S')
		return timeStamp
		pass

#Get float time after substraction from max possible time(For rescaling)
#To solve curve_fit issues
timeMax = 1346095801.0
def getFloatTime(timeStamp):
		t1 = timeStamp.timetuple()
		return time.mktime(t1)

def func(x, a, b, c):
    return a*x**b + c
def growthCurveByRepoURL(event):

	con = mdb.connect('localhost', 'root', 'root', 'github')
	try:
		cur = con.cursor()	
		sql = 'SELECT repo_watchers,timeStamp from AllEvents WHERE repo_url="'+event.repo_url+'" ORDER BY repo_watchers'
		#print sql
		cur.execute(sql)
		innerRows = cur.fetchall()
		innerX = []
		innerY = []
		allObjsList = []
		for row in innerRows:
			class Object(object):
				pass
			a = Object()
			a.repo_watchers = row[0]
			a.timeStamp = getFloatTime(getParsedTime(row[1]))
			allObjsList.append(a)

		#Sort on decreasing time difference	
		#allObjsList.sort(key = lambda x: x.timeStamp)
		#allObjsList.reverse()
		for obj in allObjsList:
			innerY.append(obj.repo_watchers)
			innerX.append(obj.timeStamp)
		#innerX.sort(reverse=True)
		#innerX = np.array(innerX)	
		#innerX = (innerX/max(innerX))*1000000
		#newX = np.array(innerX)
		#newY = np.array(innerY)
		print event.repo_url
		print innerX
		print innerY
		print "-----------------------------"
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


def getGrowthDelta(growthCurve,timeStamp):
	actualY = growthCurve.Y
	predictedY = growthCurve.AdjY
	actualX = growthCurve.X
	#print "in getGrowthDelta"
	#print actualY
	#print predictedY
	#print actualX
	#print timeStamp
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
	#Selecting top 100 users	
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
				#print "ssup!"
				growthFactor = getGrowthDelta(growthCurve,getFloatTime(a.timeStamp))
				if growthFactor is not 0:
					print "growthFactor="+str(growthFactor)+' on '+a.repo_url+' by '+a.actor
					#if abs(growthFactor) > 10:
					plt.plot(growthCurve.X,growthCurve.Y)
					plt.plot(growthCurve.X,growthCurve.AdjY)
					#plt.xlabel(a.actor+' --> '+a.repo_url+' | impact = '+str(growthFactor), fontsize=10)
					plt.xlabel(a.actor+' --> '+a.repo_url, fontsize=10)
					#plt.text(0.5, 0.5,a.actor +'-->'+,horizontalalignment='center',verticalalignment='center', fontsize=12)
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
