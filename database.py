import sqlite3

# Database Switch
database = "sqlite"


# Sqlite3 Settings
sqlite3_file = "testing.db"




if database == "sqlite":
	connection = sqlite3.connect(sqlite3_file)
	cursor = connection.cursor()
