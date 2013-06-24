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

con = mdb.connect('localhost', 'root', 'root', 'github')
try:
	cur = con.cursor()	
	sql = 'SELECT DISTINCT actor FROM growthDelta'
	cur.execute(sql)
	users = cur.fetchall()
	impactVector=[]
	for user in users:
		sql = 'SELECT repo_url, initialCount,finalCount FROM growthDelta WHERE actor='+'"'+user[0]+'"'
		cur.execute(sql)
		impactRows = cur.fetchall()
		#Calculate standard deviation in impact
		impact =[]
		for row in impactRows:
			impact.append(row[2]-row[1])
		weightVector = np.array(impact)
		std = np.std(weightVector)
		class Object(object):
			pass
		a = Object()
		a.std = std
		a.actor = user

		print "----------------"
		print a.std
		print a.actor
		impactVector.append(a)
except Exception as e:
	
	print e
	print sys.exc_traceback.tb_lineno 
	pass
	
finally:

	if con:
		con.close()	
