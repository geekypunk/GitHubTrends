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

#Quadratic for curve fitting y = a(x)^b +c
def func(x, a, b, c):
    return a*x**b + c

#This function returns the consolidated impact vector of a user, representing his impact on all the repos he started watching
#growthDelta table contains the effects after 1 day the user has started watching 
def getUserRepoImpactVector(user):
	con = mdb.connect('localhost', 'root', 'root', 'github')
	try:
		for user in users:
			sql = 'SELECT repo_url, initialCount,finalCount FROM growthDelta WHERE actor='+'"'+user+'"'
			cur.execute(sql)
			impactRows = cur.fetchall()
			#Calculate standard deviation in impact
			impactVector =[]
			for row in impactRows:
				class Object(object):
					pass
				a = Object()
				a.repo_url = row[0]
				a.impact = row[2]-row[1]
				impactVector.append(a)
				
			return impactVector
	except Exception as e:
		print e
		print sys.exc_traceback.tb_lineno 
		pass
		
	finally:

		if con:
			con.close()	
#Obtain the genuineness of an impact by a user by calculating the standard deviation of his impact on all repos
def getImpactValueOfUser(user):
	con = mdb.connect('localhost', 'root', 'root', 'github')
	try:
		weightVector = getUserRepoImpactVector(user)
		impactVector = []
		for weight in weightVector:
			impactVector.append(weight.impact)
		std = np.std(weightVector)
		return std
	except Exception as e:
		print e
		print sys.exc_traceback.tb_lineno 
		pass
		
	finally:

		if con:
			con.close()	

#Return the predicted values obtained by curve_fit function in scipy
def growthCurveByRepoURL(event):

	con = mdb.connect('localhost', 'root', 'root', 'github')
	try:
		cur = con.cursor()	
		sql = 'SELECT repo_watchers,timeStamp from AllEvents WHERE repo_url="'+event.repo_url+'"'
		cur.execute(sql)
		innerRows = cur.fetchall()
		innerX = []
		innerY = []
		allObjsList = []
		for row in innerRows:
			class Object(object):
				pass
			a = Object()
			a.Y = row[0]
			a.X = getFloatTime(getParsedTime(row[1]))
			allObjsList.append(a)
		#Sort objects bu timestamp	


		allObjsList.sort(key = lambda a: a.X)	
		i=0
		firstCount = 0
		finalCount = 0
		for obj in allObjsList:
			if i == 0:
				firstWatch = obj.X
				firstCount = obj.Y
				i = i+1
			if obj.X > firstWatch+24*3600:
				finalCount = obj.Y	
			innerX.append(obj.X)
			innerY.append(obj.Y)
		if finalCount is not 0:	
			sql = 'INSERT into growthDelta VALUES('+'"'+event.repo_url+'","'+event.actor+'"'+','+str(firstCount)+','+str(finalCount)+')'
			cur.execute(sql)
			con.commit()
		print "---------------------"
		print event.repo_url
		print innerX
		print innerY
	
		try:
			popt, pcov = curve_fit(func, innerX, innerY,maxfev=10000)
			#popt is the coeffcient a,b,c of the function func
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
	i=0
	for x, y ,z in zip(actualY, predictedY,actualX):
		if z > timeStamp and z < timeStamp + 3600:
			if i == 0:
				growthCurve.startTime = z	
				i = i+1	
			#print "adding "+str(x-y)
			effect += x - y;
		
	return effect

def getDeviationOfRepo():
	try:
		sql = 'SELECT INTO '
	except Exception, e:
		print e
		print sys.exc_traceback.tb_lineno 
		pass
	finally:
		pass


try:
	
	con = mdb.connect('localhost', 'root', 'root', 'github')
	cur = con.cursor()	
	#Selecting top 100 users for data pruning	
	cur.execute("SELECT followedUser_login from FollowEvents GROUP BY followedUser_login ORDER BY followedUser_followers DESC")
	rows = cur.fetchall()
	objList = []
	for row in rows:
		actor = row[0]
		sql = 'SELECT repo_url,timeStamp,repo_watchers,actor from AllEvents WHERE actor="'+actor+'" AND eventType = "WatchEvent" GROUP BY repo_url'
		print sql
		cur.execute(sql)
		innerRows = cur.fetchall()	
		intialWatchCount=0
		finalWatchCount=0
		i=0
		for iRow in innerRows:
			
			class Object(object):
				pass
			a = Object()
			a.repo_url = iRow[0]
			a.timeStamp = getParsedTime(iRow[1])
			a.repo_watchers = iRow[2]
			a.actor = iRow[3]
			objList.append(a)	
			if i==0:
				intialWatchCount = iRow[2]	
			growthCurve = growthCurveByRepoURL(a)
			if growthCurve is not None:
				growthFactor = getGrowthDelta(growthCurve,getFloatTime(a.timeStamp))
				
				if abs(growthFactor) > 10:
					#To decide if the user's influence is legit
					#TODO Decide on the value in the if condition
					if getImpactValueOfUser(actor) < 10:  
						plt.plot(growthCurve.X,growthCurve.Y)
						plt.plot(growthCurve.X,growthCurve.AdjY)
						plt.xlabel(a.actor+' --> '+a.repo_url, fontsize=10)
						plt.axvline(growthCurve.startTime, color='r', linestyle='dashed', linewidth=0.5)
						plt.axvline(growthCurve.startTime+24*3600, color='r', linestyle='dashed', linewidth=0.5)
						plt.legend(['Actual', 'Predicted','impactStart','impactEnd'], loc='upper left')
						plb.savefig('currentGeneratedCurves/'+a.repo_url[a.repo_url.rfind('/')+1:]+'.png')
						plt.close()

except Exception as e:
	print e
	print sys.exc_traceback.tb_lineno 
	pass
		
finally:
	
	if con:
		con.close()