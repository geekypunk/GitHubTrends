mostFreqEvents = dbGetQuery(con,statement='SELECT eventType,count(eventType) FROM AllEvents GROUP BY eventType ORDER BY count(eventType) DESC LIMIT 10')

repoCount = dbGetQuery(con,statement='SELECT DISTINCT count(*) repo_url from AllEvents')

mostWatchedRepos = dbGetQuery(con,statement='SELECT repo_url,repo_watchers,repo_forks,repo_stargazers from AllEvents GROUP BY repo_url ORDER BY repo_watchers DESC LIMIT 10')

fastGrowingRepos = dbGetQuery(con,statement='SELECT repo_url,MIN(repo_watchers) as A,MAX(repo_watchers) as B from AllEvents GROUP BY repo_url ORDER BY (MAX(repo_watchers)-MIN(repo_watchers)) DESC LIMIT 10')

mostActiveRepos = dbGetQuery(con,statement='SELECT repo_url,eventType as event,count(eventType) as count from AllEvents GROUP BY repo_url ORDER BY count(eventType) DESC LIMIT 11')

watchEventByTopGuy = dbGetQuery(con,statement='SELECT repo_url,timeStamp,repo_watchers from AllEvents WHERE ')
