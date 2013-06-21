#!/usr/bin/python

import os
import MySQLdb as mdb
import datetime
import sys, os
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import scipy as sy
import pylab as plb  

try:
	con = mdb.connect('localhost', 'root', 'root', 'github')
	cur = con.cursor()	
	#Selecting top 100 users	
	cur.execute("SELECT followedUser_login from FollowEvents GROUP BY followedUser_login ORDER BY followedUser_followers DESC")
	rows = cur.fetchall()
	objList = []
	for row in rows:
	
		#Watch events by popular users
		sql = 'SELECT repo_url,timeStamp,repo_watchers,actor from AllEvents WHERE actor="'+row[0]+'" AND eventType = "WatchEvent" GROUP BY repo_url'
		cur.execute(sql)
		innerRows = cur.fetchall()	
		intialWatchCount=0
		finalWatchCount=0
		actor=""
		for iRow in innerRows:
			intialWatchCount = iRow[2]
			rawTime = iRow[1]
			actor = iRow[3];
			repo_url = iRow[0]
			try:
				timeStamp1 = datetime.datetime.strptime(rawTime[:rawTime.rfind('-')],'%Y-%m-%dT%H:%M:%S')
			except Exception as e:
				timeStamp1 = datetime.datetime.strptime(rawTime[:rawTime.rfind(' ')],'%Y/%m/%d %H:%M:%S')
				pass
			sql = 'SELECT repo_watchers,timeStamp from AllEvents WHERE repo_url="'+repo_url+'" ORDER BY repo_watchers';
			print sql
			cur.execute(sql)
			row2 = cur.fetchall()
			countArray = []
			count =0;	
			innerX = [];
			innerY = [];
			for irow in row2:
				print "For Start"
				rawTime = irow[1]
				watcherCount = irow[0]
				try:
					timeStamp2 = datetime.datetime.strptime(rawTime[:rawTime.rfind('-')],'%Y-%m-%dT%H:%M:%S')
				except Exception as e:
					timeStamp2 = datetime.datetime.strptime(rawTime[:rawTime.rfind(' ')],'%Y/%m/%d %H:%M:%S')
					pass
				#Events after the popular user started watching, Time Delta = 5 mins
				if timeStamp2 > timeStamp1 and timeStamp2 < timeStamp1 + datetime.timedelta(minutes=60):
					print "appending"
					innerX.append(timeStamp2)
					innerY.append(watcherCount) 

				elif timeStamp2 > timeStamp1 and timeStamp2 > timeStamp1 + datetime.timedelta(minutes=60):
					growth = irow[0]-intialWatchCount
					eventType = ""
					sql = 'INSERT INTO repoGrowthAll VALUES('+'"'+mdb.escape_string(iRow[0])+'","'+actor+'",'+str(intialWatchCount)+','+str(irow[0])+','+str(growth)+',"'+eventType+'"'+',"'+str(timeStamp1)+'"'+',"'+str(timeStamp2)+'")'
					class Object(object):
   						pass
					a = Object()
					a.X = innerX
					a.Y = innerY
					a.repo_url = repo_url
					print a.X
					print a.Y
					print a.repo_url	
					print "--------------------------elif"
					cur.execute(sql)
					con.commit()
					break	
				class Object(object):
   					pass
				a = Object()
				a.X = innerX
				a.Y = innerY
				a.repo_url = repo_url
				print a.X
				print a.Y
				print a.repo_url	
				print "--------------------------Out"
							
				
		
except Exception as e:
	print e
	print sys.exc_traceback.tb_lineno 
	pass
		
finally:
	
	if con:
		con.close()
