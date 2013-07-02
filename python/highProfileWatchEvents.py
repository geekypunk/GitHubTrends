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
#growthDelta table contains the effects after 1 day the user has started watching. The tables the contains initial and final watcher counts 
# of all repos which have been touched my high profile users, final watcher count being 1 day after this user has started watching 
def getUserRepoImpactVector(user):
	con = mdb.connect('localhost', 'root', 'root', 'github')
	try:
		sql = 'SELECT repo_url, initialCount,finalCount FROM growthDelta WHERE actor='+'"'+user+'"'
		cur.execute(sql)
		impactRows = cur.fetchall()
		impactVector = []
		for row in impactRows:
			class Object(object):
				pass
			a = Object()
			a.repo_url = row[0]
			a.impact = row[2]-row[1]
			a.followers = getFollowerCount(user)
			impactVector.append(a)
				
		return impactVector
	except Exception as e:
		print 'Error in getUserRepoImpactVector'
		print 'Error in line:'+str(sys.exc_traceback.tb_lineno)
		print e
		pass
		
	finally:

		if con:
			con.close()	

def getFollowerCount(user):
	try:
		con = mdb.connect('localhost', 'root', 'root', 'github')
		sql = 'SELECT MAX(followedUser_followers) from FollowEvents WHERE followedUser_login='+'"'+user+'"'
		cur = con.cursor()
		cur.execute(sql)
		return cur.fetchone()[0]
		
	except Exception as e:
		print 'Error in getFollowerCount'
		print 'Error in line:'+str(sys.exc_traceback.tb_lineno)
		print e
		pass
		
	finally:

		if con:
			con.close()	
#Obtain the genuineness of an impact by a user by calculating the standard deviation of his impact on all repos
def getImpactValueOfUser(user):
	try:
		weightVector = getUserRepoImpactVector(user)
		noOfFollowers = getFollowerCount(user)
		impactVector = []
		for weight in weightVector:
			val = weight.impact
			followerCount = weight.followers
			#Taking weighted impact, by number of followers
			impactVector.append(val*followerCount)
		std = np.std(impactVector)
		return std
	except Exception as e:
		print 'Error in getImpactValueOfUser'
		print 'Error in line:'+str(sys.exc_traceback.tb_lineno)
		print e
		pass
		
	finally:
		pass
		
def getDatasetDeviation():
	con = mdb.connect('localhost', 'root', 'root', 'github')
	try:
		cur = con.cursor()
		sql = 'SELECT initialCount,finalCount FROM growthDelta'
		cur.execute(sql)
		impactRows = cur.fetchall()
		effect = []
		for row in impactRows:
			effect.append(row[1]-row[0])
		std = np.std(effect)	
		return std
	except Exception, e:
		print 'Error in getImpactValueOfUser'
		print 'Error in line:'+str(sys.exc_traceback.tb_lineno)
		print e
		pass
	finally:
		if con:
			con.close()
		pass
	
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
		#Sort objects by timestamp	
		allObjsList.sort(key = lambda a: a.X)	
		for obj in allObjsList:
			innerX.append(obj.X)
			innerY.append(obj.Y)
		a.X = np.array(innerX)
		a.Y = np.array(innerY)
		return a
		
	except Exception as e:
		
		print 'Error in line:'+str(sys.exc_traceback.tb_lineno)
		print e
		pass
		
	finally:
	
		if con:
			con.close()


#Calculates the delta between the predicted and actual number of watchers till 1 hour after a high profile user has started watching
def getGrowthDelta(growthCurve,predictCurve):
	actualY = growthCurve.Y
	effect = 0;
	actualX = growthCurve.X
	predictedY = predictCurve.predictY
	timeStamp = growthCurve.impactStartTime
	for x, y ,z in zip(actualY, predictedY,actualX):
		if z > timeStamp and z < timeStamp + (24*3600):
			effect += x - y
			
	return effect

#Get a Predicted curve based on the data till a high profile user has started watching. Using least squares polynomial fit
#We use a degree 2 polynomial as we do not expect much oscillatory growth behaviour
#When the fitting fails it gives a "RankWarning: Polyfit may be poorly conditioned" error
def getPredictCurve(growthCurve):
	try:
		predictX = []
		predictY = []
		class Object(object):
				pass
		predictCurve = Object()
		startTime = growthCurve.impactStartTime
		time = startTime
		print 'startTime:'+str(time)
		xnew = np.linspace(startTime,growthCurve.X.max(),600)
		a, b, c = polyfit(growthCurve.X, growthCurve.Y, 2)
		y_pred = polyval([a, b, c], xnew)
		predictCurve.predictX = xnew   
		predictCurve.predictY = y_pred
		return predictCurve

	except Exception, e:
		print 'Error in line:'+str(sys.exc_traceback.tb_lineno)
		print e
		pass
	finally:
		pass
try:
	print "DataSet deviation ="+str(getDatasetDeviation())
	con = mdb.connect('localhost', 'root', 'root', 'github')
	cur = con.cursor()	
	#Selecting top 100 users for data pruning	
	cur.execute("SELECT followedUser_login from FollowEvents GROUP BY followedUser_login ORDER BY followedUser_followers DESC")
	rows = cur.fetchall()
	objList = []
	for row in rows:
		actor = row[0]
		sql = 'SELECT repo_url,timeStamp,repo_watchers,actor from AllEvents WHERE actor="'+actor+'" AND eventType = "WatchEvent" GROUP BY repo_url'
		cur.execute(sql)
		innerRows = cur.fetchall()	
		for iRow in innerRows:
			class Object(object):
				pass
			a = Object()
			a.repo_url = iRow[0]
			a.timeStamp = getParsedTime(iRow[1])
			a.repo_watchers = iRow[2]
			a.actor = iRow[3]
			objList.append(a)	
			impactStartTime = getFloatTime(getParsedTime(iRow[1]))	
			growthCurve = growthCurveByRepoURL(a)
			
			if growthCurve is not None:
				#Setting the timeStamp when the user started watching
				growthCurve.impactStartTime = impactStartTime
				predictCurve = getPredictCurve(growthCurve)
				growthFactor = getGrowthDelta(growthCurve,predictCurve)
				
				if abs(growthFactor) > 10:
					#To decide if the user's influence is legit
					#TODO Decide on the value in the if condition
					if getImpactValueOfUser(actor) < 10:  
						print growthCurve.X
						print growthCurve.Y
						print growthCurve.impactStartTime
						plt.plot(growthCurve.X,growthCurve.Y,marker='o')
						#plt.plot(growthCurve.X,growthCurve.AdjY,'--')
						
						print predictCurve.predictY
						plt.plot(predictCurve.predictX,predictCurve.predictY,'--')
						plt.xlabel(a.actor+' --> '+a.repo_url+'| impact='+str(getImpactValueOfUser(actor)), fontsize=10)
						plt.axvline(growthCurve.impactStartTime, color='r', linestyle='dashed', linewidth=0.5)
						plt.axvline(growthCurve.impactStartTime+24*3600, color='r', linestyle='dashed', linewidth=0.5)
						plt.legend(['Actual', 'Predicted','impactStart','impactEnd'], loc='upper left')
						plb.savefig('currentGeneratedCurves/'+a.repo_url[a.repo_url.rfind('/')+1:]+'.png')
						plt.close()

except Exception as e:
	print 'Error in line:'+str(sys.exc_traceback.tb_lineno)
	print e
	pass
		
finally:
	
	if con:
		con.close()