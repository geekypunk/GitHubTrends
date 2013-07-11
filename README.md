Problem Overview and solution
===================================

Problem Statement
----------------------
Find the relationships between the watchers/committers with the popularity of a repo. How does the push/watch event of a highly popular user affect the growth curve of a GitHub repository?
Dataset
The dataset is in the form of JSON dumps of GitHub activity of various repositories and users.  Please find the sample files here

Solution
------------
The solution attempts to find the correlations between user events on a repository and its effects on the growth curve. The approach is fairly straightforward.

Algorithm
--------------
•    First select the topmost users aka high profile users (defined having highest number of followers). This is information is obtained from FollowEvents SQL dump, created using all the FollowEvents in the JSON dump.

•	Then get all the WatchEvents of each of these high profile users

o	For every WatchEvent by a user on a repository, get all the events on that repo till 24 hours after the WatchEvent. 

o	Draw a growth curve for this repository based on the above 1 day events. The x-axis contains the timestamps represented as float values and y-axis has the number of watchers of the repo at the respective timestamps

o	We first determine the plot’s eligibility to be drawn. We draw a plot if the growth curve shows substantial deviation from its predicted curve. The predicted curve is drawn since the timestamp of the WatchEvent. The data prior to this event is used for prediction. Least squares polynomial fitting is used to draw the curve. 

o	Then we determine the genuineness of a user’s impact (explained later) on that repo. If a user’s WatchEvent has actually caused the change in the growth curve, the plot of that repo is generated and stored in an image file

•	Using the above generated growth curve, we also try to observe as how group dynamics work in social coding. Do some users act as flock when one of them starts watching a repo? See User dynamics section for more info
Implementation

The python implementation for the above algorithm can be found here. 

Genuineness of a user’s impact
-------------------------------
Since the change in the growth curve of a repository need not be influenced by a WatchEvent of a particular user, we try to estimate as how genuine his WatchEvent is. The algorithm used for this is as follows

o	Get all the changes in watch counts of all the repos he has started watching. The initial and final watch counts differ by a timestamp of 1 day.

o	Calculate the standard deviation of all these differences.

o	If the standard is low “enough”, we deem the impact to be genuine, i.e the growth change has happened due to the user watching the repo

User Dynamics
--------------

This section explains the methodology used to observe user behavior in the social coding context. Do user operate in flock, when one of them starts following a repo? Which users most “connected”, i.e. the users most probable to start watching a repo, when one of them does?

Algorithm

o	Using the growth curve generated from the above algorithm, we can create lists of chronological user sequences. Each sequence contains a list of usernames, which represents the all the users,in-order,who have started watching the repo after the first user in the list has.

o	For example for a repo, if the first WatchEvent was by a high profile user called A, and the subsequent watch events on the repo till 1 day after that were by B C D and E. The list would look like [A,B,C,D,E]  

o	So essentially we will have a list of such sequences.

o	Now, to determine the user groups which are most “close”, we simply need to determine the subsequences which are most common among all the sequences in the list. We say sub-sequence and not sequence as the users need not appear in the exact same order in every sequence encountered, but just should be chronologically same.  For example if A appears before C in a sequence, and same is in another sequence, it is safe to assume A’s influence on C. This assumption is only valid upto a certain distance between the two users. As the longer is the gap between two users in a sequence, lower is their “connectivity”, i.e lower is A’s influence on C.(Currently working on accommodating this logic)

o	This high co-incidence user groups is obtained by maintaining a map of all possible permutations, of all the sequences encountered so far as we iterate the list of sequences. Whenever we see an already seen permutation, we increment its occurrence count.

Sub-Algorithm

Input :  List on chronological user sequences S
		Output : Count map, M, representing the occurrence count of all sub-sequences

		For all sequences Q in S:
			For every possible permutation P of sequence Q in map M:
				Check if P already present in M:
					If True:
						M[P]++   //Increase the occurrence count
Implementation
The python implementation for the above algorithm can be found here.  The script takes two command-line arguments, first one is the size of user sets and second is how many such top sets.
For example,
If we need the top 5 users sets each of size 3 who show high connectivity, issue the command
		python getFlockUsers.py 3 5
Code setup
------------
•	Put appropriate database credentials in def getDBConnection() function of  highProfileWatchEvents.py
•	Import the sql files from here
•	Run highProfileWatchEvents.py  to generate plots


Observations
--------------

•   By looking at the plot images, most of the plots show an increased growth rate after a high profile user starts watching. The rate slowly saturates with time

•	If a user has particularly high number of followers, the growth rate increases substantially

•	If a user has lower than average number of followers(average calculated from the data), the chance of the growth rate being continually increasing is less, showing that the growth rate is mostly independent of his impact

•	The growth rates of very popular repos seem not to differ much, even when a high profile user starts watching
•	Most of the "social" effect is seen within 1 day of the event, similar behavior is also observed during news proliferation in social networking sites like Facebook. Here the workflow is usually like...User watches a repo->His followers get notified; follow the repo->Their followers. So on.

•	User do seem to behave in groups, a distinct set of users show high co-incidence, i.e if a user’s starts watching another set users are most probable to follow that repository. The below are set of two users, with their incidence count

o	(('torifat', 'mkol5222'), 642)
o	(('fnu', 'torifat'), 452)
o	(('jasolko', 'fnu'), 342)
o	(('hansstimer', 'payco'), 152)
o	(('rgigger', 'roundhead',32)

The below are set of three users, with their incidence count

o	(('anggriawan', 'rgigger', 'jasolko'), 314)
o	(('fnu', 'jasolko', 'torifat'), 134)
o	(('payco', 'roundhead', 'rgigger'), 78)
o	(('fnu', 'hansstimer', 'torifat'), 34)
o	(('rgigger', 'anggriawan', 'payco'), 29)

