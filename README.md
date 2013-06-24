GitHubTrends
============
Problem Statement
-----------------

Find the relationships between the watchers/committers with the popularity of a repo. The number of watchers and forks decide the popularity of a project for any language. It is ok to go with defaults about the number of watchers, but gradually we would like to think about top x% of repos on a language.

###Input Data

The data is provided as activity streams. Each activity can be one of the 6 different types,

1     PushEvent     

2    WatchEvent     

3    ForkEvent     

4    CreateEvent     

5    IssueCommentEvent     

6    FollowEvent

From our perspective we find the Push, Watch and Fork events indicative of the popularity of an repo. FollowEvent gives us information about people following a individual rather than a repo. This event could be used to estimate the popularity of a person, we would like to find out if there is any correlation between the popularity of a person with the popularity of a repo that he watches/owns/commits to.


Attempted Solution
--------------------

The summary of this solution is to create a predicted growth curve and compare this with the actual data at hand.

######*Growth Curve Definition*

X-axis : scaled timestamps represented as a float value(seconds since epoch)

Y-axis : No of watchers

impactRegion : point from which a “high-profile” user has starting watching the repo. Higher the number of followers a user has, higher is his credibility

The text below x-axis is of the format

impactUserName --> repo he impacted | change in number of watchers in 1 hour

The growthcurves images comparing the actual and predicted growth are in *growthCurvesBackup[https://github.com/geekypunk/GitHubTrends/tree/master/python/currentGeneratedCurves] folder*
