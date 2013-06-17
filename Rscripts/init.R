# Call this once, when fresh prompt library(RMySQL)
library(RMySQL)
con = dbConnect(MySQL(), user="root", password="root",dbname="github", host="localhost")
dbListTables(con)







