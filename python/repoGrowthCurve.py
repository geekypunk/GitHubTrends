#!/usr/bin/python

from __future__ import division
import os
import MySQLdb as mdb
import datetime

try:
	con = mdb.connect('localhost', 'root', 'root', 'github')
	cur = con.cursor()	
	sql = "SELECT DISTINCT repo_url from AllEvents"
	cur.execute(sql)
	rows = cur.fetchall()
	for row in rows:
		repo_url = row[0]
		min_sql = 'SELECT repo_watchers,timeStamp from AllEvents WHERE repo_url='+'"'+repo_url+'"'+' ORDER BY repo_watchers LIMIT 1'	
		max_sql = 'SELECT repo_watchers,timeStamp from AllEvents WHERE repo_url='+'"'+repo_url+'"'+' ORDER BY repo_watchers DESC LIMIT 1'
		#print min_sql
		#print max_sql
		cur.execute(min_sql)
		minRow = cur.fetchone()
		minRepoWatchers = minRow[0]
		minTimeStamp = minRow[1]
		try:
			minTimeStampNew = datetime.datetime.strptime(minTimeStamp[:minTimeStamp.rfind('-')],'%Y-%m-%dT%H:%M:%S')
		except Exception as e:
			#print rawTime
			minTimeStampNew = datetime.datetime.strptime(minTimeStamp[:minTimeStamp.rfind(' ')],'%Y/%m/%d %H:%M:%S')
		cur.execute(max_sql)
		maxRow = cur.fetchone()
		maxRepoWatchers = maxRow[0]
		maxTimeStamp = maxRow[1]
		try:
			maxTimeStampNew = datetime.datetime.strptime(maxTimeStamp[:maxTimeStamp.rfind('-')],'%Y-%m-%dT%H:%M:%S')
		except Exception as e:
			#print rawTime
			maxTimeStampNew = datetime.datetime.strptime(maxTimeStamp[:maxTimeStamp.rfind(' ')],'%Y/%m/%d %H:%M:%S')
		watchersDelta = maxRepoWatchers - minRepoWatchers 	
		timeDelta = maxTimeStampNew - minTimeStampNew	
		print watchersDelta
		print maxTimeStampNew
		print minTimeStampNew
		print timeDelta.seconds
		print "------------------------------"
		if timeDelta.seconds >0 : 
			dyBydx = watchersDelta/timeDelta.seconds
			print dyBydx
		
		
except Exception as e:
	print e
	pass
		
finally:
	
	if con:
		con.close()
