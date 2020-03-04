#!/usr/bin/env python3
import sqlite3

# Connect to a sqlite3 database
connection = sqlite3.connect("schedule_sync.db")
cursor = connection.cursor()
# Get rid of tables, if any exist
cursor.execute("DROP TABLE IF EXISTS Users;")
# Create new table for Users
cursor.execute("CREATE TABLE Users (username text, password text, " + 
               "security_question text, sq_answer text);")
# Commit changes and close connection
connection.commit()
connection.close()
