import sqlite3

#base dir
base_dir = "/opt/featuretracker"

# Database Switch
database = "sqlite"


# Sqlite3 Settings
sqlite3_file = base_dir + "/testing.db"




if database == "sqlite":
	connection = sqlite3.connect(sqlite3_file)
	cursor = connection.cursor()
