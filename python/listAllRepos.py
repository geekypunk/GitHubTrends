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
	if obj['repository'] is not None:
		etlMySQLRepos(obj['repository'])


def etlMySQLRepos(obj):
	db = mdb.connect(host="localhost",user="root",passwd="root",db="github")
	cursor = db.cursor()
	url = obj['url']
	owner = obj['owner']
	createdAt = obj['created_at']
	forks = obj['forks']
	watchers = obj['watchers']
	stargazers = obj['stargazers']
	pushedAt = obj['pushedAt']
	sql = "INSERT INTO FollowEvents VALUES ('"+user+"','"+timeStamp+"','"+followed_user_login+"',"+str(followed_user_followers)+","+str(followed_user_id)+",'"+mdb.escape_string(followed_user_url)+"',"+str(followed_user_repos)+")"
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
