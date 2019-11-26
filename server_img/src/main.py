import pymysql
import time

# wait until sql database fully loaded
time.sleep(15)

# Open database connection
db = pymysql.connect(host = 'mysql-dev', user = 'root', password = 'password', db = 'flights')

# prepare a cursor object using cursor() method
cursor = db.cursor()

# execute SQL query using execute() method.
cursor.execute("SELECT VERSION()")

# Fetch a single row using fetchone() method.
data = cursor.fetchone()
print ("Database version : %s " % data)

cursor.execute("select * from flights_table")
rows = cursor.fetchall()
for row in rows:
    print(row[0],row[1],row[2])

# disconnect from server
db.close()