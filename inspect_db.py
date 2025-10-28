
import sqlite3

conn = sqlite3.connect("nutrition.db")
cursor = conn.cursor()

# List tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
print("Tables in the database:")
print(cursor.fetchall())

# Query foods table
cursor.execute("SELECT * FROM foods;")
print("\nContents of the foods table:")
print(cursor.fetchall())

conn.close()
