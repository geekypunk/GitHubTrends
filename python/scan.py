#!/usr/bin/python
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
	if obj['type'] == "WatchEvent":
		etlMySQLWatch(obj)

def etlMySQLWatch(obj):
	db = mdb.connect(host="localhost",user="root",passwd="root",db="github")
	cursor = db.cursor()
	user = obj['actor']
	user_type = obj['actor_attributes']['type']	
	timeStamp = obj['created_at']
	repo_id = 0
	try:
		repo_id = obj['repository']['id']
	except Exception as e:
		pass
	repo_url = obj['repository']['url']
	watchers = obj['repository']['watchers']
	stargazers = obj['repository']['stargazers']	
	forks = obj['repository']['forks']
	print user+'|'+user_type+'|'+timeStamp+'|'+repo_url+'|'+str(watchers)+'|'+str(stargazers)+'|'+str(forks)	
	sql = "INSERT INTO WatchEvents VALUES ('"+user+"','"+user_type+"','"+timeStamp+"',"+str(repo_id)+",'"+mdb.escape_string(repo_url)+"',"+str(watchers)+","+str(stargazers)+","+str(forks)+")"
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

