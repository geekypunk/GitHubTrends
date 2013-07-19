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

def getDBConnection():
	user = "root"
	password = "root"
	databaseName = "github"
	conn = mdb.connect('localhost', user, password, databaseName)
	return conn
	
def executeSQL(con,sql):
	cursor = con.cursor()
	cursor.execute(sql)	
	return cursor.fetchall()

try:

	conn = getDBConnection()
	sql = 'SELECT DISTINCT repo_url from AllEventsv2'
	allRepos = executeSQL(conn,sql)
	for repo in allRepos:
		sql = "SELECT actor,watchersNow,timeStampInFloat from AllEventsv2 WHERE repo_url='"+repo+"'"
		events = executeSQL(conn,sql)
		i=0
		for event in events:
			if i == 0:
				startTime = event[0]
				i = i + 1
			if startTime+24*3600 > event[1]:
				endTime = event[1]
		print sql
		sql = "INSERT INTO growthDeltav2 VALUES("+"'"+repo+"',"+"'"+actor+"',"+str(startTime)+","+str(endTime)+")"
		cursor = conn.cursor()
		cursor.execute(sql)
		db.commit()			

	pass
except Exception, e:
	raise e
finally:
	pass