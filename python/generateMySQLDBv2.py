#!/usr/bin/python
#To extract all github event from the JSON dumps and save it to the DB
from json import JSONDecoder
import sys,os
import MySQLdb as mdb
import gzip
import datetime
import time
import re


FLAGS = re.VERBOSE | re.MULTILINE | re.DOTALL
WHITESPACE = re.compile(r'[ \t\n\r]*', FLAGS)

#Get float time 
def getFloatTime(rawTime):
	try:
		timeStamp = datetime.datetime.strptime(rawTime[:rawTime.rfind('-')],'%Y-%m-%dT%H:%M:%S')
		t1 = timeStamp.timetuple()
		return time.mktime(t1)
	except Exception as e:
		try:
			timeStamp = datetime.datetime.strptime(rawTime[:rawTime.rfind(' ')],'%Y/%m/%d %H:%M:%S')
			t1 = timeStamp.timetuple()
			return time.mktime(t1)
		except:
			timeStamp = datetime.datetime.strptime(rawTime,'%Y-%m-%dT%H:%M:%SZ')
			t1 = timeStamp.timetuple()
			return time.mktime(t1)
def decode(s):
	
	try:
		_w=WHITESPACE.match
		decoder = JSONDecoder()
		s_len = len(s)
		end = 0
		while end != s_len:
			obj, end = decoder.raw_decode(s, idx=_w(s, end).end())
			end = _w(s, end).end()
			if obj['type'] =='PushEvent' or obj['type'] =='WatchEvent' or obj['type'] =='FollowEvent':  
				print obj['type']
				etlMySQL(obj)
	except Exception as e:
		print 'Error in line:'+str(sys.exc_traceback.tb_lineno)
		print e
		pass	        
	

def loads_invalid_obj_list(s):
	try:
		decoder = JSONDecoder()
		s_len = len(s)
		end = 0
		while end != s_len:
			obj, end = decoder.raw_decode(s, idx=end)
			if obj['type'] =='PushEvent' or obj['type'] =='WatchEvent' or obj['type'] =='FollowEvent':  
					etlMySQL(obj)
			
		
	except Exception as e:
		print 'Error in line:'+str(sys.exc_traceback.tb_lineno)
		print e	
		pass

def etlMySQL(obj):
	try:
		db = mdb.connect(host="localhost",user="root",passwd="root",db="github")
		cursor = db.cursor()

		user = obj['actor']
		if type(user) == dict:
			user = user['login']
		timeStamp = obj['created_at']
		eventType = obj['type']
		repo_id = 0
		owner = ""
		repo_url=""
		repo_name = ""
		repo_language = ""
		watchers = 0
		stargazers = 0
		forks = 0

		try:
			repo_id = obj['repository']['id']
		except Exception as e:
			#repo_id = obj['repo']['id']
			print 'Error in line:'+str(sys.exc_traceback.tb_lineno)
			print e
			pass

		try:
			owner = obj['repository']['owner']
		except Exception as e:
			#owner = obj['repo']['owner']
			print 'Error in line:'+str(sys.exc_traceback.tb_lineno)
			print e
			pass

		try:
			repo_url = obj['repository']['url']
		except Exception as e:
			repo_url = obj['repo']['url']
			print 'Error in line:'+str(sys.exc_traceback.tb_lineno)
			print e
			pass

		try:
			repo_name = obj['repository']['name']
		except Exception as e:
			#repo_name = obj['repo']['name']
			print 'Error in line:'+str(sys.exc_traceback.tb_lineno)
			print e
			pass

		try:
			repo_language = obj['repository']['language']

		except Exception as e:
			#repo_language = obj['repo']['language']
			print 'Error in line:'+str(sys.exc_traceback.tb_lineno)
			print e
			pass
		
		try:
			watchers = obj['repository']['watchers']
		except Exception as e:
			#watchers = obj['repo']['watchers']
			print 'Error in line:'+str(sys.exc_traceback.tb_lineno)
			print e
			pass

		try:
			stargazers = obj['repository']['stargazers']
		except Exception as e:
			#stargazers = obj['repo']['stargazers']
			print 'Error in line:'+str(sys.exc_traceback.tb_lineno)
			print e
			pass

		try:
			forks = obj['repository']['forks']
		except Exception as e:
			#forks = obj['repo']['forks']
			print 'Error in line:'+str(sys.exc_traceback.tb_lineno)
			print e
			pass

		sql = "INSERT INTO AllEventsv2 VALUES ('"+user+"','"+timeStamp+"','"+str(eventType)+"','"+mdb.escape_string(repo_url)+"','"+str(repo_name)+"','"+str(owner)+"','"+str(repo_language)+"',"+str(watchers)+","+str(forks)+","+str(stargazers)+","+str(getFloatTime(timeStamp))+")"
		print sql
		cursor.execute(sql)
		db.commit()		
	except Exception as e:
		print 'Error in line:'+str(sys.exc_traceback.tb_lineno)
		print e
		pass
path = "/home/kira/GitHubTrends/2012data/"+(sys.argv[1])		
os.chdir(path)	
for zippedFile in os.listdir("."):
	print zippedFile
	try:
		f = gzip.open(zippedFile, 'rb')
		file_content = f.read()
		#print file_content
		decode(file_content)
	except Exception as e:
		print 'Error in line:'+str(sys.exc_traceback.tb_lineno)
		print e
		pass
	finally:
		f.close()	

