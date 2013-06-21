import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import scipy as sy
import pylab as plb  
import MySQLdb as mdb
import datetime
import numpy as np
import time

def func(x, a, b, c):
    return a*x**b + c

con = mdb.connect('localhost', 'root', 'root', 'github')
try:
	
	cur = con.cursor()	
	sql = "SELECT DISTINCT repo_url from AllEvents"
	cur.execute(sql)
	rows = cur.fetchall()
	allCurvesX = []
	allCurvesY = []
	objList = []
	for row in rows:	
		sql = 'SELECT repo_watchers,timeStamp from AllEvents WHERE repo_url="'+row[0]+'"'
		cur.execute(sql)
		innerRows = cur.fetchall()
		innerX = []
		innerY = []
		for innerRow in innerRows:
			innerX.append(innerRow[0])
			rawTime = innerRow[1]	
			try:
				timeStamp = datetime.datetime.strptime(rawTime[:rawTime.rfind('-')],'%Y-%m-%dT%H:%M:%S')
			except Exception as e:
				timeStamp = datetime.datetime.strptime(rawTime[:rawTime.rfind(' ')],'%Y/%m/%d %H:%M:%S')
				pass
			t1 = timeStamp.timetuple()
			innerY.append(time.mktime(t1))
		try:
			popt, pcov = curve_fit(func, innerX, innerY)
			yAdjusted = func(innerX,popt[0],popt[1],popt[2])
			allCurvesX.append(innerX)
			allCurvesY.append(yAdjusted)
			class Object(object):
   				pass
			a = Object()
			a.repo_url = row[0]
			a.X = innerX
			a.AdjY = yAdjusted
			a.Y = innerY
			objList.append(a)
			print a.repo_url
		except Exception, e:
			pass
		finally:
			pass
	optimalX = [];	
	for obj in objList:
		print a.repo_url
					
except Exception as e:
	print e
	pass
		
finally:
	
	if con:
		con.close()

