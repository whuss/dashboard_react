#! /usr/bin/env python
# Get size of Database and store it together with the current time in table DbSizePackage
# This is used to create a plot of database growth in the web dashboard
# This script should be run periodically using a cron job.

# It is done this way because the MySQL event_scheduler is turned off in our database configuration

from app import db, DbSizePackage

# Get current size of database
sql = """SELECT CURDATE(), table_schema, ROUND(SUM(data_length) / 1024 / 1024, 1) as data_size,
         ROUND(SUM(index_length) / 1024 / 1024, 1) as index_size
         FROM information_schema.tables
         WHERE table_schema = 'bbf_inf_rep'
"""

query = db.session.execute(sql)
data = query.first()

date = data[0]
database_name = data[1]
data_size = float(data[2])
index_size = float(data[3])

# Get free size of database
sql = """SELECT SUM(data_free)
         FROM information_schema.partitions
         WHERE table_schema = 'bbf_inf_rep'
"""

query = db.session.execute(sql)
data = query.first()
free_size = float(data[0])

print(f"Database data_size: {data_size:.2f}mb, index_size: {index_size:.2f}mb, free_size: {free_size:.2f}mb, date={date}")

# Add current database size to Table DbSizePackage
db_size_package = DbSizePackage(date=date, data_size_in_mb=data_size, index_size_in_mb=index_size)
db.session.add(db_size_package)
db.session.commit()
