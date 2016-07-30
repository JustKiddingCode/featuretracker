#!/usr/bin/env python3

import sqlite3

import config

# Database Switch
database = "sqlite"


# Sqlite3 Settings
sqlite3_file = config.BASE_DIR + "testing.db"




if database == "sqlite":
	connection = sqlite3.connect(sqlite3_file)
	cursor = connection.cursor()
