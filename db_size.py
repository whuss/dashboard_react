#! /usr/bin/env python
# Get size of Database and store it together with the current time in table DbSizePackage
# This is used to create a plot of database growth in the web dashboard
# This script should be run periodically using a cron job.

# It is done this way because the MySQL event_scheduler is turned off in our database configuration

from app import db, DbSizePackage

# Get current size of data base
sql = """SELECT CURDATE(), table_schema, ROUND(SUM(data_length + index_length) / 1024 / 1024, 1) as size
         FROM information_schema.tables
         WHERE table_schema = 'bbf_inf_rep'
"""

query = db.session.execute(sql)
data = query.first()

date = data[0]
size = float(data[2])

print(f"Database size: {size:.2f}mb, date={date}")

# Add current database size to Table DbSizePackage
db_size_package = DbSizePackage(date=date, size_in_mb=size)
db.session.add(db_size_package)
db.session.commit()
