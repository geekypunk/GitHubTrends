#!/usr/bin/python
#To extract all github event from the JSON dumps and save it to the DB
from json import JSONDecoder
import os
import MySQLdb as mdb

os.chdir("/home/kira/GitHubTrends/githubdata")

def loads_invalid_obj_list(s):
    decoder = JSONDecoder()
    s_len = len(s)
    objs = []
    end = 0
    while end != s_len:
        obj, end = decoder.raw_decode(s, idx=end)
        objs.append(obj)
	#if obj['repository'] is not None:
	etlMySQLWatch(obj)

def etlMySQLWatch(obj):
	db = mdb.connect(host="localhost",user="root",passwd="root",db="github")
	cursor = db.cursor()
	user = obj['actor']
	timeStamp = obj['created_at']
	eventType = obj['type']
	repo_id = 0
	owner = ""
	repo_url=""
	watchers = 0
	stargazers = 0
	forks = 0
	try:
		repo_id = obj['repository']['id']
	except Exception as e:
		pass
	try:
		owner = obj['repository']['owner']
	except Exception as e:
		pass

	try:
		repo_url = obj['repository']['url']
	except Exception as e:
		pass
	try:
		watchers = obj['repository']['watchers']
	except Exception as e:
		pass
	try:
		stargazers = obj['repository']['stargazers']
	except Exception as e:
		pass
	try:
		forks = obj['repository']['forks']
	except Exception as e:
		pass
	
	print user+'|'+timeStamp+'|'+repo_url+'|'+str(watchers)+'|'+str(stargazers)+'|'+str(forks)	
	sql = "INSERT INTO AllEvents VALUES ('"+user+"','"+timeStamp+"','"+eventType+"',"+str(repo_id)+",'"+mdb.escape_string(repo_url)+"','"+owner+"',"+str(watchers)+","+str(stargazers)+","+str(forks)+")"
	print sql
	cursor.execute(sql)
	db.commit()		
	
	
	
		
for files in os.listdir("."):
        #print files
	try:
		f = open(files,'r')
		loads_invalid_obj_list(f.read())
		#etlMySQL(objs)
	except Exception as e:
		print e
		#pass

