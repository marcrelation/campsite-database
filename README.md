# campsite-database
Open source database of campground sites. (Currently only FL State Parks)
- As an added bonus availability_finder.py has been added which for FL State Parks will find all site availability for the next 11 months based on a query using the campground database.

***Description:***
- Python based scripts to generate a sqlite3 database that contains park and site information.  Currently the database is not committed and will require you to generate it from the scripts for usage.

***Reason:***
- Most campground websites require a significant amount of navigation just to determine if they have sites that are full hookup and which ones they might be.  This database lets you query for the amenities you care about.  

***Contributing:***
- Additional scrapers and contributions are welcome.

***Requirements:***
- Python3
- Bash

***Usage:***
- ./create_database.sh
